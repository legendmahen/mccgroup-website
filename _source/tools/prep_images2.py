"""Adds the second batch of site photos (14) to dist/assets/img and tools/images.json.
Crops away the GPS-camera panel on the Bhisi photos and the date stamp on two others; strips EXIF."""
import json, os
from PIL import Image, ImageOps
A = "/mnt/user-data/attachments/baa112d9-b828-5dde-b567-be42f4ea6040/"
OUT = "/home/claude/mcc/dist/assets/img"
GPS = (0, 0, 1, 0.76)
STAMP = (0, 0, 1, 0.92)
P = {
    "structure-5": ("2a9d642b", None),
    "structure-6": ("9dc5ae3f", None), "earthwork-1": ("55b21348", None), "earthwork-2": ("550d6b40", STAMP),
    "earthwork-3": ("ae8863f6", None), "fleet-1": ("230ee03b", STAMP),
    "village-1": ("493553b3", GPS), "village-2": ("73e1ed6c", GPS), "village-3": ("762d2981", GPS),
    "village-4": ("496955a8", GPS), "village-5": ("e944b643", GPS), "village-6": ("f2d38c51", GPS),
}
mf = json.load(open("/home/claude/mcc/tools/images.json"))
for slug, (fid, crop) in P.items():
    im = ImageOps.exif_transpose(Image.open(f"{A}{fid}-image.jpg")).convert("RGB")
    if crop:
        w, h = im.size; l, t, r, b = crop
        im = im.crop((int(l*w), int(t*h), int(r*w), int(b*h)))
    w, h = im.size
    mf[slug] = {"w": w, "h": h, "sizes": []}
    for tw in (480, 960, 1600):
        use = min(tw, w)
        if use in mf[slug]["sizes"]: continue
        r = im.resize((use, round(h*use/w)), Image.LANCZOS) if use != w else im.copy()
        r.save(f"{OUT}/{slug}-{use}.webp", "WEBP", quality=78, method=6)
        mf[slug]["sizes"].append(use)
    top = max(mf[slug]["sizes"])
    big = im.resize((top, round(h*top/w)), Image.LANCZOS) if top != w else im
    big.save(f"{OUT}/{slug}-{top}.jpg", "JPEG", quality=80, optimize=True, progressive=True)
    mf[slug]["jpg"] = top
json.dump(mf, open("/home/claude/mcc/tools/images.json", "w"), indent=1)
print(len(P), "added")
