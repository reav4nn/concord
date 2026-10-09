"""Generate synthetic air-cargo shipments: 4 PDFs per shipment + ground truth.

Each shipment gets 0-2 injected errors (see concord/schema.py ERROR_TYPES). Consignee names are
ALWAYS written three ways (Azerbaijani Latin / English / Russian Cyrillic): that is realistic and
is NOT an error, so a naive string-compare baseline produces false alarms while Concord should not.

IMPORTANT for honest evaluation: the person who builds/tunes the pipeline should not look at
truth.json. Run with a seed you did not tune on (e.g. --seed 2026) for the final numbers.

Usage: python data/generate.py --n 30 --seed 7 --out data/shipments
"""
import argparse, copy, json, random
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

HERE = Path(__file__).parent
pdfmetrics.registerFont(TTFont("DV", str(HERE / "fonts" / "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DVB", str(HERE / "fonts" / "DejaVuSans-Bold.ttf")))

CONSIGNEES = [
    ("Kür Elektronika MMC", "KUR ELEKTRONIKA LLC", "ООО «Кюр Электроника»"),
    ("Xəzər Texnika MMC", "KHAZAR TEKHNIKA LLC", "ООО «Хазар Техника»"),
    ("Bakı Ticarət Evi MMC", "BAKU TRADE HOUSE LLC", "ООО «Бакинский Торговый Дом»"),
    ("Qafqaz Kargo MMC", "GAFGAZ CARGO LLC", "ООО «Гафгаз Карго»"),
    ("Sahil Sənaye MMC", "SAHIL SANAYE LLC", "ООО «Сахиль Санайе»"),
]
SHIPPERS = ["Xinjiang Tianlu Trading Co., Ltd.", "Shenzhen Hongda Electronics Co., Ltd.",
            "Yiwu Lianfa Import & Export Co., Ltd.", "Guangzhou Meiya Industrial Co., Ltd."]
ITEMS = [("Wireless earphones", "851830", (6, 14)), ("Smartphone cases", "392690", (0.8, 2.5)),
         ("USB-C cables", "854442", (0.6, 1.8)), ("Power banks 10000mAh", "850760", (7, 12)),
         ("LED desk lamps", "940520", (5, 11)), ("Bluetooth speakers", "851822", (9, 19)),
         ("Laptop bags", "420212", (4, 9))]
ROUTES = [("Ürümçi (URC)", "Bakı (GYD)"), ("Şençjen (SZX)", "Bakı (GYD)"), ("Quançjou (CAN)", "Bakı (GYD)")]


def make_shipment(rng, idx):
    cons = rng.randrange(len(CONSIGNEES))
    tax = str(rng.randint(1000000000, 1999999999))
    items = []
    for desc, hs, (lo, hi) in rng.sample(ITEMS, rng.randint(3, 6)):
        qty = rng.choice([200, 300, 400, 500, 600, 800, 1000, 1200])
        price = round(rng.uniform(lo, hi), 2)
        items.append({"description": desc, "hs_code": hs, "qty": qty, "unit_price": price,
                      "amount": round(qty * price, 2)})
    total = round(sum(i["amount"] for i in items), 2)
    packages = rng.randint(12, 60)
    gross = round(packages * rng.uniform(18, 32), 1)
    base = dict(shipper_name=rng.choice(SHIPPERS), consignee_tax_id=tax,
                invoice_no=f"TL-2026-{rng.randint(1000, 9999)}", awb_no=f"771-{rng.randint(1000,9999)} {rng.randint(1000,9999)}",
                currency="USD", gross_weight_kg=gross, net_weight_kg=round(gross * 0.86, 1),
                packages=packages, origin_country="China", route=rng.choice(ROUTES))
    az, en, ru = CONSIGNEES[cons]
    docs = {
        "invoice": dict(base, doc_type="invoice", consignee_name=az, items=items, total_amount=total),
        "packing_list": dict(base, doc_type="packing_list", consignee_name=ru,
                             items=[{k: i[k] for k in ("description", "qty")} for i in items], total_amount=None),
        "certificate_of_origin": dict(base, doc_type="certificate_of_origin", consignee_name=az,
                                      items=[{k: i[k] for k in ("description", "hs_code", "qty")} for i in items],
                                      total_amount=None, gross_weight_kg=None, net_weight_kg=None),
        "awb": dict(base, doc_type="awb", consignee_name=en, items=[], total_amount=None, net_weight_kg=None,
                    consignee_tax_id=None),
    }
    return docs, cons


def inject(rng, docs, etype, cons):
    d = docs
    if etype == "weight_mismatch":
        d["invoice"]["gross_weight_kg"] = round(d["invoice"]["gross_weight_kg"] + rng.choice([-1, 1]) * rng.uniform(25, 60), 1)
        return "invoice"
    if etype == "total_mismatch":
        d["invoice"]["total_amount"] = round(d["invoice"]["total_amount"] + rng.choice([5, 10, -5, 50, 0.5]), 2)
        return "invoice"
    if etype == "tax_id_mismatch":
        target = rng.choice(["packing_list", "certificate_of_origin"])
        t = list(d[target]["consignee_tax_id"]); i = rng.randrange(2, 8)
        while t[i] == t[i + 1]:
            i = rng.randrange(2, 8)
        t[i], t[i + 1] = t[i + 1], t[i]
        d[target]["consignee_tax_id"] = "".join(t)
        return target
    if etype == "consignee_mismatch":
        other = rng.choice([c for j, c in enumerate(CONSIGNEES) if j != cons])
        target = rng.choice(["awb", "packing_list"])
        d[target]["consignee_name"] = other[1] if target == "awb" else other[2]
        return target
    if etype == "hs_mismatch":
        it = rng.choice(d["certificate_of_origin"]["items"])
        it["hs_code"] = rng.choice([h for _, h, _ in ITEMS if h != it["hs_code"]])
        return "certificate_of_origin"
    if etype == "package_mismatch":
        d["awb"]["packages"] += rng.choice([-2, -1, 1, 3])
        return "awb"


def fmt_hs(h):
    return f"{h[:4]}.{h[4:]}"


def render(doc, path):
    c = canvas.Canvas(str(path), pagesize=A4); W, H = A4; y = H - 60
    def line(txt, size=10, bold=False, dy=16, x=50):
        nonlocal y
        c.setFont("DVB" if bold else "DV", size); c.drawString(x, y, txt); y -= dy
    t = doc["doc_type"]
    title = {"invoice": "COMMERCIAL INVOICE", "packing_list": "PACKING LIST / УПАКОВОЧНЫЙ ЛИСТ",
             "certificate_of_origin": "CERTIFICATE OF ORIGIN", "awb": "AIR WAYBILL"}[t]
    line(title, 16, True, 28)
    line(f"Shipper: {doc['shipper_name']}")
    line(f"Consignee: {doc['consignee_name']}")
    if doc.get("consignee_tax_id"):
        line(f"Consignee tax ID (VÖEN): {doc['consignee_tax_id']}")
    if t in ("invoice", "packing_list"):
        line(f"Invoice No: {doc['invoice_no']}")
    line(f"AWB No: {doc['awb_no']}")
    line(f"Route: {doc['route'][0]} - {doc['route'][1]}")
    if t == "certificate_of_origin":
        line(f"Country of origin: {doc['origin_country']}")
    y -= 8
    if t == "invoice":
        line("Description                         HS code     Qty     Unit price    Amount (USD)", 9, True)
        for it in doc["items"]:
            line(f"{it['description']:<34}  {fmt_hs(it['hs_code']):<10}  {it['qty']:>5}   {it['unit_price']:>9.2f}   {it['amount']:>12.2f}", 9)
        y -= 6; line(f"TOTAL: {doc['total_amount']:.2f} {doc['currency']}", 11, True)
        line(f"Gross weight: {doc['gross_weight_kg']} kg    Net weight: {doc['net_weight_kg']} kg    Packages: {doc['packages']}")
    elif t == "packing_list":
        line("Description / Наименование               Qty / Кол-во", 9, True)
        for it in doc["items"]:
            line(f"{it['description']:<40} {it['qty']:>6}", 9)
        y -= 6
        line(f"Брутто / G.W.: {doc['gross_weight_kg']} kg   Нетто / N.W.: {doc['net_weight_kg']} kg   Мест / Ctns: {doc['packages']}")
    elif t == "certificate_of_origin":
        line("Description of goods                 HS code      Quantity", 9, True)
        for it in doc["items"]:
            line(f"{it['description']:<36} {fmt_hs(it['hs_code']):<11} {it['qty']:>6}", 9)
        y -= 6; line(f"Number of packages: {doc['packages']}")
    else:
        line(f"No. of pieces: {doc['packages']}      Gross weight: {doc['gross_weight_kg']} kg")
        line("Nature of goods: consumer electronics and accessories")
    c.showPage(); c.save()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=30); ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--out", default=str(HERE / "shipments"))
    a = ap.parse_args(); rng = random.Random(a.seed); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    from concord_schema import ERROR_TYPES  # noqa (local import shim below)
    for k in range(1, a.n + 1):
        docs, cons = make_shipment(rng, k)
        n_err = 0 if k % 5 == 0 else rng.choice([1, 1, 2])
        labels = []
        for et in rng.sample(ERROR_TYPES, n_err):
            labels.append({"type": et, "doc": inject(rng, docs, et, cons)})
        d = out / f"ship_{k:02d}"; d.mkdir(exist_ok=True)
        for t, doc in docs.items():
            render(doc, d / f"{t}.pdf")
        (d / "truth.json").write_text(json.dumps({"labels": labels, "docs": docs}, ensure_ascii=False, indent=1))
    print(f"{a.n} shipments -> {out}")


if __name__ == "__main__":
    import sys; sys.path.insert(0, str(HERE.parent))
    import concord.schema as s; sys.modules["concord_schema"] = s
    main()
