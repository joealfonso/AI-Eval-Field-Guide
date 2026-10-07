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
d.text((190, 110), "AI Evaluation Field Guide", font=m, fill="#1b1b1b", anchor="lm")
d.text((80, 210), "Principles for judging", font=t, fill="#1b1b1b")
d.text((80, 305), "whether an AI system", font=t, fill="#1b1b1b")
d.text((80, 400), "actually holds up.", font=t, fill="#9b2f1f")
d.text((80, 565), "26 short, sourced patterns  ·  lawsofaievaluation.com", font=s, fill="#555555", anchor="lm")
(ROOT / "img").mkdir(exist_ok=True)
im.save(ROOT / "img" / "og.png", optimize=True)


# ---- per-law share images: img/og/<slug>.png
import json, textwrap

laws = json.loads((ROOT / "data" / "laws.json").read_text(encoding="utf-8"))
laws = laws["laws"] if isinstance(laws, dict) else laws
cats = {"I": "What you’re measuring", "II": "The test itself", "III": "Running the eval", "IV": "Reading the results", "V": "Beyond the benchmark"}
ital = ImageFont.truetype("/System/Library/Fonts/Supplemental/Georgia Italic.ttf", 40)
big = ImageFont.truetype(f, 86)
small = ImageFont.truetype(f, 30)
(ROOT / "img" / "og").mkdir(parents=True, exist_ok=True)


def wrap(text, font, width):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if d2.textlength(trial, font=font) <= width:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    return lines + [cur]


for l in laws:
    im2 = Image.new("RGB", (W, H), "#faf7f1")
    d2 = ImageDraw.Draw(im2)
    d2.rectangle([0, 0, W, 16], fill="#9b2f1f")
    d2.rectangle([80, 60, 140, 120], fill="#9b2f1f")
    d2.text((110, 90), "§", font=ImageFont.truetype(f, 48), fill="#faf7f1", anchor="mm")
    d2.text((165, 90), "AI Evaluation Field Guide", font=small, fill="#1b1b1b", anchor="lm")
    d2.text((80, 175), "No. %s  ·  %s" % (l["no"], cats.get(l["category"], "")), font=small, fill="#9b2f1f")
    size = 86
    name_font = big
    while d2.textlength(l["name"], font=name_font) > W - 160 and size > 50:
        size -= 4
        name_font = ImageFont.truetype(f, size)
    d2.text((80, 225), l["name"], font=name_font, fill="#1b1b1b")
    y = 345
    for line in wrap("“%s”" % l["aphorism"], ital, W - 160)[:4]:
        d2.text((80, y), line, font=ital, fill="#444444")
        y += 56
    d2.text((80, 575), "lawsofaievaluation.com", font=small, fill="#555555", anchor="lm")
    im2.save(ROOT / "img" / "og" / ("%s.png" % l["slug"]), optimize=True)
