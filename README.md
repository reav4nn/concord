<p align="center">
  <img src="brand/concord-lockup.png" alt="Concord" width="420">
</p>

<p align="center"><b>Freight documents that agree before customs does.</b></p>

<p align="center">
  NeuroBridge.SI · Baku · 9-10 October 2026 · AI Enterprise Solutions · Team Project-ZH
</p>

---

Concord reads the four documents of an air-cargo shipment (commercial invoice, packing list, certificate of origin, air waybill), cross-checks them against each other, shows every discrepancy with the value and location from each document, and drafts the correction email to the shipper.

## The problem

A declarant at a Baku freight forwarder or customs broker receives four documents per shipment, each filled in by a different party. Today they are compared by eye.

> "With all documents in hand it takes 5-10 minutes, sometimes 20. Errors can be anywhere; most often the consignee side is wrong, and the arithmetic, an amount off by 5 dollars."
> Asad Piriyev, Air Cargo Azerbaijan (phone interview, 9 Oct 2026)

The same company also appears in three scripts across one shipment (`Kür Elektronika MMC`, `KUR ELEKTRONIKA LLC`, `ООО «Кюр Электроника»`), so simple field matching raises false alarms on almost every shipment.

## How it works

```
 PDF / scan / photo ──► 1. Extract (LLM vision) ──► one JSON schema per document
                                                          │
                       2. Cross-check ◄───────────────────┘
                          ├─ code:  gross weight (0.5% tolerance), pieces, tax ID (VÖEN),
                          │         invoice total vs line items, HS codes
                          └─ LLM:   is every consignee spelling the same company?
                                                          │
                       3. Report: Xəta / Yoxlanmalı / Uyğun, each with evidence table
                       4. Correction email built from confirmed errors only
```

| Step | Decided by | Why |
|---|---|---|
| Read PDF or photo into data | LLM | Layouts differ, languages mix, scans are messy |
| Same company across scripts? | LLM | Transliteration and legal forms (MMC = LLC = ООО) have no rule |
| Weight, pieces, tax ID, HS code, invoice total | Code | Exact and testable; no reason to let a model guess numbers |
| Correction email | Code | Built only from confirmed errors; nothing invented |

Every finding in the UI states which of the two produced it.

## Results

Same 15 unseen shipments (seed 2026, never used while building), 14 injected errors across 6 types, three input qualities. Model: GPT-6 Luna. Baseline: exact field matching.

| Input | Concord precision / recall | Baseline precision / recall |
|---|---|---|
| Clean PDF | **1.00 / 1.00** | 0.48 / 0.93 |
| Scan (blur, tilt, noise) | **0.93 / 1.00** | 0.48 / 0.93 |
| Bad phone photo (stress test) | 0.35 / 0.43 | 0.35 / 0.43 |

About 17 s per shipment (4 extractions + 1 name check, run in parallel). Full per-type tables: [`app/eval/results_clean.md`](app/eval/results_clean.md), [`results_scan.md`](app/eval/results_scan.md), [`results_phone.md`](app/eval/results_phone.md).

### What broke

- **Bad photos.** The model returned empty fields; empty fields were treated as "no conflict", so errors passed silently. Next fix: an unreadable field becomes *Yoxlanmalı* (needs review), never a silent pass.
- **One false alarm on scans.** A blurred consignee name was judged a different company (1 of 15; the baseline raises this alarm in 15 of 15).
- **Parallel PDF rendering crashed.** pdfium is not thread-safe; rendering now runs under a lock while model calls stay parallel.
- **Synthetic data.** All shipments come from our generator. The next test set is real, anonymised shipments from a forwarder.

## Quick start

Requires Python 3.11+.

```bash
cd app
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

export CONCORD_PROVIDER=openai
export OPENAI_API_KEY=sk-...
export CONCORD_MODEL=gpt-6-luna      # any vision model your key can use

python check_setup.py                # verifies key, model, and runs one real shipment
streamlit run app.py
```

**Live demo:** https://projectzh-concord.streamlit.app/?lang=en. No API key needed for **Open sample**, which loads a precomputed result. Language switch (AZ / EN / RU) at the bottom.

To use Anthropic instead: `CONCORD_PROVIDER=anthropic`, `ANTHROPIC_API_KEY`, `CONCORD_MODEL=<claude model id>`.

### Reproduce the evaluation

```bash
python data/generate.py --n 15 --seed 2026 --out data/holdout
python data/degrade.py  --src data/holdout --out data/holdout_scan  --level scan
python data/degrade.py  --src data/holdout --out data/holdout_phone --level phone

python eval/run_eval.py --mode full --data data/holdout
python eval/run_eval.py --mode full --data data/holdout_scan
python eval/run_eval.py --mode full --data data/holdout_phone
python eval/run_eval.py --mode offline        # rule logic only, no API calls
```

## Repository

```
app/
  app.py                 Streamlit UI (upload, findings, correction letter, extracted data)
  check_setup.py         first-run check: key, model, one real shipment
  concord/
    llm.py               provider switch (OpenAI / Anthropic), PDF → image rendering
    extract.py           document → unified JSON schema
    compare.py           rule checks + LLM company-name check
    letter.py            correction email from confirmed errors
    schema.py            schema and error types
  data/
    generate.py          synthetic shipments (4 PDFs + ground truth)
    degrade.py           scan / phone-photo versions of a set
    shipments/           30 development shipments (seed 7)
  eval/
    run_eval.py          Concord vs baseline, precision / recall per error type
    results_*.md         recorded holdout results
  demo/sample_result.json  offline demo result
brand/                   logo, lockups, app icon
design/                  UI and logo design sources
docs/                    research notes, pitch outline, submission text
CLAUDE.md                project context and decisions
DESIGN.md                design system
```

## Disclosure

- **Built** during NeuroBridge.SI on 9 October 2026. Idea research, the interview and phone calls were done on day one.
- **Models:** OpenAI GPT-6 Luna via API (extraction and company-name matching). All numeric and ID checks are plain Python.
- **Data:** synthetic only, from `app/data/generate.py`. No real customer documents.
- **Components:** Streamlit, openai and anthropic Python SDKs, pypdfium2, Pillow, reportlab, IBM Plex and DejaVu fonts. Logo drafted with ChatGPT image generation and vectorised by the team.

## Next step

A two-week pilot with a Baku forwarder on about 200 anonymised real shipments, including scans and phone photos. Metrics: minutes per shipment and errors caught before documents are sent.

---

Team Project-ZH · Private repository, shared with the judges for verification.
