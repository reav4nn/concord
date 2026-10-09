"""Step 1: read each document (PDF or image) with the model and return the unified schema."""
import json
from pathlib import Path
from .schema import EXTRACTION_SCHEMA
from .llm import ask_json, file_to_images

SYSTEM = (
    "You extract data from freight and customs documents (commercial invoice, packing list, "
    "certificate of origin, air waybill). Documents may mix Azerbaijani, Russian, English and Chinese. "
    "Copy values exactly as printed: do not correct, normalise or translate names, and do not fix "
    "arithmetic. Numbers: plain numbers (1284.0), weights in kg. HS codes: digits only. "
    "If a field is not on the document, return null. Return ONLY one JSON object matching the schema."
)


def extract(path, doc_type_hint: str | None = None) -> dict:
    path = Path(path)
    hint = f"This document is probably a {doc_type_hint}. " if doc_type_hint else ""
    out = ask_json(SYSTEM, hint + "Extract this JSON schema:\n" + json.dumps(EXTRACTION_SCHEMA),
                   images=file_to_images(path))
    if doc_type_hint and out.get("doc_type") not in ("invoice", "packing_list", "certificate_of_origin", "awb"):
        out["doc_type"] = doc_type_hint
    out.setdefault("items", [])
    out["_source_file"] = path.name
    return out
