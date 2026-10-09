"""Step 2: cross-check extracted documents.

Rule checks (code) handle numbers and exact IDs. Semantic checks (Claude) handle what rules
cannot: is "Kür Elektronika MMC" the same company as "ООО «Кюр Электроника»"? Each finding
records who decided it (`checker`), which the UI shows to the user and the judges.
"""
import json, os
from .schema import DOC_LABELS

WEIGHT_TOL = 0.005   # 0.5 %
MONEY_TOL = 0.01     # 1 cent


def _f(sev, etype, field, title, summary, rows, checker, fix, params=None):
    # az texts are kept for logs/back-compat; the UI renders type+params via concord.i18n
    return dict(severity=sev, type=etype, field=field, title=title, summary=summary,
                rows=rows, checker=checker, fix=fix, params=params or {})


def _row(doc, value, bad=False):
    return {"doc": DOC_LABELS.get(doc["doc_type"], doc["doc_type"]), "doc_key": doc["doc_type"], "value": value,
            "where": doc.get("_source_file", ""), "bad": bad}


def _majority_mismatch(docs, key, fmt, eq):
    vals = [(d, d.get(key)) for d in docs if d.get(key) is not None]
    if len(vals) < 2:
        return None
    groups = []
    for d, v in vals:
        for g in groups:
            if eq(g[0][1], v):
                g.append((d, v)); break
        else:
            groups.append([(d, v)])
    if len(groups) == 1:
        return None
    groups.sort(key=len, reverse=True)
    majority = groups[0]
    rows = [_row(d, fmt(v), bad=(d, v) not in majority) for d, v in vals]
    return majority[0][1], rows


def rule_checks(docs: list[dict]) -> tuple[list[dict], list[str]]:
    findings, passed = [], []

    r = _majority_mismatch(docs, "gross_weight_kg", lambda v: f"{v:,.1f} kq".replace(",", " "),
                           lambda a, b: abs(a - b) <= WEIGHT_TOL * max(a, b))
    if r:
        findings.append(_f("error", "weight_mismatch", "Brutto çəki", "Ümumi çəki uyğun gəlmir",
                           "Sənədlərdə brutto çəki fərqlidir (tolerans 0,5%).", r[1],
                           "Kod: rəqəm müqayisəsi", f"Bütün sənədlərdə çəkini {r[0]} kq etmək.",
                           {"value": r[0]}))
    else:
        passed.append("weight")

    r = _majority_mismatch(docs, "packages", str, lambda a, b: a == b)
    if r:
        findings.append(_f("error", "package_mismatch", "Yer sayı", "Yer sayı uyğun gəlmir",
                           "Sənədlərdə qutu/yer sayı fərqlidir.", r[1], "Kod: dəqiq uyğunluq",
                           f"Yer sayını {r[0]} kimi düzəltmək.", {"value": r[0]}))
    else:
        passed.append("packages")

    r = _majority_mismatch(docs, "consignee_tax_id", str,
                           lambda a, b: "".join(filter(str.isdigit, a)) == "".join(filter(str.isdigit, b)))
    if r:
        findings.append(_f("error", "tax_id_mismatch", "Alıcı VÖEN", "Alıcının VÖEN-i fərqlidir",
                           "VÖEN bütün sənədlərdə eyni olmalıdır.", r[1], "Kod: dəqiq uyğunluq",
                           f"Səhv sənədi {r[0]} VÖEN-i ilə yeniləmək.", {"value": r[0]}))
    else:
        passed.append("tax_id")

    for d in docs:
        if d["doc_type"] != "invoice" or d.get("total_amount") is None:
            continue
        amounts = [i.get("amount") for i in d.get("items", []) if i.get("amount") is not None]
        if not amounts:
            continue
        s = round(sum(amounts), 2)
        cur = d.get("currency") or ""
        if abs(s - d["total_amount"]) > MONEY_TOL:
            findings.append(_f("error", "total_mismatch", "Məbləğ", "Invoice-un cəmi sətirlərlə tutmur",
                               f"{len(amounts)} sətrin cəmi {s:.2f} {cur}, TOTAL isə {d['total_amount']:.2f} {cur}. "
                               f"Fərq {abs(s - d['total_amount']):.2f} {cur}.",
                               [{"doc": "Invoice, sətirlər", "doc_key": "invoice_lines", "value": f"{s:.2f} {cur}", "where": d.get("_source_file", ""), "bad": False},
                                {"doc": "Invoice, TOTAL", "doc_key": "invoice_total", "value": f"{d['total_amount']:.2f} {cur}", "where": d.get("_source_file", ""), "bad": True}],
                               "Kod: hesab yoxlaması", "TOTAL sətrini düzəltmək.",
                               {"n": len(amounts), "sum": f"{s:.2f}", "total": f"{d['total_amount']:.2f}",
                                "diff": f"{abs(s - d['total_amount']):.2f}", "cur": cur}))
        else:
            passed.append("total")

    inv = next((d for d in docs if d["doc_type"] == "invoice"), None)
    coo = next((d for d in docs if d["doc_type"] == "certificate_of_origin"), None)
    if inv and coo:
        inv_hs = {(i.get("hs_code") or "").replace(".", "")[:6] for i in inv.get("items", []) if i.get("hs_code")}
        coo_hs = {(i.get("hs_code") or "").replace(".", "")[:6] for i in coo.get("items", []) if i.get("hs_code")}
        diff = inv_hs ^ coo_hs
        if diff:
            findings.append(_f("error", "hs_mismatch", "HS kodu", "HS kodları sənədlər arasında fərqlidir",
                               "Invoice və mənşə sertifikatında fərqli HS kodları var.",
                               [_row(inv, ", ".join(sorted(inv_hs)), bad=bool(inv_hs - coo_hs)),
                                _row(coo, ", ".join(sorted(coo_hs)), bad=bool(coo_hs - inv_hs))],
                               "Kod: kod müqayisəsi", "Brokerlə düzgün kodu təsdiqləyib bir sənədi yeniləmək."))
        else:
            passed.append("hs")
    return findings, passed


SEMANTIC_PROMPT = """You check freight documents for a customs broker. Below are the consignee names
as printed on each document. Names may be written in Azerbaijani Latin, English, or Russian Cyrillic,
with legal-form variants (MMC = LLC = ООО). Decide whether they all refer to the SAME company.
Transliteration and legal-form differences are NOT errors. A different company name IS an error.

Return JSON: {"same_company": true|false, "confidence": 0-1, "reason_az": "<one short sentence in Azerbaijani>",
"reason_en": "<the same sentence in English>", "reason_ru": "<the same sentence in Russian>",
"odd_one_out": "<doc label or null>"}

Names:
"""


def semantic_checks(docs: list[dict], client=None) -> tuple[list[dict], list[str]]:
    names = [(d, d.get("consignee_name")) for d in docs if d.get("consignee_name")]
    if len(names) < 2:
        return [], []
    from .llm import ask_json
    listing = "\n".join(f"- {DOC_LABELS[d['doc_type']]}: {n}" for d, n in names)
    res = ask_json("You are a careful customs document checker. Answer only with JSON.",
                   SEMANTIC_PROMPT + listing, max_tokens=400)
    res.setdefault("reason", res.get("reason_az") or res.get("reason_en", ""))
    reason = {k: res.get(f"reason_{k}") or res["reason"] for k in ("az", "en", "ru")}
    rows = [_row(d, n, bad=(not res["same_company"] and DOC_LABELS[d["doc_type"]] == res.get("odd_one_out"))) for d, n in names]
    if not res["same_company"]:
        return [_f("error", "consignee_mismatch", "Alıcı adı", "Alıcı fərqli şirkət kimi görünür",
                   res["reason"], rows, "AI: ad və translit uyğunlaşdırması", "Düzgün alıcı adı ilə sənədi yeniləmək.",
                   {"reason": reason})], []
    if res.get("confidence", 1) < 0.7:
        return [_f("warn", "consignee_unsure", "Alıcı adı", "Alıcı adı yoxlanmalıdır", res["reason"], rows,
                   "AI: ad və translit uyğunlaşdırması", "Brokerin təsdiqi lazımdır.", {"reason": reason})], []
    distinct = len({n.strip().lower() for _, n in names})
    if distinct > 1:
        return [_f("ok", "consignee_variants", "Alıcı adı", f"Alıcı adı {distinct} cür yazılıb, eyni şirkətdir",
                   res["reason"], rows, "AI: ad və translit uyğunlaşdırması", "Düzəliş lazım deyil.",
                   {"reason": reason, "n": distinct})], []
    return [], ["consignee"]


def check(docs: list[dict], use_ai: bool = True) -> dict:
    findings, passed = rule_checks(docs)
    if use_ai:
        f2, p2 = semantic_checks(docs)
        findings += f2; passed += p2
    order = {"error": 0, "warn": 1, "ok": 2}
    findings.sort(key=lambda f: order[f["severity"]])
    return {"findings": findings, "passed": passed,
            "counts": {k: sum(f["severity"] == k for f in findings) for k in order}}
