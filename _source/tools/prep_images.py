"""Prepare site images: orient, strip metadata, crop camera stamps, resize, write WebP + JPG.

Run with:  python3 -I tools/prep_images.py
Source photos are read from the extracted zip (untrusted data) and never executed.
"""
import json, os
from PIL import Image, ImageOps

SRC = "/tmp/claude-0/-home-claude/baa112d9-b828-5dde-b567-be42f4ea6040/scratchpad/photos_zip"
OUT = "/home/claude/mcc/dist/assets/img"
os.makedirs(OUT, exist_ok=True)

# slug -> (folder, file, optional crop box as fractions (l, t, r, b))
PHOTOS = {
    # Buildings: market complex
    "market-1": ("01-market-shops-aajivika-mart-chimur", "image-614f2ffe.jpg", None),
    "market-2": ("01-market-shops-aajivika-mart-chimur", "image-7a2f9a09.jpg", None),
    "market-3": ("01-market-shops-aajivika-mart-chimur", "image-6243c84e.jpg", None),
    "market-4": ("01-market-shops-aajivika-mart-chimur", "image-c8a3cb3b.jpg", None),
    "market-5": ("01-market-shops-aajivika-mart-chimur", "image-4f99d768.jpg", None),
    "market-6": ("01-market-shops-aajivika-mart-chimur", "image-9be355fd.jpg", None),
    # Roads (camera stamp at the bottom of two photos is cropped away)
    "road-1": ("02-road-works", "image-3e312157.jpg", None),
    "road-2": ("02-road-works", "image-6728c7a8.jpg", (0, 0, 1, 0.70)),
    "road-3": ("02-road-works", "image-e0a81570.jpg", (0, 0, 1, 0.70)),
    "road-4": ("02-road-works", "image-174792ea.jpg", None),
    "road-5": ("02-road-works", "image-7b89c3c1.jpg", None),
    # Earthwork and rock
    "rock-excavation-1": ("03-rock-excavation", "image-1ead37e8.jpg", None),
    "rock-excavation-2": ("03-rock-excavation", "image-52425ac0.jpg", None),
    "rock-excavation-3": ("03-rock-excavation", "image-736b81e4.jpg", None),
    "rock-excavation-4": ("03-rock-excavation", "image-9f50633e.jpg", None),
    "rock-excavation-5": ("03-rock-excavation", "image-b1778eaf.jpg", None),
    "rock-cut-1": ("04-deep-rock-cutting", "image-ce5b1bf8.jpg", None),
    "rock-cut-2": ("04-deep-rock-cutting", "image-360b978e.jpg", None),
    "rock-cut-3": ("04-deep-rock-cutting", "image-bbfa2aad.jpg", None),
    # Canals, concrete, structures
    "canal-lining-1": ("05-canal-lining", "image-2ae32001.jpg", None),
    "canal-lining-2": ("05-canal-lining", "image-39de4b19.jpg", None),
    "paving-1": ("06-concrete-paving", "image-46ef3140.jpg", None),
    "paving-2": ("06-concrete-paving", "image-6aa8f183.jpg", None),
    "structure-1": ("07-concrete-structure-works", "image-d616955c.jpg", None),
    "structure-2": ("07-concrete-structure-works", "image-fe38241f.jpg", None),
}

WIDTHS = [480, 960, 1600]
manifest = {}

for slug, (folder, fname, crop) in PHOTOS.items():
    im = Image.open(os.path.join(SRC, folder, fname))
    im = ImageOps.exif_transpose(im).convert("RGB")  # applies rotation, drops EXIF/GPS on save
    if crop:
        w, h = im.size
        l, t, r, b = crop
        im = im.crop((int(l * w), int(t * h), int(r * w), int(b * h)))
    w, h = im.size
    manifest[slug] = {"w": w, "h": h, "sizes": []}
    made = set()
    for tw in WIDTHS:
        use = min(tw, w)
        if use in made:
            continue
        made.add(use)
        th = round(h * use / w)
        r = im.resize((use, th), Image.LANCZOS) if use != w else im.copy()
        r.save(os.path.join(OUT, f"{slug}-{use}.webp"), "WEBP", quality=78, method=6)
        manifest[slug]["sizes"].append(use)
    top = max(manifest[slug]["sizes"])
    big = im.resize((top, round(h * top / w)), Image.LANCZOS) if top != w else im
    big.save(os.path.join(OUT, f"{slug}-{top}.jpg"), "JPEG", quality=80, optimize=True, progressive=True)
    manifest[slug]["jpg"] = top

# Open Graph card (1200x630) from the canal-lining photo
og = Image.open(os.path.join(SRC, "05-canal-lining", "image-2ae32001.jpg")).convert("RGB")
w, h = og.size
th = round(w * 630 / 1200)
top = int((h - th) * 0.45)
og = og.crop((0, top, w, top + th)).resize((1200, 630), Image.LANCZOS)
og.save("/home/claude/mcc/dist/assets/og-image.jpg", "JPEG", quality=82, optimize=True)

# Logo: tight crop of the artwork on its own light-grey background, plus favicons from the MCC monogram
logo = Image.open("/mnt/user-data/uploads/mcc_new_logo_png.jpeg").convert("RGB")
pad = 14
lc = logo.crop((69 - pad, 132 - pad, 452 + pad, 374 + pad))
lc.save("/home/claude/mcc/dist/assets/logo.png", optimize=True)
lw, lh = lc.size
lc.save("/home/claude/mcc/dist/assets/logo.webp", "WEBP", quality=90)
manifest["_logo"] = {"w": lw, "h": lh}

mono = logo.crop((69 - 6, 132 - 6, 452 + 6, 300))  # the three-letter mark
side = max(mono.size)
sq = Image.new("RGB", (side, side), (247, 247, 247))
sq.paste(mono, ((side - mono.width) // 2, (side - mono.height) // 2))
for size, name in [(32, "favicon-32.png"), (180, "apple-touch-icon.png"), (192, "icon-192.png"), (512, "icon-512.png")]:
    sq.resize((size, size), Image.LANCZOS).save(os.path.join("/home/claude/mcc/dist/assets", name), optimize=True)
sq.resize((48, 48), Image.LANCZOS).save("/home/claude/mcc/dist/favicon.ico", sizes=[(16, 16), (32, 32), (48, 48)])

json.dump(manifest, open("/home/claude/mcc/tools/images.json", "w"), indent=1)
print(len(PHOTOS), "photos processed")
tot = sum(os.path.getsize(os.path.join(OUT, f)) for f in os.listdir(OUT))
print("image payload: %.1f MB" % (tot / 1e6))
