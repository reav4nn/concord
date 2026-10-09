"""One place for model calls. Provider and model come from the environment:

  CONCORD_PROVIDER = openai (default) | anthropic
  CONCORD_MODEL    = exact model id, e.g. the GPT model your key has access to
  OPENAI_API_KEY / ANTHROPIC_API_KEY

PDFs are rendered to PNG pages (pypdfium2) so both providers receive images.
"""
import base64, io, json, mimetypes, os, threading
_PDF_LOCK = threading.Lock()
from pathlib import Path

PROVIDER = os.getenv("CONCORD_PROVIDER", "openai").lower()
MODEL = os.getenv("CONCORD_MODEL", "gpt-5" if PROVIDER == "openai" else "claude-sonnet-5-5")
MAX_PAGES = 3


def file_to_images(path: Path) -> list[tuple[bytes, str]]:
    """Return [(png_or_jpeg_bytes, mime)] for a PDF (first MAX_PAGES pages) or an image."""
    mime = mimetypes.guess_type(path.name)[0] or ""
    if mime == "application/pdf" or path.suffix.lower() == ".pdf":
        import pypdfium2 as pdfium
        out = []
        with _PDF_LOCK:
            pdf = pdfium.PdfDocument(str(path))
            for i in range(min(len(pdf), MAX_PAGES)):
                img = pdf[i].render(scale=2).to_pil()
                buf = io.BytesIO(); img.save(buf, format="PNG")
                out.append((buf.getvalue(), "image/png"))
            pdf.close()
        return out
    return [(path.read_bytes(), mime or "image/png")]


def _parse_json(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1].removeprefix("json").strip()
    start, end = text.find("{"), text.rfind("}")
    return json.loads(text[start:end + 1])


def ask_json(system: str, prompt: str, images: list[tuple[bytes, str]] = (), max_tokens: int = 2000) -> dict:
    if PROVIDER == "openai":
        from openai import OpenAI
        client = OpenAI()
        content = [{"type": "image_url", "image_url": {"url": f"data:{m};base64,{base64.b64encode(b).decode()}"}}
                   for b, m in images]
        content.append({"type": "text", "text": prompt})
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": content}],
            response_format={"type": "json_object"},
            max_completion_tokens=max_tokens,
        )
        return _parse_json(resp.choices[0].message.content)
    import anthropic
    client = anthropic.Anthropic()
    content = [{"type": "image", "source": {"type": "base64", "media_type": m, "data": base64.b64encode(b).decode()}}
               for b, m in images]
    content.append({"type": "text", "text": prompt})
    msg = client.messages.create(model=MODEL, max_tokens=max_tokens, system=system,
                                 messages=[{"role": "user", "content": content}])
    return _parse_json("".join(b.text for b in msg.content if b.type == "text"))
