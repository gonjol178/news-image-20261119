#!/usr/bin/env python3
"""Compose the 19 Nov 2026 front page: panels + crisp PIL-rendered headlines."""
from PIL import Image, ImageDraw, ImageFont
import os

A = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'entry.png')

SERIF_B = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf'
SANS_B = '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
SANS = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (20, 16, 12)
GREY = (84, 78, 68)
RULE = (20, 16, 12)
ACCENT = (146, 22, 22)

img = Image.new('RGB', (W, H), PAPER)
d = ImageDraw.Draw(img)

def font(path, size):
    return ImageFont.truetype(path, size)

def fit(img_src, w, h):
    """Center-crop image to cover w x h, return resized copy."""
    iw, ih = img_src.size
    scale = max(w / iw, h / ih)
    nw, nh = int(iw * scale + 0.5), int(ih * scale + 0.5)
    r = img_src.resize((nw, nh), Image.LANCZOS)
    x = (nw - w) // 2
    y = (nh - h) // 2
    return r.crop((x, y, x + w, y + h))

def panel(name, x, y, w, h):
    p = Image.open(os.path.join(A, name)).convert('RGB')
    img.paste(fit(p, w, h), (x, y))
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=INK, width=2)

def wrap(text, fnt, maxw):
    words, lines, cur = text.split(), [], ''
    for w_ in words:
        t = (cur + ' ' + w_).strip()
        if d.textlength(t, font=fnt) <= maxw:
            cur = t
        else:
            lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

M = 26  # margin

# ---------- masthead ----------
y = 18
d.text((W // 2, y), 'T H E   W O R L D   I N   O N E   D A Y', font=font(SANS_B, 21),
       fill=ACCENT, anchor='ma')
y += 34
d.line([M, y, W - M, y], fill=RULE, width=3)
y += 10
d.text((W // 2, y), 'THURSDAY, 19 NOVEMBER 2026', font=font(SERIF_B, 48), fill=INK, anchor='ma')
y += 66
d.line([M, y, W - M, y], fill=RULE, width=3)
y += 12

# ---------- lead story: Shenzhen trilateral ----------
panel('media-generation-panel-shenzhen-0-23ede0ba-c75d-4c9e-9241-f717b7cf1a66.webp', M, y, W - 2 * M, 256)
y += 268
for ln in wrap('TRUMP, XI AND PUTIN MEET IN SHENZHEN', font(SERIF_B, 40), W - 2 * M):
    d.text((M, y), ln, font=font(SERIF_B, 40), fill=INK)
    y += 48
for ln in wrap('First three-way summit ends in a joint declaration on nuclear risks and '
               'stable energy flows; Ukraine not mentioned', font(SANS, 20), W - 2 * M):
    d.text((M, y), ln, font=font(SANS, 20), fill=GREY)
    y += 27
y += 8
d.line([M, y, W - M, y], fill=RULE, width=2)
y += 12

# ---------- middle row: ICJ Myanmar + Kerch Bridge ----------
colw = (W - 2 * M - 16) // 2
panel('media-generation-panel-icj-0-6ea342ed-0145-4ccc-bfc6-1f457a60820f.webp', M, y, colw, 140)
panel('media-generation-panel-kerch-0-59159dae-2428-4542-823a-a3904d53f6b3.webp', M + colw + 16, y, colw, 140)
y += 150
cap_y = y
for ln in wrap('U.N. COURT RULES MYANMAR COMMITTED GENOCIDE', font(SANS_B, 22), colw):
    d.text((M, cap_y), ln, font=font(SANS_B, 22), fill=INK); cap_y += 28
for ln in wrap('First such ruling by the highest U.N. court; 2017 crackdown killed '
               'thousands of Rohingya', font(SANS, 16), colw):
    d.text((M, cap_y), ln, font=font(SANS, 16), fill=GREY); cap_y += 21
cap2_y = y
for ln in wrap('UKRAINE HITS KERCH BRIDGE A THIRD TIME', font(SANS_B, 22), colw):
    d.text((M + colw + 16, cap2_y), ln, font=font(SANS_B, 22), fill=INK); cap2_y += 28
for ln in wrap("Third strike on the Crimea link this week; rail traffic halted after "
               'the latest attack', font(SANS, 16), colw):
    d.text((M + colw + 16, cap2_y), ln, font=font(SANS, 16), fill=GREY); cap2_y += 21
y = max(cap_y, cap2_y) + 8
d.line([M, y, W - M, y], fill=RULE, width=2)
y += 12

# ---------- bottom row: Gaza text story + one-liners ----------
bot_y = y
for ln in wrap('ISRAEL WRAPS UP CENTRAL GAZA OPERATION', font(SANS_B, 20), colw):
    d.text((M, bot_y), ln, font=font(SANS_B, 20), fill=INK); bot_y += 26
for ln in wrap('Tanks rolled past the Yellow Line near Nuseirat; the IDF says the raid '
               'against Hamas infrastructure is over', font(SANS, 16), colw):
    d.text((M, bot_y), ln, font=font(SANS, 16), fill=GREY); bot_y += 21
tx = M + colw + 16
ty = y
items = [
    ('RIYADH', 'Apparent Houthi strike damages PIF Tower'),
    ('DHAKA', 'Yunus home torched; four killed in unrest'),
    ('COPENHAGEN', 'Denmark OKs Greenland-U.S. Arctic deal'),
    ('SEOUL', 'Top court clears ex-PM Han over martial law'),
    ('SILICON VALLEY', "Anthropic's record $81bn IPO opens"),
]
for head, body in items:
    d.text((tx, ty), head + ' \u2014 ', font=font(SANS_B, 16), fill=ACCENT)
    hw = d.textlength(head + ' \u2014 ', font=font(SANS_B, 16))
    d.text((tx + hw, ty), body, font=font(SANS, 16), fill=INK)
    ty += 25

# ---------- footer ----------
d.line([M, H - 44, W - M, H - 44], fill=RULE, width=3)
d.text((W // 2, H - 36), 'ONE DAY \u2022 ONE PAGE \u2022 THE WORLD ON THURSDAY 19 NOVEMBER 2026',
       font=font(SANS_B, 16), fill=GREY, anchor='ma')

img.save(OUT)
print('saved', OUT, img.size, os.path.getsize(OUT), 'bytes')
