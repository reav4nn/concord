"""Run this FIRST after setting the key: python check_setup.py
Checks the API key, the model name, PDF rendering and one real extraction."""
import json, os, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from concord import llm

print("provider:", llm.PROVIDER, "| model:", llm.MODEL)
if llm.PROVIDER == "openai" and not os.getenv("OPENAI_API_KEY"):
    sys.exit("OPENAI_API_KEY is not set")
if llm.PROVIDER == "openai":
    from openai import OpenAI
    ids = sorted(m.id for m in OpenAI().models.list())
    if llm.MODEL not in ids:
        print(f"Model '{llm.MODEL}' is not available for this key. Similar models:")
        print([i for i in ids if i.startswith("gpt")][-30:])
        sys.exit(1)
from concord.extract import extract
from concord.compare import check
ship = Path(__file__).parent / "data" / "shipments" / "ship_02"
t0 = time.time()
docs = [extract(ship / f"{t}.pdf", t) for t in ("invoice", "packing_list", "certificate_of_origin", "awb")]
print(f"extracted 4 docs in {time.time() - t0:.1f}s")
print(json.dumps(docs[0], ensure_ascii=False, indent=1)[:1500])
res = check(docs)
print("findings:", [(f["severity"], f["type"]) for f in res["findings"]])
print("truth   :", json.loads((ship / "truth.json").read_text())["labels"])
