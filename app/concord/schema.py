"""Unified document schema. Every document type is extracted into this shape.
Fields a document does not carry stay None."""

DOC_TYPES = ["invoice", "packing_list", "certificate_of_origin", "awb"]

DOC_LABELS = {
    "invoice": "Invoice",
    "packing_list": "Packing list",
    "certificate_of_origin": "Mənşə sertifikatı",
    "awb": "AWB",
}

EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "doc_type": {"type": "string", "enum": DOC_TYPES},
        "shipper_name": {"type": ["string", "null"]},
        "consignee_name": {"type": ["string", "null"]},
        "consignee_tax_id": {"type": ["string", "null"], "description": "VÖEN / tax ID, digits only"},
        "invoice_no": {"type": ["string", "null"]},
        "awb_no": {"type": ["string", "null"]},
        "currency": {"type": ["string", "null"]},
        "gross_weight_kg": {"type": ["number", "null"]},
        "net_weight_kg": {"type": ["number", "null"]},
        "packages": {"type": ["integer", "null"], "description": "number of pieces / cartons"},
        "origin_country": {"type": ["string", "null"]},
        "total_amount": {"type": ["number", "null"], "description": "the TOTAL printed on the document"},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "description": {"type": "string"},
                    "hs_code": {"type": ["string", "null"]},
                    "qty": {"type": ["number", "null"]},
                    "amount": {"type": ["number", "null"]},
                },
                "required": ["description"],
            },
        },
    },
    "required": ["doc_type"],
}

# Error types the generator injects and the checker must find.
ERROR_TYPES = [
    "weight_mismatch",     # gross weight differs between documents
    "total_mismatch",      # invoice TOTAL != sum of line items
    "tax_id_mismatch",     # consignee VÖEN differs (digit swap)
    "consignee_mismatch",  # a genuinely different consignee company
    "hs_mismatch",         # HS code differs between invoice and certificate of origin
    "package_mismatch",    # number of pieces differs
]
