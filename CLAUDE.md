# CLAUDE.md

Guidance for contributors and AI coding agents working in this repository. Read this file first, then `DESIGN.md` before touching the UI.

## What Concord is

Concord cross-checks the documents of a single freight shipment (commercial invoice, packing list, certificate of origin, air waybill) against each other, reports every discrepancy with the value and location from each document, and drafts a correction email to the shipper.

**Users.** Declarants at freight forwarders and customs brokers in Baku who handle Middle Corridor shipments. Today they compare the documents by eye, which takes 5 to 20 minutes per shipment. The most common errors are in consignee details and amounts.

**Name.** *Concord* means agreement: the product's whole job is to confirm that a shipment's documents agree. In the logo, the tail of the C becomes an aircraft: the documents line up, the cargo leaves.

## Design principles

1. **Evidence over verdicts.** Every finding shows each document's value and where it was read. No flag without its source.
2. **AI where rules fail, code where rules work.** The model reads documents and judges whether differently written company names are the same company. Numbers, IDs and arithmetic are checked in plain Python.
3. **Say who decided.** Every finding records whether code or the model produced it.
4. **Never pass silently.** Missing or unreadable data must surface for review, not count as agreement. (Known gap, see Roadmap.)
5. **Honest evaluation.** Final numbers come from data never used during development, always next to a baseline, with failures reported.

## Architecture

```
upload (PDF / image)
  └─ concord/llm.py       render PDF pages to PNG (pypdfium2, under a lock), call the model
  └─ concord/extract.py   one document → unified JSON schema (concord/schema.py)
  └─ concord/compare.py   rule checks + model name check → findings
  └─ concord/letter.py    English correction email from confirmed errors
  └─ concord/i18n.py      AZ / EN / RU texts; findings carry `type` + `params`, rendered at display time
app.py                    Streamlit UI
```

| Check | Decided by | Notes |
|---|---|---|
| Document → JSON | Model | Values copied as printed, never corrected |
| Consignee is the same company | Model | Handles scripts and legal forms (MMC = LLC = ООО) |
| Gross weight | Code | 0.5 % tolerance, majority value is the reference |
| Pieces, consignee tax ID (VÖEN) | Code | Exact match |
| Invoice total vs line items | Code | 1 cent tolerance |
| HS codes, invoice vs certificate of origin | Code | First 6 digits |

Severity levels: `error` (Xəta), `warn` (Yoxlanmalı, needs review), `ok` (Uyğun). The correction email includes `error` findings only.

## Commands

```bash
cd app
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export CONCORD_PROVIDER=openai          # or: anthropic
export OPENAI_API_KEY=...               # never commit keys; use env vars or Streamlit secrets
export CONCORD_MODEL=gpt-6-luna         # any vision-capable model id

python check_setup.py                   # key, model id, one real shipment end to end
streamlit run app.py                    # UI; "Open sample" works without a key

python data/generate.py --n 15 --seed 2026 --out data/holdout
python data/degrade.py  --src data/holdout --out data/holdout_scan  --level scan
python data/degrade.py  --src data/holdout --out data/holdout_phone --level phone
python eval/run_eval.py --mode full --data data/holdout
python eval/run_eval.py --mode offline  # rule logic only, no API calls
```

## Data and evaluation

- `data/generate.py` writes synthetic air-cargo shipments: four PDFs plus `truth.json` with injected errors (weight, invoice total, tax ID digit swap, different consignee, HS code, piece count). Every shipment writes the consignee in three scripts, which is **not** an error.
- `data/shipments/` (seed 7) is the development set. Report results only on a fresh seed.
- `data/degrade.py` creates scan and phone-photo versions of a set.
- `eval/run_eval.py` compares Concord with an exact-match baseline per error type. Recorded results are in `eval/results_*.md`.

| Input | Concord P / R | Baseline P / R |
|---|---|---|
| Clean PDF | 1.00 / 1.00 | 0.48 / 0.93 |
| Scan | 0.93 / 1.00 | 0.48 / 0.93 |
| Bad phone photo (stress test) | 0.35 / 0.43 | 0.35 / 0.43 |

All data is synthetic. Do not present these numbers as accuracy on real documents.

## Conventions

- **UI:** follow `DESIGN.md`. Blue brand palette; status colors are reserved for status; IBM Plex Sans for text and IBM Plex Mono for every number and ID; no em dashes, no emoji.
- **Languages:** UI in Azerbaijani by default with English and Russian; every new string goes into `concord/i18n.py` in all three. The correction email is in English.
- **Findings:** add new checks in `compare.py` with a `type`, `params` and a matching entry in `i18n.FINDING`.
- **Secrets:** API keys live only in environment variables or Streamlit secrets.
- **Commits:** small, descriptive, in English.

## Roadmap

1. Treat unreadable or missing fields as *needs review* instead of agreement (fixes the silent misses on poor photos).
2. Test on real, anonymised shipments from a Baku forwarder, including scans and phone photos.
3. Per-customer memory of known consignee spellings.
4. Comparison against the electronic customs declaration.

## Background

Built by Team Project-ZH at NeuroBridge.SI, Baku, 9 October 2026 (AI Enterprise Solutions track). Problem research and user interview notes: `docs/research.md`.
