"""Evaluate Concord against ground truth, and against a naive baseline.

Modes:
  --mode full     : real pipeline. Claude extracts every PDF, then rule + AI checks. (needs ANTHROPIC_API_KEY)
  --mode offline  : skips extraction (uses truth.json documents), rules only. Tests the checker logic, free.

Baseline ("how a tired human / simple script does it"): exact string equality on every shared field,
no tolerance, no transliteration awareness, no arithmetic check of the invoice total.

Output: eval/results.json and eval/results.md (paste the table into the deck and the submission form).
Usage: python eval/run_eval.py --mode full --data data/shipments
"""
import argparse, json, sys, time
from collections import defaultdict
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from concord.schema import ERROR_TYPES
from concord.compare import check


def baseline(docs):
    found = set()
    def vals(k): return [d.get(k) for d in docs if d.get(k) is not None]
    if len(set(vals("gross_weight_kg"))) > 1: found.add("weight_mismatch")
    if len(set(vals("packages"))) > 1: found.add("package_mismatch")
    if len(set(vals("consignee_tax_id"))) > 1: found.add("tax_id_mismatch")
    if len(set(vals("consignee_name"))) > 1: found.add("consignee_mismatch")
    inv = [d for d in docs if d["doc_type"] == "invoice"]
    coo = [d for d in docs if d["doc_type"] == "certificate_of_origin"]
    if inv and coo:
        a = {i.get("hs_code") for i in inv[0].get("items", [])}; b = {i.get("hs_code") for i in coo[0].get("items", [])}
        if a != b: found.add("hs_mismatch")
    return found


def score(pred_by_ship, truth_by_ship):
    per = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    for s, truth in truth_by_ship.items():
        pred = pred_by_ship[s]
        for t in ERROR_TYPES:
            if t in pred and t in truth: per[t]["tp"] += 1
            elif t in pred: per[t]["fp"] += 1
            elif t in truth: per[t]["fn"] += 1
    tot = {k: sum(v[k] for v in per.values()) for k in ("tp", "fp", "fn")}
    def pr(v):
        p = v["tp"] / (v["tp"] + v["fp"]) if v["tp"] + v["fp"] else 1.0
        r = v["tp"] / (v["tp"] + v["fn"]) if v["tp"] + v["fn"] else 1.0
        return round(p, 3), round(r, 3)
    return {t: {**per[t], "precision": pr(per[t])[0], "recall": pr(per[t])[1]} for t in ERROR_TYPES}, \
           {**tot, "precision": pr(tot)[0], "recall": pr(tot)[1]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["full", "offline"], default="offline")
    ap.add_argument("--data", default=str(Path(__file__).resolve().parents[1] / "data" / "shipments"))
    ap.add_argument("--limit", type=int, default=0, help="only the first N shipments")
    a = ap.parse_args()
    ap_workers = 6
    ships = sorted(p for p in Path(a.data).iterdir() if p.is_dir())[: a.limit or None]
    truth, ours, base, details, t0 = {}, {}, {}, {}, time.time()
    from concurrent.futures import ThreadPoolExecutor
    if a.mode == "full":
        from concord.extract import extract

    def run_one(sd):
        tj = json.loads((sd / "truth.json").read_text())
        if a.mode == "full":
            types = ("invoice", "packing_list", "certificate_of_origin", "awb")
            with ThreadPoolExecutor(4) as ex:
                docs = list(ex.map(lambda t: extract(next(sd.glob(f"{t}.*")), t), types))
        else:
            docs = [dict(d, _source_file=f"{t}.pdf") for t, d in tj["docs"].items()]
        res = check(docs, use_ai=(a.mode == "full"))
        return sd.name, {l["type"] for l in tj["labels"]}, res, docs

    with ThreadPoolExecutor(ap_workers if a.mode == "full" else 1) as ex:
        for name, tr, res, docs in ex.map(run_one, ships):
            truth[name] = tr
            ours[name] = {f["type"] for f in res["findings"] if f["severity"] == "error"}
            base[name] = baseline(docs)
            details[name] = {"truth": sorted(tr), "concord": sorted(ours[name]), "baseline": sorted(base[name]),
                             "missed": sorted(tr - ours[name]), "false_alarm": sorted(ours[name] - tr)}
            print(name, details[name], flush=True)
    per_c, tot_c = score(ours, truth); per_b, tot_b = score(base, truth)
    out = {"mode": a.mode, "shipments": len(ships), "seconds": round(time.time() - t0, 1),
           "concord": {"total": tot_c, "per_type": per_c}, "baseline": {"total": tot_b, "per_type": per_b},
           "per_shipment": details}
    here = Path(__file__).parent
    (here / "results.json").write_text(json.dumps(out, indent=1))
    rows = ["| Xəta növü | Concord P | Concord R | Baseline P | Baseline R |", "|---|---|---|---|---|"]
    for t in ERROR_TYPES:
        rows.append(f"| {t} | {per_c[t]['precision']} | {per_c[t]['recall']} | {per_b[t]['precision']} | {per_b[t]['recall']} |")
    rows.append(f"| **Cəmi** | **{tot_c['precision']}** | **{tot_c['recall']}** | {tot_b['precision']} | {tot_b['recall']} |")
    md = f"Mode: {a.mode}, {len(ships)} yük, {out['seconds']} san.\n\n" + "\n".join(rows) + "\n"
    (here / "results.md").write_text(md); print("\n" + md)


if __name__ == "__main__":
    main()
