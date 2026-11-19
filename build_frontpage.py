#!/usr/bin/env python3
"""Render the 19 November 2026 front page from photo panels + set type.

The three photographs are AI-generated editorial panels stored under
``assets/`` (no text in them). Every word on the page is drawn here with
Pillow, so no headline can garble. Running this script rewrites
``entry.png`` next to it; the output is deterministic.
"""
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(HERE, "assets")

PAGE_W, PAGE_H = 1024, 1024
MARGIN = 26
PAPER_RGB = (247, 243, 234)
INK_RGB = (20, 16, 12)
GREY_RGB = (84, 78, 68)
RED_RGB = (146, 22, 22)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
FONTS = {
    "serif_b": os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf"),
    "sans_b": os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"),
    "sans": os.path.join(FONT_DIR, "DejaVuSans.ttf"),
}


def typeface(kind, size):
    return ImageFont.truetype(FONTS[kind], size)


def cover_crop(source, box_w, box_h):
    """Resize + centre-crop an image so it exactly covers box_w x box_h."""
    iw, ih = source.size
    factor = max(box_w / iw, box_h / ih)
    grown = source.resize((int(iw * factor + 0.5), int(ih * factor + 0.5)),
                          Image.LANCZOS)
    left = (grown.size[0] - box_w) // 2
    top = (grown.size[1] - box_h) // 2
    return grown.crop((left, top, left + box_w, top + box_h))


class Page:
    """A blank front page with a vertical cursor and drawing helpers."""

    def __init__(self):
        self.sheet = Image.new("RGB", (PAGE_W, PAGE_H), PAPER_RGB)
        self.pen = ImageDraw.Draw(self.sheet)
        self.y = 0

    def rule(self, weight=2, gap_above=0, gap_below=0):
        self.y += gap_above
        self.pen.line([MARGIN, self.y, PAGE_W - MARGIN, self.y],
                      fill=INK_RGB, width=weight)
        self.y += weight + gap_below

    def centred(self, text, kind, size, colour, gap_below=0):
        self.pen.text((PAGE_W // 2, self.y), text,
                      font=typeface(kind, size), fill=colour, anchor="ma")
        self.y += size + gap_below

    def photo(self, filename, x, w, h):
        shot = Image.open(os.path.join(ASSETS, filename)).convert("RGB")
        self.sheet.paste(cover_crop(shot, w, h), (x, self.y))
        self.pen.rectangle([x, self.y, x + w - 1, self.y + h - 1],
                           outline=INK_RGB, width=2)
        return self.y + h

    def flow_text(self, text, kind, size, colour, x, max_w, leading):
        """Draw wrapped text starting at (x, self.y); advance self.y."""
        words, lines, current = text.split(), [], ""
        for word in words:
            trial = (current + " " + word).strip()
            if self.pen.textlength(trial, font=typeface(kind, size)) <= max_w:
                current = trial
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
        for line in lines:
            self.pen.text((x, self.y), line, font=typeface(kind, size),
                          fill=colour)
            self.y += leading
        return self.y


# ---------------------------------------------------------------- stories
LEAD = {
    "photo": "media-generation-panel-shenzhen-0-23ede0ba-c75d-4c9e-9241-f717b7cf1a66.webp",
    "headline": "TRUMP, XI AND PUTIN MEET IN SHENZHEN",
    "deck": "First three-way summit ends in a joint declaration on nuclear "
            "risks and stable energy flows; Ukraine not mentioned",
}

MIDDLE = [
    {
        "photo": "media-generation-panel-icj-0-6ea342ed-0145-4ccc-bfc6-1f457a60820f.webp",
        "headline": "U.N. COURT RULES MYANMAR COMMITTED GENOCIDE",
        "deck": "First such ruling by the highest U.N. court; 2017 crackdown "
                "killed thousands of Rohingya",
    },
    {
        "photo": "media-generation-panel-kerch-0-59159dae-2428-4542-823a-a3904d53f6b3.webp",
        "headline": "UKRAINE HITS KERCH BRIDGE A THIRD TIME",
        "deck": "Third strike on the Crimea link this week; rail traffic "
                "halted after the latest attack",
    },
]

TEXT_STORY = {
    "headline": "ISRAEL WRAPS UP CENTRAL GAZA OPERATION",
    "deck": "Tanks rolled past the Yellow Line near Nuseirat; the IDF says "
            "the raid against Hamas infrastructure is over",
}

ONE_LINERS = [
    ("RIYADH", "Apparent Houthi strike damages PIF Tower"),
    ("DHAKA", "Yunus home torched; four killed in unrest"),
    ("COPENHAGEN", "Denmark OKs Greenland-U.S. Arctic deal"),
    ("SEOUL", "Top court clears ex-PM Han over martial law"),
    ("SILICON VALLEY", "Anthropic's record $81bn IPO opens"),
]


def build():
    page = Page()
    page.y = 18
    page.centred("T H E   W O R L D   I N   O N E   D A Y", "sans_b", 21,
                 RED_RGB, gap_below=13)
    page.rule(weight=3, gap_below=10)
    page.centred("THURSDAY, 19 NOVEMBER 2026", "serif_b", 48, INK_RGB,
                 gap_below=18)
    page.rule(weight=3, gap_below=12)

    # Lead story: full-width photo, big serif headline, deck.
    page.photo(LEAD["photo"], MARGIN, PAGE_W - 2 * MARGIN, 256)
    page.y += 268
    page.y = page.flow_text(LEAD["headline"], "serif_b", 40, INK_RGB,
                            MARGIN, PAGE_W - 2 * MARGIN, 48)
    page.y = page.flow_text(LEAD["deck"], "sans", 20, GREY_RGB,
                            MARGIN, PAGE_W - 2 * MARGIN, 27)
    page.y += 8
    page.rule(weight=2, gap_below=12)

    # Middle row: two photo stories side by side.
    half = (PAGE_W - 2 * MARGIN - 16) // 2
    row_top = page.y
    page.photo(MIDDLE[0]["photo"], MARGIN, half, 140)
    page.photo(MIDDLE[1]["photo"], MARGIN + half + 16, half, 140)
    page.y = row_top + 150
    page.flow_text(MIDDLE[0]["headline"], "sans_b", 22, INK_RGB,
                   MARGIN, half, 28)
    page.flow_text(MIDDLE[0]["deck"], "sans", 16, GREY_RGB,
                   MARGIN, half, 21)
    left_end = page.y
    page.y = row_top + 150
    page.flow_text(MIDDLE[1]["headline"], "sans_b", 22, INK_RGB,
                   MARGIN + half + 16, half, 28)
    page.flow_text(MIDDLE[1]["deck"], "sans", 16, GREY_RGB,
                   MARGIN + half + 16, half, 21)
    right_end = page.y
    page.y = max(left_end, right_end) + 8
    page.rule(weight=2, gap_below=12)

    # Bottom row: text story on the left, one-liners on the right.
    bottom_top = page.y
    page.flow_text(TEXT_STORY["headline"], "sans_b", 20, INK_RGB,
                   MARGIN, half, 26)
    page.flow_text(TEXT_STORY["deck"], "sans", 16, GREY_RGB,
                   MARGIN, half, 21)
    tx = MARGIN + half + 16
    ty = bottom_top
    for place, news in ONE_LINERS:
        label = place + " \u2014 "
        page.pen.text((tx, ty), label, font=typeface("sans_b", 16),
                      fill=RED_RGB)
        offset = page.pen.textlength(label, font=typeface("sans_b", 16))
        page.pen.text((tx + offset, ty), news, font=typeface("sans", 16),
                      fill=INK_RGB)
        ty += 25

    # Footer.
    page.pen.line([MARGIN, PAGE_H - 44, PAGE_W - MARGIN, PAGE_H - 44],
                  fill=INK_RGB, width=3)
    page.pen.text((PAGE_W // 2, PAGE_H - 36),
                  "ONE DAY \u2022 ONE PAGE \u2022 THE WORLD ON THURSDAY 19 NOVEMBER 2026",
                  font=typeface("sans_b", 16), fill=GREY_RGB, anchor="ma")

    out = os.path.join(HERE, "entry.png")
    page.sheet.save(out)
    print("saved %s %s %d bytes" % (out, page.sheet.size,
                                    os.path.getsize(out)))


if __name__ == "__main__":
    build()
