"""Make "phone photo" / "scan" JPEG copies of a shipment set to test Concord on messy inputs.
Usage: python data/degrade.py --src data/holdout --out data/holdout_phone --level phone"""
import argparse, random, shutil
from pathlib import Path
import pypdfium2 as pdfium
from PIL import Image, ImageFilter, ImageEnhance, ImageOps, ImageChops
LEVELS = {"scan": dict(rot=1.2, blur=0.8, noise=10, q=55, scale=1.6, persp=0.0, light=0.10),
          "phone": dict(rot=4.0, blur=1.4, noise=18, q=40, scale=1.2, persp=0.04, light=0.35)}
def degrade(img, c, rng):
    img = img.convert("L"); w, h = img.size
    if c["persp"]:
        d = c["persp"]; r = lambda m: rng.uniform(-d, d) * m
        img = img.transform((w, h), Image.QUAD, (r(w), r(h), r(w), h + r(h), w + r(w), h + r(h), w + r(w), r(h)), resample=Image.BICUBIC, fillcolor=235)
    img = img.rotate(rng.uniform(-c["rot"], c["rot"]), resample=Image.BICUBIC, expand=True, fillcolor=235)
    grad = Image.linear_gradient("L").resize(img.size)
    if rng.random() < 0.5: grad = ImageOps.mirror(grad.rotate(90))
    img = ImageChops.subtract(img, ImageEnhance.Brightness(grad).enhance(c["light"]))
    img = ImageEnhance.Contrast(img).enhance(rng.uniform(0.75, 0.95)).filter(ImageFilter.GaussianBlur(c["blur"]))
    return ImageChops.add(img, Image.effect_noise(img.size, c["noise"]), scale=1.0, offset=-128)
if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--src"); ap.add_argument("--out"); ap.add_argument("--level", default="phone")
    a = ap.parse_args(); c = LEVELS[a.level]; rng = random.Random(11)
    for sd in sorted(p for p in Path(a.src).iterdir() if p.is_dir()):
        od = Path(a.out) / sd.name; od.mkdir(parents=True, exist_ok=True); shutil.copy(sd / "truth.json", od / "truth.json")
        for pp in sorted(sd.glob("*.pdf")):
            pdf = pdfium.PdfDocument(str(pp)); img = pdf[0].render(scale=c["scale"]).to_pil(); pdf.close()
            degrade(img, c, rng).save(od / f"{pp.stem}.jpg", quality=c["q"])
    print(a.level, "->", a.out)
