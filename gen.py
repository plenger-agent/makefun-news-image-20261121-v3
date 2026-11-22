#!/usr/bin/env python3
"""
gen.py -- renders entry.png, a one-page broadsheet that squeezes the whole
of Saturday 21 November 2026 into a single 1024x1024 image.

Layout, top to bottom: masthead, UTC timeline, stat strip, three picture-led
front-page stories, six illustrated cards, a ten-item grid, then a world map
beside the "also on Saturday" column. Everything is drawn with Pillow
primitives; no photographs are used.

Run:  python3 gen.py     (writes entry.png next to this file)
"""

import os
from PIL import Image, ImageDraw, ImageFont

# --------------------------------------------------------------------------
# Canvas and palette
# --------------------------------------------------------------------------
SIDE = 1024
PAPER = (247, 242, 231)          # cream newsprint
INK = (18, 22, 34)               # near-black navy ink
NAVY = (16, 34, 64)
RED = (178, 34, 40)
GREY = (92, 92, 88)
RULE = (30, 30, 30)
SEA = (196, 218, 226)
LAND = (232, 213, 163)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

NOTO = "/usr/share/fonts/truetype/noto"

# --------------------------------------------------------------------------
# Regions: nine of them, each with its own colour used across the page
# --------------------------------------------------------------------------
REGIONS = {
    "ME":  ("MIDDLE EAST",    (217, 108, 27)),
    "EU":  ("EUROPE",         (38, 92, 158)),
    "AF":  ("AFRICA",         (166, 124, 0)),
    "NA":  ("NORTH AMERICA",  (125, 60, 152)),
    "LA":  ("LATIN AMERICA",  (30, 132, 73)),
    "SA":  ("SOUTH ASIA",     (194, 24, 91)),
    "EA":  ("EAST ASIA",      (0, 131, 143)),
    "OC":  ("OCEANIA",        (84, 110, 122)),
    "SCI": ("SCIENCE / SPACE", (93, 64, 55)),
}

# --------------------------------------------------------------------------
# The day's stories.  3 leads + 6 cards + 10 grid + 21 also = 40.
# --------------------------------------------------------------------------
LEADS = [
    {
        "scene": "hormuz", "region": "ME", "num": 1,
        "place": "MANAMA - STRAIT OF HORMUZ", "tag": "ONGOING",
        "headline": "Iran strikes Bahrain, tankers hit",
        "dek": "IRGC missiles and drones hit US posts; two tankers ablaze.",
    },
    {
        "scene": "sparta", "region": "EU", "num": 2,
        "place": "GULF OF FINLAND - BALTIC SEA", "tag": "CONFIRMED",
        "headline": "Drones set Russian cargo ship ablaze",
        "dek": "Two drones hit Sparta II; crew safe. Finland blames "
               "Moscow for the attack.",
    },
    {
        "scene": "cop", "region": "EU", "num": 3,
        "place": "ANTALYA - COP31 SUMMIT", "tag": "OVERTIME",
        "headline": "COP31 deadlocked over fossil fuels",
        "dek": "Talks ran into overtime; the draft dropped fossil fuels.",
    },
]

CARDS = [
    {
        "icon": "quake", "region": "EA", "num": 4,
        "place": "BANDA SEA - QUAKE", "tag": "CONFIRMED",
        "headline": "Quake shakes Timor-Leste M6.8",
        "fact": "09:42 UTC, deep; no tsunami threat.",
    },
    {
        "icon": "mercury", "region": "SCI", "num": 5,
        "place": "MERCURY - SCIENCE", "tag": "OFFICIAL",
        "headline": "BepiColombo reaches Mercury",
        "fact": "18:24 UTC, ESA/JAXA twin craft.",
    },
    {
        "icon": "pact", "region": "EA", "num": 6,
        "place": "BRUSSELS - TRADE", "tag": "SIGNED",
        "headline": "EU and Indonesia sign trade pact",
        "fact": "Duties cut on 98% of goods.",
    },
    {
        "icon": "fugitive", "region": "LA", "num": 7,
        "place": "SINALOA - SECURITY", "tag": "CONFIRMED",
        "headline": "Mexico seizes 'El Chapo Isidro'",
        "fact": "FBI most-wanted, held in army raid.",
    },
    {
        "icon": "robots", "region": "EU", "num": 8,
        "place": "GENEVA - AI WEAPONS", "tag": "CONFIRMED",
        "headline": "No treaty on 'killer robots'",
        "fact": "0 binding rules agreed in Geneva.",
    },
    {
        "icon": "boat", "region": "AF", "num": 9,
        "place": "BAYELSA - DISASTER", "tag": "SEARCH ON",
        "headline": "Nigeria funeral boat toll hits 24",
        "fact": "24 bodies found; search goes on.",
    },
]

GRID = [
    ("EU", "DUBLIN", "Ireland edge SA 20-17"),
    ("SA", "WELLINGTON", "India 486-4 v NZ"),
    ("NA", "LAS VEGAS", "Verstappen wins GP"),
    ("NA", "WALL ST", "AI sell-off: correction"),
    ("EU", "PARIS", "82,500 march, sixth Saturday"),
    ("EA", "OSAKA", "BTS take two MAMA prizes"),
    ("OC", "AUCKLAND", "Australia beat NZ 3-1"),
    ("LA", "C. PERU", "M6.7 quake shakes centre"),
    ("ME", "GAZA", "Strike kills boy, 7, medic"),
    ("SA", "MANIPUR", "Liquor toll reaches 16"),
]

ALSO = [
    ("EU", "KYIV", "Bridge toll rises to nine"),
    ("ME", "MANAMA", "Bahrain petitions UN"),
    ("EU", "GENEVA", "Pope writes to robot talks"),
    ("EU", "FRANCE", "Unions call Dec 1 strike"),
    ("EA", "YOGYAKARTA", "Wolbachia cuts dengue"),
    ("OC", "CANBERRA", "47,000 sign sub petition"),
    ("EU", "BARCELONA", "Housing rally in centre"),
    ("EA", "JAKARTA", "Fire kills 3, 36 missing"),
    ("EA", "SUMATRA", "60,000 battle big fires"),
    ("EU", "LONDON", "Record win over All Blacks"),
    ("OC", "COOK ISLANDS", "Cyclone Xavier fades"),
    ("LA", "SANTIAGO", "M4.7 quake in north"),
    ("OC", "SYDNEY", "Cummins keeps captaincy"),
    ("EA", "PONTIANAK", "Flood warning issued"),
    ("OC", "MELBOURNE", "Chaudhary stars at MCG"),
    ("EA", "MANILA", "Musk island claim surfaces"),
    ("EU", "WARSAW", "Russian missiles land"),
    ("NA", "WASHINGTON", "Trump warns AI firms"),
    ("EA", "BIMA", "Ex-drug chief jailed 20 yrs"),
    ("EA", "SHENZHEN", "Leapmotor profit -73%"),
    ("EA", "TIANJIN", "Empty tower nears finish"),
]

STORY_TOTAL = len(LEADS) + len(CARDS) + len(GRID) + len(ALSO)
assert STORY_TOTAL == 40, STORY_TOTAL
assert {s["region"] for s in LEADS + CARDS} | {g[0] for g in GRID} \
    | {a[0] for a in ALSO} == set(REGIONS), "all nine regions must appear"

STATS = [
    ("82,500", "march in Paris in a sixth Saturday of protests"),
    ("$5m", "FBI reward that stood on 'El Chapo Isidro'"),
    ("M6.8", "Banda Sea quake, 09:42 UTC, off Timor-Leste"),
    ("130+", "nations at COP31 climate talks"),
    ("24", "dead in Nigeria's Bayelsa funeral-boat disaster"),
    ("486-4", "India's close-of-play total, Wellington Test"),
]

TIMELINE = [
    ("00:09", "PERU QUAKE", "LA"),
    ("06:50", "SPARTA II STRUCK", "EU"),
    ("09:42", "BANDA SEA QUAKE", "EA"),
    ("13:10", "EU-INDONESIA PACT", "EA"),
    ("18:24", "BEPICOLOMBO AT MERCURY", "SCI"),
    ("20:00", "IRAN STRIKES BAHRAIN", "ME"),
]

# --------------------------------------------------------------------------
# Font helpers
# --------------------------------------------------------------------------
_cache = {}


def F(name, size):
    key = (name, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(os.path.join(NOTO, name), size)
    return _cache[key]


def serif_black(size):  return F("NotoSerifDisplay-Black.ttf", size)
def serif_xbold(size):  return F("NotoSerifDisplay-ExtraBold.ttf", size)
def serif_bold(size):   return F("NotoSerifDisplay-Bold.ttf", size)
def serif_reg(size):    return F("NotoSerif-Regular.ttf", size)
def serif_it(size):     return F("NotoSerif-BoldItalic.ttf", size)
def sans_bold(size):    return F("NotoSansDisplay-Bold.ttf", size)
def sans_reg(size):     return F("NotoSansDisplay-Regular.ttf", size)
def cond_bold(size):    return F("NotoSansDisplay-CondensedBold.ttf", size)
def cond_reg(size):     return F("NotoSansDisplay-Condensed.ttf", size)


def tw(d, text, font):
    return d.textlength(text, font=font)


def wrap(d, text, font, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if tw(d, trial, font) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def centre(d, cx, y, text, font, fill=INK):
    d.text((cx - tw(d, text, font) / 2, y), text, font=font, fill=fill)


def tag_chip(d, x, y, text, fill):
    f = cond_bold(12)
    w = tw(d, text, f) + 12
    d.rectangle([x, y, x + w, y + 17], fill=fill)
    d.text((x + 6, y + 2), text, font=f, fill=(255, 255, 255))
    return w


def num_badge(d, x, y, n, r=13):
    d.ellipse([x, y, x + 2 * r, y + 2 * r], fill=INK)
    f = sans_bold(15)
    s = str(n)
    d.text((x + r - tw(d, s, f) / 2, y + r - 9), s, font=f,
           fill=(255, 255, 255))


# --------------------------------------------------------------------------
# Lead scenes.  Each paints inside the box it is handed.
# --------------------------------------------------------------------------
def flame(d, cx, base, h, w):
    """A layered teardrop flame centred on cx, standing on base."""
    d.polygon([(cx - w, base), (cx - w * 0.28, base - h * 0.55),
               (cx, base - h), (cx + w * 0.28, base - h * 0.55),
               (cx + w, base)], fill=(232, 110, 20))
    d.polygon([(cx - w * 0.55, base), (cx, base - h * 0.62),
               (cx + w * 0.55, base)], fill=(245, 176, 32))
    d.polygon([(cx - w * 0.26, base), (cx, base - h * 0.34),
               (cx + w * 0.26, base)], fill=(252, 226, 120))


def smoke(d, cx, cy, r, tone=120):
    for dx, dy, rr in ((-r, 4, r * 0.8), (0, -r * 0.5, r), (r, 2, r * 0.75),
                       (r * 0.4, -r * 1.1, r * 0.7)):
        d.ellipse([cx + dx - rr, cy + dy - rr, cx + dx + rr, cy + dy + rr],
                  fill=(tone, tone, tone - 6))


def scene_hormuz(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    # Iran shore along the top, Oman shore along the bottom
    d.polygon([(x, y), (x + w * 0.62, y), (x + w * 0.52, y + h * 0.30),
               (x + w * 0.30, y + h * 0.22), (x, y + h * 0.34)], fill=LAND)
    d.polygon([(x + w * 0.30, y + h), (x + w * 0.52, y + h * 0.68),
               (x + w, y + h * 0.78), (x + w, y + h)], fill=LAND)
    f = cond_bold(15)
    d.text((x + 46, y + 8), "I R A N", font=f, fill=(120, 92, 40))
    d.text((x + w * 0.66, y + h - 24), "OMAN", font=f, fill=(120, 92, 40))
    d.text((x + 10, y + h * 0.40), "STRAIT OF\nHORMUZ", font=cond_bold(13),
           fill=(52, 96, 120))
    # tanker mid-channel
    tx, ty = x + w * 0.34, y + h * 0.60
    d.polygon([(tx, ty), (tx + w * 0.42, ty), (tx + w * 0.37, ty + 20),
               (tx + 8, ty + 20)], fill=(24, 30, 44))
    d.rectangle([tx + 4, ty - 7, tx + w * 0.42 - 2, ty], fill=(178, 34, 40))
    d.rectangle([tx + w * 0.33, ty - 24, tx + w * 0.40, ty - 7],
                fill=(240, 238, 230))
    d.rectangle([tx + w * 0.345, ty - 20, tx + w * 0.385, ty - 15],
                fill=(70, 130, 170))
    flame(d, tx + w * 0.13, ty - 6, 44, 13)
    flame(d, tx + w * 0.24, ty - 6, 30, 10)
    smoke(d, tx + w * 0.16, ty - 52, 15)
    # dashed missile arcs dropping from the Iran shore
    for sx, ex in ((0.10, 0.34), (0.24, 0.44)):
        for t in range(0, 11):
            tt = t / 10.0
            px = x + w * (sx + (ex - sx) * tt)
            py = y + h * (0.16 + 0.42 * tt * tt)
            if t % 2 == 0:
                d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
    d.rectangle([x + 10, y + h - 26, x + 128, y + h - 6], fill=RED)
    d.text((x + 17, y + h - 23), "TANKER ON FIRE", font=cond_bold(13),
           fill=(255, 255, 255))
    tag_chip(d, x + w - 118, y + 8, "TRAFFIC HALTED", NAVY)


def scene_sparta(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h * 0.62], fill=(214, 228, 233))
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=(110, 156, 180))
    for i in range(5):  # wave strokes
        wy = y + h * 0.70 + i * 9
        for wx in range(x + 8 + (i % 2) * 22, x + w - 30, 46):
            d.arc([wx, wy, wx + 26, wy + 7], 200, 330, fill=(230, 242, 246),
                  width=2)
    # hull and container stacks
    hx, hy = x + w * 0.10, y + h * 0.60
    hw = w * 0.80
    d.polygon([(hx, hy), (hx + hw, hy), (hx + hw - 18, hy + 22),
               (hx + 14, hy + 22)], fill=(30, 34, 44))
    cols = [(196, 60, 44), (44, 96, 168), (232, 150, 30), (90, 140, 70),
            (140, 70, 150)]
    for i, c in enumerate(cols):
        bx = hx + 16 + i * (hw - 90) / 4.6
        d.rectangle([bx, hy - 34, bx + 34, hy - 4], fill=c)
        if i % 2 == 0:
            d.rectangle([bx, hy - 58, bx + 34, hy - 36], fill=c)
    d.rectangle([hx + hw - 52, hy - 44, hx + hw - 18, hy - 4],
                fill=(238, 236, 228))
    centre(d, hx + hw / 2, hy + 3, "SPARTA II", cond_bold(14),
           fill=(255, 255, 255))
    flame(d, hx + hw * 0.42, hy - 56, 52, 15)
    flame(d, hx + hw * 0.55, hy - 34, 34, 11)
    smoke(d, hx + hw * 0.50, hy - 96, 20, tone=105)
    smoke(d, hx + hw * 0.62, hy - 112, 15, tone=140)
    # two drones, top corners
    for dx, dy in ((x + 34, y + 22), (x + w - 40, y + 18)):
        d.line([dx - 13, dy - 13, dx + 13, dy + 13], fill=INK, width=3)
        d.line([dx - 13, dy + 13, dx + 13, dy - 13], fill=INK, width=3)
        for ox, oy in ((-13, -13), (13, -13), (-13, 13), (13, 13)):
            d.ellipse([dx + ox - 6, dy + oy - 3, dx + ox + 6, dy + oy + 3],
                      outline=INK, width=2)
        d.ellipse([dx - 4, dy - 4, dx + 4, dy + 4], fill=RED)
    d.rectangle([x + 10, y + h - 26, x + 84, y + h - 6], fill=NAVY)
    d.text((x + 17, y + h - 23), "06:50 UTC", font=cond_bold(13),
           fill=(255, 255, 255))


def scene_cop(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 238, 220))
    # summit badge
    d.rectangle([x + 40, y + 12, x + 116, y + 62], fill=(34, 110, 54))
    centre(d, x + 78, y + 18, "COP31", serif_xbold(21), fill=(255, 255, 255))
    centre(d, x + 78, y + 42, "ANTALYA", cond_bold(11), fill=(255, 255, 255))
    # the draft document, fossil-fuel line struck through
    dx, dy = x + 16, y + h * 0.46
    d.rectangle([dx, dy, dx + 138, dy + 82], fill=(253, 252, 246),
                outline=(150, 150, 140))
    d.text((dx + 10, dy + 7), "DRAFT TEXT", font=cond_bold(12), fill=GREY)
    for i in range(3):
        d.line([dx + 10, dy + 30 + i * 10, dx + 118, dy + 30 + i * 10],
               fill=(170, 170, 162), width=3)
    d.text((dx + 10, dy + 60), "fossil fuels", font=serif_it(15), fill=RED)
    d.line([dx + 8, dy + 68, dx + 92, dy + 68], fill=RED, width=3)
    # overtime clock
    cx, cy, r = x + w * 0.66, y + h * 0.36, 34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(253, 252, 246),
              outline=INK, width=3)
    for a in range(0, 360, 90):
        import math
        d.line([cx + (r - 8) * math.cos(math.radians(a)),
                cy + (r - 8) * math.sin(math.radians(a)),
                cx + r * math.cos(math.radians(a)),
                cy + r * math.sin(math.radians(a))], fill=INK, width=2)
    d.line([cx, cy, cx, cy - r + 9], fill=INK, width=3)
    d.line([cx, cy, cx + r - 13, cy + 8], fill=INK, width=3)
    centre(d, cx, cy + r + 6, "OVERTIME", cond_bold(14), fill=RED)
    centre(d, cx, cy + r + 23, "a day past deadline", cond_reg(11), fill=GREY)
    # thermometer at 1.5 degrees
    tx = x + w - 42
    d.rectangle([tx, y + 26, tx + 12, y + h - 44], outline=INK, width=2)
    d.rectangle([tx + 3, y + h - 92, tx + 9, y + h - 47], fill=RED)
    d.ellipse([tx - 6, y + h - 46, tx + 18, y + h - 22], fill=RED)
    centre(d, tx + 6, y + h - 20, "1.5C", cond_bold(13), fill=INK)


SCENES = {"hormuz": scene_hormuz, "sparta": scene_sparta, "cop": scene_cop}


def lead_panel(d, story, x, y, w, h):
    scene_h = int(h * 0.555)
    d.rectangle([x, y, x + w, y + h], outline=RULE, width=2)
    SCENES[story["scene"]](d, x + 2, y + 2, w - 4, scene_h - 2)
    num_badge(d, x + 10, y + 10, story["num"])
    # region bar under the picture
    col = REGIONS[story["region"]][1]
    by = y + scene_h
    d.rectangle([x + 2, by, x + w - 2, by + 19], fill=col)
    d.text((x + 9, by + 3), story["place"], font=cond_bold(13),
           fill=(255, 255, 255))
    tag_chip(d, x + w - 8 - (tw(d, story["tag"], cond_bold(12)) + 12),
             by + 1, story["tag"], INK)
    # headline and dek; shrink the headline a step if it would need
    # a third line, so the text block always stays inside the panel
    hy = by + 24
    size = 31
    lines = wrap(d, story["headline"], serif_black(size), w - 18)
    while len(lines) > 2 and size > 26:
        size -= 1
        lines = wrap(d, story["headline"], serif_black(size), w - 18)
    for line in lines:
        d.text((x + 9, hy), line, font=serif_black(size), fill=INK)
        hy += 34
    for line in wrap(d, story["dek"], serif_reg(15), w - 18):
        d.text((x + 9, hy + 2), line, font=serif_reg(15), fill=(52, 52, 50))
        hy += 16


# --------------------------------------------------------------------------
# Card icons, drawn in a square box
# --------------------------------------------------------------------------
def icon_quake(d, x, y, s):
    cx, cy = x + s / 2, y + s / 2
    for r, col in ((s * 0.46, (232, 130, 40)), (s * 0.32, RED),
                   (s * 0.18, (150, 26, 30))):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=4)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=INK)


def icon_mercury(d, x, y, s):
    d.rounded_rectangle([x, y, x + s, y + s], 8, fill=(24, 28, 52))
    for sx, sy, r in ((0.2, 0.25, 2), (0.8, 0.2, 2), (0.65, 0.75, 2),
                      (0.15, 0.7, 1)):
        d.ellipse([x + s * sx - r, y + s * sy - r, x + s * sx + r,
                   y + s * sy + r], fill=(240, 240, 230))
    cx, cy, r = x + s * 0.42, y + s * 0.55, s * 0.24
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(206, 188, 168))
    d.pieslice([cx - r, cy - r, cx + r, cy + r], 90, 270, fill=(178, 158, 138))
    d.ellipse([cx - r * 0.4, cy - r * 0.5, cx + r * 0.1, cy],
              fill=(160, 140, 118))
    d.ellipse([x + s * 0.06, y + s * 0.30, x + s * 0.94, y + s * 0.80],
              outline=(240, 200, 90), width=2)
    # the twin craft, a body with two panel wings
    px, py = x + s * 0.72, y + s * 0.30
    d.rectangle([px - 12, py - 3, px - 4, py + 3], fill=(90, 130, 200))
    d.rectangle([px + 4, py - 3, px + 12, py + 3], fill=(90, 130, 200))
    d.rectangle([px - 3, py - 5, px + 3, py + 5], fill=(230, 230, 220))


def icon_pact(d, x, y, s):
    # EU flag: blue field, ring of gold stars
    import math
    fx, fy, fw, fh = x + 4, y + 10, s * 0.44, s * 0.52
    d.rectangle([fx, fy, fx + fw, fy + fh], fill=(36, 62, 150))
    for i in range(8):
        a = math.radians(i * 45)
        sx = fx + fw / 2 + math.cos(a) * fw * 0.30
        sy = fy + fh / 2 + math.sin(a) * fh * 0.30
        d.ellipse([sx - 2, sy - 2, sx + 2, sy + 2], fill=(245, 200, 60))
    # Indonesian flag: red over white
    gx = x + s * 0.52
    d.rectangle([gx, fy, gx + fw, fy + fh / 2], fill=(200, 40, 46))
    d.rectangle([gx, fy + fh / 2, gx + fw, fy + fh], fill=(248, 248, 244),
                outline=(180, 180, 172))
    centre(d, x + s / 2, y + s - 18, "CEPA", cond_bold(13), fill=INK)


def icon_fugitive(d, x, y, s):
    cx, cy = x + s / 2, y + s * 0.42
    d.ellipse([cx - 20, cy - 20, cx + 20, cy + 20], fill=(216, 164, 32))
    import math
    pts = []
    for i in range(10):
        a = math.radians(i * 36 - 90)
        r = 13 if i % 2 == 0 else 6
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    d.polygon(pts, fill=(250, 226, 130))
    d.ellipse([x + s * 0.22, y + s * 0.66, x + s * 0.50, y + s * 0.92],
              outline=INK, width=4)
    d.ellipse([x + s * 0.50, y + s * 0.66, x + s * 0.78, y + s * 0.92],
              outline=INK, width=4)


def icon_robots(d, x, y, s):
    hx, hy = x + s * 0.22, y + s * 0.24
    d.line([hx + 20, hy, hx + 20, hy - 10], fill=INK, width=3)
    d.ellipse([hx + 16, hy - 15, hx + 24, hy - 7], fill=RED)
    d.rounded_rectangle([hx, hy, hx + 40, hy + 34], 7, fill=(150, 158, 168),
                        outline=INK, width=2)
    d.ellipse([hx + 8, hy + 11, hx + 16, hy + 19], fill=INK)
    d.ellipse([hx + 24, hy + 11, hx + 32, hy + 19], fill=INK)
    d.line([hx + 10, hy + 27, hx + 30, hy + 27], fill=INK, width=2)
    # gavel beside the head
    gx, gy = x + s * 0.60, y + s * 0.52
    d.rectangle([gx, gy, gx + 26, gy + 11], fill=(146, 102, 52))
    d.line([gx + 20, gy + 8, gx + 34, gy + 24], fill=(110, 76, 38), width=5)
    d.line([x + s * 0.14, y + s * 0.86, x + s * 0.86, y + s * 0.86],
           fill=INK, width=3)


def icon_boat(d, x, y, s):
    by = y + s * 0.52
    d.polygon([(x + 8, by), (x + s - 8, by), (x + s - 18, by + 14),
               (x + 18, by + 14)], fill=(120, 78, 40))
    d.line([x + s / 2, by, x + s / 2, by - 22], fill=INK, width=3)
    d.polygon([(x + s / 2, by - 22), (x + s / 2, by - 4),
               (x + s / 2 + 13, by - 4)], fill=(238, 236, 228))
    for i in range(3):
        wy = by + 20 + i * 7
        for wx in range(x + 4, x + s - 20, 30):
            d.arc([wx, wy, wx + 20, wy + 6], 200, 330, fill=(70, 130, 170),
                  width=2)
    d.ellipse([x + s - 24, y + 4, x + s - 6, y + 22], outline=RED, width=3)
    d.line([x + s - 15, y + 8, x + s - 15, y + 18], fill=RED, width=3)
    d.line([x + s - 20, y + 13, x + s - 10, y + 13], fill=RED, width=3)


ICONS = {"quake": icon_quake, "mercury": icon_mercury, "pact": icon_pact,
         "fugitive": icon_fugitive, "robots": icon_robots, "boat": icon_boat}


def card(d, story, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], outline=RULE, width=2)
    d.rectangle([x + 2, y + 2, x + 84, y + h - 2], fill=(240, 234, 218))
    ICONS[story["icon"]](d, x + 8, y + (h - 68) / 2, 68)
    num_badge(d, x + 6, y + 6, story["num"], r=11)
    tx = x + 92
    col = REGIONS[story["region"]][1]
    d.rectangle([tx, y + 7, tx + 7, y + 20], fill=col)
    d.text((tx + 12, y + 6), story["place"], font=cond_bold(13), fill=INK)
    tag_chip(d, x + w - 8 - (tw(d, story["tag"], cond_bold(12)) + 12),
             y + 5, story["tag"], INK)
    hy = y + 23
    for line in wrap(d, story["headline"], serif_bold(21), w - 104):
        d.text((tx, hy), line, font=serif_bold(21), fill=INK)
        hy += 21
    for line in wrap(d, story["fact"], sans_reg(13), w - 104):
        d.text((tx, hy + 1), line, font=sans_reg(13), fill=(52, 52, 50))
        hy += 16


# --------------------------------------------------------------------------
# World map: simplified coastline polygons on an equirectangular grid,
# lat +78 to -58, with graticule lines and numbered story pins.


# --------------------------------------------------------------------------
# World map: simplified coastline polygons on an equirectangular grid,
# lat +74 to -48, with graticule lines and numbered story pins.
# --------------------------------------------------------------------------
def _poly(d, pts, proj, fill):
    d.polygon([proj(lon, lat) for lon, lat in pts], fill=fill)


CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69), (-86, 66),
     (-82, 60), (-88, 56), (-92, 57), (-90, 51), (-84, 50), (-79, 48),
     (-76, 44), (-70, 44), (-72, 40), (-75, 37), (-76, 34), (-80, 31),
     (-81, 25), (-84, 29), (-89, 29), (-94, 29), (-97, 25), (-97, 21),
     (-94, 18), (-90, 15), (-84, 10), (-79, 9), (-84, 12), (-90, 14),
     (-95, 16), (-100, 17), (-104, 19), (-108, 22), (-112, 27), (-115, 31),
     (-119, 34), (-123, 39), (-124, 47), (-131, 55), (-145, 60), (-160, 59),
     (-166, 61)],
    # South America
    [(-79, 9), (-72, 12), (-64, 10), (-56, 6), (-51, 1), (-44, -3),
     (-35, -8), (-38, -14), (-40, -21), (-47, -26), (-55, -33), (-61, -38),
     (-63, -41), (-66, -46), (-67, -51), (-69, -54), (-71, -54), (-73, -47),
     (-73, -38), (-71, -30), (-70, -20), (-74, -15), (-78, -8), (-81, -4),
     (-80, 1), (-77, 4), (-78, 7)],
    # Europe mainland
    [(-9, 43), (-9, 37), (-6, 36), (0, 39), (3, 42), (7, 44), (10, 44),
     (8, 44), (4, 46), (-1, 46), (-2, 49), (0, 50), (4, 52), (7, 54),
     (8, 56), (10, 58), (18, 57), (20, 55), (24, 58), (28, 60), (25, 61),
     (21, 62), (18, 66), (16, 68), (20, 70), (28, 71), (31, 70), (29, 66),
     (25, 65), (23, 61), (30, 59), (28, 56), (30, 50), (28, 45), (24, 44),
     (20, 44), (19, 42), (15, 40), (16, 38), (13, 41), (10, 44)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 55), (-3, 57), (-2, 58), (-1, 54), (1, 52),
     (1, 51)],
    # Africa
    [(-6, 35), (0, 36), (10, 37), (11, 34), (20, 32), (30, 31), (33, 30),
     (35, 27), (38, 21), (40, 15), (43, 12), (48, 11), (51, 12), (44, 4),
     (41, -3), (40, -11), (37, -19), (35, -25), (32, -29), (27, -33),
     (20, -35), (18, -33), (15, -28), (12, -18), (13, -12), (9, -4),
     (9, 1), (6, 4), (-2, 5), (-8, 5), (-13, 8), (-17, 13), (-16, 18),
     (-15, 25), (-13, 28), (-9, 32)],
    # Asia (Arabia to Siberia, India and SE Asia included)
    [(28, 41), (36, 36), (36, 33), (34, 29), (39, 21), (43, 12), (45, 12),
     (52, 15), (55, 17), (58, 19), (59, 22), (57, 24), (52, 25), (50, 27),
     (49, 29), (51, 29), (54, 26), (57, 27), (61, 25), (66, 25), (70, 22),
     (72, 20), (73, 16), (75, 13), (77, 8), (80, 10), (80, 14), (84, 18),
     (88, 22), (91, 22), (92, 16), (95, 16), (98, 14), (99, 9), (101, 5),
     (103, 1), (104, 3), (101, 8), (99, 12), (100, 14), (105, 9), (107, 12),
     (109, 15), (106, 20), (109, 22), (114, 22), (118, 25), (121, 28),
     (122, 31), (120, 34), (122, 37), (126, 39), (122, 41), (127, 41),
     (130, 42), (133, 44), (137, 45), (141, 48), (142, 52), (141, 56),
     (137, 56), (142, 60), (150, 61), (157, 63), (163, 66), (170, 67),
     (178, 66), (178, 63), (170, 61), (162, 59), (158, 53), (156, 51),
     (145, 50), (138, 47), (132, 44), (128, 42), (122, 39), (120, 35),
     (110, 36), (100, 38), (90, 42), (82, 45), (75, 46), (68, 48),
     (60, 50), (55, 52), (50, 55), (45, 58), (40, 62), (36, 60), (33, 55),
     (30, 48), (28, 44)],
    # Indonesia: Sumatra, Borneo, Java, Sulawesi, New Guinea
    [(95, 5), (99, 2), (103, -3), (106, -6), (103, -5), (99, 1), (96, 4)],
    [(109, 1), (111, 3), (114, 4), (117, 6), (119, 3), (118, -1), (115, -3),
     (111, -3), (109, -1)],
    [(106, -6), (110, -7), (114, -8), (114, -9), (108, -8), (106, -7)],
    [(119, 1), (121, 1), (123, 0), (121, -2), (120, -4), (119, -2)],
    [(131, -1), (136, -2), (141, -3), (146, -6), (150, -9), (148, -10),
     (143, -8), (137, -4), (132, -3)],
    # Japan
    [(130, 31), (132, 33), (135, 34), (138, 35), (140, 36), (141, 40),
     (142, 44), (143, 43), (141, 39), (139, 35), (136, 34), (132, 32)],
    # Australia and New Zealand
    [(113, -22), (114, -29), (115, -34), (119, -35), (125, -33), (130, -32),
     (133, -32), (136, -35), (138, -36), (141, -38), (145, -38), (148, -38),
     (150, -37), (153, -31), (153, -26), (151, -23), (148, -20), (146, -19),
     (143, -15), (142, -11), (141, -14), (140, -18), (137, -16), (136, -12),
     (133, -11), (130, -13), (126, -14), (122, -17), (118, -20), (114, -21)],
    [(167, -46), (170, -43), (172, -41), (174, -39), (177, -38), (178, -37),
     (175, -39), (173, -41), (171, -44), (168, -47)],
]

# story pins: (story number, lon, lat, region)
PINS = [
    (1, 56, 26, "ME"), (2, 27, 60, "EU"), (3, 31, 37, "EU"),
    (4, 128, -8, "EA"), (6, 107, -6, "EA"), (7, -107, 25, "LA"),
    (8, 6, 46, "EU"), (9, 6, 5, "AF"), (10, -6, 53, "EU"),
    (11, 175, -41, "OC"), (12, -115, 36, "NA"), (14, 2, 49, "EU"),
    (15, 139, 35, "EA"), (16, 175, -37, "OC"), (17, -75, -9, "LA"),
    (18, 34, 31, "ME"),
]


def world_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(233, 240, 242),
                outline=RULE, width=2)

    def proj(lon, lat):
        return (x + (lon + 180) / 360.0 * w,
                y + (74 - lat) / 122.0 * h)

    # graticule every 30 degrees
    for lon in range(-150, 180, 30):
        gx, _ = proj(lon, 0)
        d.line([gx, y + 3, gx, y + h - 3], fill=(205, 217, 221), width=1)
    for lat in range(-30, 75, 30):
        _, gy = proj(0, lat)
        d.line([x + 3, gy, x + w - 3, gy], fill=(205, 217, 221), width=1)
    land = (203, 192, 152)
    for pts in CONTINENTS:
        _poly(d, pts, proj, land)
    # numbered pins in region colours
    for num, lon, lat, reg in PINS:
        px, py = proj(lon, lat)
        col = REGIONS[reg][1]
        r = 8
        d.ellipse([px - r, py - r, px + r, py + r], fill=col,
                  outline=(255, 255, 255), width=2)
        f = sans_bold(10)
        s = str(num)
        d.text((px - tw(d, s, f) / 2, py - 6), s, font=f,
               fill=(255, 255, 255))


# --------------------------------------------------------------------------
# Page assembly.  Vertical budget (1024px): masthead to y=124, timeline to
# 178, stats to 240, leads 252-540, cards 548-716, bottom band 724-990,
# footer at 994.
# --------------------------------------------------------------------------
MX = 12                      # side margin
CW = SIDE - 2 * MX           # content width
WARNINGS = []


def masthead(d):
    d.text((MX, 6), "THE WORLD IN ONE DAY", font=sans_bold(15), fill=INK)
    centre(d, SIDE / 2, 6, "DAY 325 OF 2026", sans_bold(15), RED)
    r = "ALL TIMES UTC - RANKED BY CONSEQUENCE"
    d.text((SIDE - MX - tw(d, r, sans_bold(15)), 6), r, font=sans_bold(15),
           fill=INK)
    d.line([MX, 26, SIDE - MX, 26], fill=RULE, width=3)
    centre(d, SIDE / 2, 31, "Saturday 21 November 2026", serif_black(58))
    d.line([MX, 96, SIDE - MX, 96], fill=RULE, width=2)
    centre(d, SIDE / 2, 102,
           "%d STORIES - 9 REGIONS - EVERY ONE DATED SATURDAY "
           "21 NOVEMBER 2026" % STORY_TOTAL, sans_bold(19), RED)


def timeline(d):
    x0, x1, axis = MX + 6, SIDE - MX - 6, 146
    d.line([x0, axis, x1, axis], fill=INK, width=2)
    for hr in range(0, 25, 4):
        tx = x0 + (x1 - x0) * hr / 24.0
        d.line([tx, axis - 4, tx, axis + 4], fill=INK, width=2)
        centre(d, tx, axis + 6, "%02d" % hr, cond_reg(10), GREY)
    for i, (clock, label, reg) in enumerate(TIMELINE):
        hh, mm = int(clock[:2]), int(clock[3:])
        tx = x0 + (x1 - x0) * (hh + mm / 60.0) / 24.0
        col = REGIONS[reg][1]
        d.ellipse([tx - 5, axis - 5, tx + 5, axis + 5], fill=col)
        text = "%s %s" % (clock, label)
        f = cond_bold(12)
        lx = min(max(tx - tw(d, text, f) / 2, MX), SIDE - MX - tw(d, text, f))
        d.text((lx, 130 if i % 2 == 0 else 164), text, font=f, fill=INK)


def stat_strip(d):
    colw = CW / 6.0
    for i, (big, small) in enumerate(STATS):
        cx = MX + i * colw
        if i:
            d.line([cx, 190, cx, 232], fill=(190, 184, 168), width=1)
        centre(d, cx + colw / 2, 188, big, serif_black(26), INK)
        for j, line in enumerate(wrap(d, small, cond_reg(11), colw - 12)[:2]):
            centre(d, cx + colw / 2, 219 + j * 12, line, cond_reg(11), GREY)


def section_head(d, x, y, title, note=None):
    d.text((x, y), title, font=sans_bold(15), fill=INK)
    if note:
        d.text((x + tw(d, title, sans_bold(15)) + 10, y + 2), note,
               font=cond_reg(12), fill=RED)


def build():
    img = Image.new("RGB", (SIDE, SIDE), PAPER)
    d = ImageDraw.Draw(img)
    lw = (CW - 16) // 3

    masthead(d)
    timeline(d)
    d.line([MX, 182, SIDE - MX, 182], fill=RULE, width=2)
    stat_strip(d)
    d.line([MX, 246, SIDE - MX, 246], fill=RULE, width=2)

    # three picture-first leads
    for i, story in enumerate(LEADS):
        lead_panel(d, story, MX + i * (lw + 8), 252, lw, 288)

    # six illustrated cards, two rows of three
    for i, story in enumerate(CARDS):
        card(d, story, MX + (i % 3) * (lw + 8), 546 + (i // 3) * 90, lw, 86)

    # bottom band, left column: the day in ten, then the map
    section_head(d, MX, 724, "THE DAY IN TEN", "ten more, a line each")
    for i, (reg, place, head) in enumerate(GRID):
        gx = MX + (i // 5) * 249
        yy = 748 + (i % 5) * 17
        d.rectangle([gx, yy + 3, gx + 10, yy + 13], fill=REGIONS[reg][1])
        d.text((gx + 16, yy), place, font=cond_bold(15), fill=INK)
        d.text((gx + 16 + tw(d, place, cond_bold(15)) + 5, yy), "- " + head,
               font=cond_reg(15), fill=(52, 52, 50))
        wline = 16 + tw(d, place, cond_bold(15)) + 5 \
            + tw(d, "- " + head, cond_reg(15))
        if wline > 243:
            WARNINGS.append("grid overflow %.0f: %s" % (wline, place))
    section_head(d, MX, 845, "WHERE IT HAPPENED", "pins = story numbers")
    world_map(d, MX, 867, 492, 119)

    # bottom band, right column: also on Saturday, then the region legend
    ax = MX + 492 + 16
    section_head(d, ax, 724, "ALSO ON SATURDAY", "21 more stories")
    for i, (reg, place, head) in enumerate(ALSO):
        gx = ax + (i // 11) * 249
        yy = 748 + (i % 11) * 17.5
        d.ellipse([gx, yy + 4, gx + 7, yy + 11], fill=REGIONS[reg][1])
        line = "%s - %s" % (place, head)
        d.text((gx + 12, yy), line, font=cond_reg(15), fill=(40, 40, 38))
        if 12 + tw(d, line, cond_reg(15)) > 243:
            WARNINGS.append("also overflow: %s" % line)
    d.text((ax, 940), "NINE REGIONS", font=sans_bold(13), fill=INK)
    d.text((ax + tw(d, "NINE REGIONS", sans_bold(13)) + 10, 942),
           "every colour on this page", font=cond_reg(12), fill=RED)
    names = [(REGIONS[k][0], REGIONS[k][1]) for k in
             ("ME", "EU", "AF", "NA", "LA", "SA", "EA", "OC", "SCI")]
    for i, (name, col) in enumerate(names):
        gx = ax + (i % 5) * 99
        yy = 960 + (i // 5) * 16
        d.rectangle([gx, yy + 2, gx + 9, yy + 11], fill=col)
        d.text((gx + 14, yy), name, font=cond_bold(11), fill=INK)

    d.line([MX, 994, SIDE - MX, 994], fill=RULE, width=2)
    centre(d, SIDE / 2, 999,
           "DATE CHECK - Every story above was reported on Saturday "
           "21 November 2026 (UTC), as the named outlets reported it. "
           "Sources: Reuters - AP - AFP - ESA - USGS - GFZ - NEMA.",
           cond_reg(12), GREY)

    img.save(OUT, optimize=True)
    for wtext in WARNINGS:
        print("WARN:", wtext)
    print("wrote", OUT, os.path.getsize(OUT), "bytes;",
          STORY_TOTAL, "stories,", len(REGIONS), "regions")


if __name__ == "__main__":
    build()
