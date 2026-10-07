"""Generate img/og.png, the default social share image (1200x630). Run: python3 build/make_og.py"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
W, H = 1200, 630
f = "/System/Library/Fonts/Supplemental/Georgia.ttf"
im = Image.new("RGB", (W, H), "#faf7f1")
d = ImageDraw.Draw(im)
t, s, m, mk = (ImageFont.truetype(f, n) for n in (84, 34, 32, 64))
d.rectangle([0, 0, W, 16], fill="#9b2f1f")
d.rectangle([80, 70, 160, 150], fill="#9b2f1f")
d.text((120, 110), "§", font=mk, fill="#faf7f1", anchor="mm")
d.text((190, 110), "Laws of AI Evaluation", font=m, fill="#1b1b1b", anchor="lm")
d.text((80, 210), "Principles for judging", font=t, fill="#1b1b1b")
d.text((80, 305), "whether an AI system", font=t, fill="#1b1b1b")
d.text((80, 400), "actually holds up.", font=t, fill="#9b2f1f")
d.text((80, 565), "26 short, sourced laws  ·  lawsofaievaluation.com", font=s, fill="#555555", anchor="lm")
(ROOT / "img").mkdir(exist_ok=True)
im.save(ROOT / "img" / "og.png", optimize=True)
