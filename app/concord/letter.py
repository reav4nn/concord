"""Correction letter to the shipper (English), built from error findings only (warnings wait for the broker)."""
from .i18n import finding_text, doc_label


def build_letter(findings, awb_no="[AWB]", shipper="[SHIPPER]"):
    errs = [f for f in findings if f["severity"] == "error"]
    if not errs:
        return None
    lines = [f"Dear {shipper} team,", "",
             f"Before we submit AWB {awb_no} to customs, please correct the following:", ""]
    for i, f in enumerate(errs, 1):
        bad = [r for r in f["rows"] if r.get("bad")]
        good = [r for r in f["rows"] if not r.get("bad")]
        detail = "; ".join(f"{doc_label(r.get('doc_key'), 'en') if r.get('doc_key') else r['doc']}: {r['value']}" for r in bad)
        ref = f" (other documents: {good[0]['value']})" if good else ""
        lines.append(f"{i}. {finding_text(f, 'en')['field']}: {detail}{ref}.")
    lines += ["", "Please send the corrected documents to this address.", "", "Best regards,", "[YOUR NAME], [COMPANY]"]
    return "\n".join(lines)
