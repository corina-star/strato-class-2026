"""Builds the signature sheet PDF for Executive Awards.

Input: signers.json, a list of {"full_name", "crew", "signature"} rows,
exported from Supabase (project fairway-read-along, table strato_signups).
Output: strato-signature-sheet.pdf, one cell per signer:
signature on top, full name and crew number in small letters beneath.
"""
import io, json, sys, urllib.request
from PIL import Image, ImageDraw, ImageFont

BUCKET = "https://ihtddoaefacyovcxcqrh.supabase.co/storage/v1/object/public/strato-sig/"
rows = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "signers.json"))
rows.sort(key=lambda r: (r["crew"] is None, r["crew"] or 0, r["full_name"]))

W, H, M = 2550, 3300, 150                     # US Letter at 300 dpi
COLS, CW, CH = 3, (2550 - 2 * 150) // 3, 520
PER_PAGE = ((H - 2 * M - 180) // CH) * COLS
title = ImageFont.truetype("/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf", 90)
small = ImageFont.truetype("/System/Library/Fonts/Supplemental/DIN Condensed Bold.ttf", 44)

pages = []
for p in range(0, max(len(rows), 1), PER_PAGE):
    pg = Image.new("RGB", (W, H), "white"); d = ImageDraw.Draw(pg)
    d.text((W / 2, M), "STRATOSPHERE CLASS OF 2026 · SIGNATURES", font=title, fill="black", anchor="mt")
    for i, r in enumerate(rows[p:p + PER_PAGE]):
        x = M + (i % COLS) * CW; y = M + 180 + (i // COLS) * CH
        sig = Image.open(io.BytesIO(urllib.request.urlopen(BUCKET + r["signature"]).read())).convert("RGB")
        sig.thumbnail((CW - 60, CH - 130))
        pg.paste(sig, (x + (CW - sig.width) // 2, y + (CH - 130 - sig.height) // 2))
        label = r["full_name"].upper() + (f"  ·  CREW #{r['crew']}" if r["crew"] else "")
        d.text((x + CW / 2, y + CH - 100), label, font=small, fill="black", anchor="mt")
        d.rectangle([x + 10, y, x + CW - 10, y + CH - 30], outline="#cccccc", width=3)
    pages.append(pg)
pages[0].save("strato-signature-sheet.pdf", save_all=True, append_images=pages[1:], resolution=300)
print(len(rows), "signers,", len(pages), "page(s)")
