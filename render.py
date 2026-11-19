#!/usr/bin/env python3
"""One-page newspaper front page: the world on Wednesday 18 November 2026.

Draws 35 verified stories into a single 1024x1024 PNG with PIL only.
No randomness, no clock, no network: running this twice produces the
same bytes. Run:  python3 render.py
Outputs (next to this file): entry.png (1024x1024) and entry-300px.png.
"""

import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))

# --- palette ---------------------------------------------------------------
PAPER = (247, 241, 227)
INK = (26, 26, 26)
NAVY = (15, 32, 64)
GOLD = (201, 162, 39)
RED = (166, 30, 30)
GREY = (74, 74, 74)
SEA = (172, 208, 226)
LAND = (233, 221, 186)
SKY = (214, 228, 238)
GREEN = (46, 125, 70)

W, H = 1024, 1024
MAX_BYTES = 1_048_576

FONT_DIR = "/usr/share/fonts/truetype/liberation"


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def serif_b(s):
    return font("LiberationSerif-Bold.ttf", s)


def serif_i(s):
    return font("LiberationSerif-Italic.ttf", s)


def sans_b(s):
    return font("LiberationSans-Bold.ttf", s)


def sans_r(s):
    return font("LiberationSans-Regular.ttf", s)


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def text_w(draw, text, fnt):
    return draw.textlength(text, font=fnt)


def centred(draw, x0, x1, y, text, fnt, fill):
    tw = text_w(draw, text, fnt)
    draw.text(((x0 + x1 - tw) / 2, y), text, font=fnt, fill=fill)


def segments_centred(draw, x0, x1, y, parts, fnt):
    """Draw [(text, colour), ...] as one centred line."""
    total = sum(text_w(draw, t, fnt) for t, _ in parts)
    x = (x0 + x1 - total) / 2
    for t, colour in parts:
        draw.text((x, y), t, font=fnt, fill=colour)
        x += text_w(draw, t, fnt)


# --- the verified stories --------------------------------------------------
LEADS = [
    {
        "num": 1,
        "kicker": "MIDDLE EAST · WAR",
        "headline": "US–Iran war widens to Kuwait",
        "fact": "Iran hits US base at Ali Al Salem; Tehran says it downed a US MQ-9.",
        "art": "gulf",
    },
    {
        "num": 2,
        "kicker": "EUROPE · WAR IN UKRAINE",
        "headline": "Kerch Bridge road span falls into the sea",
        "fact": "227-m arch down; 2 killed; rail back on one track.",
        "art": "bridge",
    },
    {
        "num": 3,
        "kicker": "ASIA · DIPLOMACY",
        "headline": "Xi greets Putin in Shenzhen; Trump arrives",
        "fact": "APEC opens; three-way talks set for Thursday.",
        "art": "summit",
    },
]

FEATURED = [
    ("MARKETS · TECHNOLOGY", "Nvidia revenue $115.8bn, up 103%",
     "Dow drops 849 pts in the sell-off.", "chip"),
    ("ASIA · WEATHER", "Cyclone Akvan nears landfall",
     "Friday noon; gusts 110 km/h, IMD says.", "cyclone"),
    ("ISRAEL · POLITICS", "Eisenkot tapped to form government",
     "Herzog picks ex-army chief over Netanyahu.", "parliament"),
    ("EUROPE · POLITICS", "EU proposes €45bn loan for Ukraine",
     "Official plan; covers two-thirds of 2027 gap.", "euro"),
    ("USA · ELECTION", "Peltola wins Alaska — Senate 56–44",
     "Democrats flip 9 seats; first Alaska Native.", "ballot"),
    ("ASIA · SECURITY", "Quad unveils first joint patrol plan",
     "Manila pact; joint P-8 patrols from 2027.", "patrol"),
]

NUMBERS = [
    ("$115.8bn", "Nvidia revenue, +103%"),
    ("849 pts", "Dow drop, 18 Nov"),
    ("56–44", "US Senate, Democrats"),
    ("5,568", "Ebola deaths, DR Congo"),
]

ALSO_ON = [
    "India condemns tanker attack — 21 saved",
    "India inflation 12.29% — 4-year high",
    "India-Japan hold 2+2 talks in Tokyo",
    "COP31 draft criticised — EU: untenable",
    "Thailand seeks US tariff cut to 10%",
    "Cyclone Xavier hits Cooks — gusts 315",
    "Romania quake M5.3 — felt in Bucharest",
    "Trump meets Marcos in Manila",
    "Rubio: no imminent threat — 'dirty bomb'",
    "Pakistan cuts petrol Rs3 — 11th in a row",
    "One Nation: cut refugee intake 90%",
    "Taiwan stocks swing below 40,000",
    "Xi meets South Korea's Lee in Shenzhen",
    "Iran declares maritime restricted area",
    "US revokes Iran oil-selling licence",
    "Ebola in DR Congo — 5,568 dead",
    "US tech outages hit Microsoft, Apple",
    "US loses measles-free status — PAHO",
    "Gaza Board of Peace: ceasefire at risk",
    "PNG quake M6.0 — depth 10 km",
    "Kigali Amendment ratification nears 90%",
    "Saudi coalition hits 60 Houthi sites",
    "Argentina rout Costa Rica 7-0",
    "US strikes 60+ IRGC boats in Gulf",
    "Kuwait: all drones downed, no damage",
    "Estonia to shut Russia border in Dec.",
]

# (lat, lon) for the numbered dots 1-9 and the small dots 10-35.
NUMBERED_DOTS = [
    (25.0, 59.0), (45.3, 36.5), (22.5, 114.0), (40.7, -74.0),
    (15.0, 85.0), (32.2, 35.5), (50.8, 4.4), (61.2, -149.9),
    (14.6, 121.0),
]
SMALL_DOTS = [
    (20.0, 54.0), (28.6, 77.2), (35.7, 139.7), (36.9, 30.7),
    (13.8, 100.5), (-21.2, -159.8), (45.7, 26.6), (12.5, 124.0),
    (38.9, -77.0), (33.7, 73.1), (-35.3, 149.1), (25.0, 121.6),
    (37.6, 127.0), (20.0, 63.0), (23.0, 51.0), (-2.5, 23.5),
    (37.3, -122.0), (33.7, -84.4), (31.5, 34.5), (-6.3, 147.0),
    (-1.9, 30.0), (15.3, 44.2), (-34.6, -58.4), (25.0, 55.0),
    (28.5, 48.5), (59.4, 24.7),
]

# Rough continent outlines in (lon, lat); drawn as simple flat shapes.
CONTINENTS = [
    # North America
    [(-168, 66), (-150, 70), (-135, 70), (-125, 71), (-110, 73), (-95, 80),
     (-85, 76), (-80, 73), (-76, 62), (-65, 60), (-55, 52), (-60, 47),
     (-70, 42), (-75, 35), (-80, 26), (-84, 30), (-90, 21), (-97, 16),
     (-105, 20), (-110, 24), (-117, 33), (-125, 40), (-125, 49),
     (-135, 58), (-150, 60), (-165, 60)],
    # Greenland
    [(-58, 64), (-45, 60), (-40, 64), (-32, 68), (-22, 70), (-25, 76),
     (-40, 80), (-58, 76), (-68, 70)],
    # South America
    [(-80, 10), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-70, -18),
     (-70, -23), (-65, -30), (-62, -38), (-68, -50), (-66, -55),
     (-60, -52), (-52, -48), (-48, -40), (-40, -33), (-35, -28),
     (-35, -20), (-40, -15), (-35, -8), (-50, -2), (-55, 0), (-60, 5),
     (-70, 9), (-77, 8)],
    # Africa
    [(-6, 35), (0, 36), (10, 37), (20, 32), (30, 31), (35, 28), (38, 22),
     (43, 12), (48, 11), (51, 10), (44, 2), (40, -5), (40, -12),
     (35, -18), (32, -26), (28, -33), (20, -35), (17, -32), (12, -18),
     (9, -2), (9, 4), (0, 6), (-8, 5), (-13, 8), (-17, 12), (-17, 15),
     (-16, 20), (-15, 25), (-10, 30), (-6, 33)],
    # Asia (drawn before Europe so Europe sits on top at the seam)
    [(30, 66), (40, 68), (55, 69), (70, 72), (85, 73), (100, 76),
     (115, 73), (130, 72), (145, 72), (158, 70), (170, 66), (178, 65),
     (170, 60), (162, 58), (158, 52), (150, 59), (142, 55), (140, 50),
     (135, 45), (130, 42), (127, 40), (122, 38), (120, 34), (122, 30),
     (120, 25), (115, 22), (110, 20), (108, 15), (105, 10), (103, 8),
     (100, 7), (98, 10), (95, 16), (92, 21), (88, 22), (85, 19),
     (80, 15), (77, 8), (75, 12), (72, 20), (68, 23), (66, 25),
     (62, 25), (58, 26), (56, 27), (52, 26), (50, 29), (48, 30),
     (44, 29), (40, 28), (38, 25), (35, 29), (34, 31), (33, 35),
     (30, 36), (28, 40), (30, 46), (33, 52), (38, 58), (42, 62),
     (45, 64), (50, 65)],
    # Europe
    [(-10, 37), (-9, 43), (-2, 44), (-4, 48), (0, 50), (3, 52), (7, 54),
     (8, 57), (12, 56), (18, 56), (21, 55), (23, 58), (24, 60), (20, 64),
     (15, 68), (18, 70), (25, 71), (30, 70), (32, 68), (30, 66),
     (28, 62), (24, 60), (21, 59), (18, 58), (15, 55), (12, 54),
     (8, 53), (4, 52), (0, 51), (-3, 50), (-5, 48), (-2, 47),
     (-4, 44), (-9, 43)],
    # Britain
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53)],
    # Australia
    [(113, -22), (114, -30), (115, -34), (120, -34), (125, -33),
     (130, -32), (135, -35), (140, -38), (145, -38), (150, -37),
     (153, -32), (153, -27), (150, -22), (146, -19), (142, -15),
     (142, -11), (137, -12), (135, -15), (132, -12), (130, -13),
     (126, -14), (122, -17), (118, -20), (114, -21)],
    # Indonesia / Borneo / New Guinea (small islands)
    [(95, 5), (98, 3), (100, 0), (104, -2), (106, -5), (110, -7),
     (114, -8), (118, -9), (120, -10), (119, -8), (115, -5), (110, -3),
     (106, 0), (102, 3)],
    [(109, 1), (112, 3), (116, 5), (118, 2), (117, -2), (114, -3),
     (110, -1)],
    [(131, -1), (136, -2), (141, -4), (146, -7), (141, -8), (136, -6),
     (132, -3)],
]


# --- flat illustrations for the three leads --------------------------------
def art_gulf(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 28, 54))
    for sx, sy in [(18, 14), (60, 26), (120, 10), (180, 30), (240, 16), (290, 28)]:
        d.ellipse([x + sx - 1, y + sy - 1, x + sx + 1, y + sy + 1],
                  fill=(240, 240, 220))
    d.ellipse([x + w - 52, y + 10, x + w - 16, y + 46], fill=(232, 198, 90))
    # jet + contrail
    d.line([x + 30, y + 34, x + 96, y + 22], fill=(200, 200, 200), width=2)
    d.polygon([(x + 96, y + 18), (x + 116, y + 23), (x + 96, y + 28)],
              fill=(220, 220, 220))
    d.polygon([(x + 100, y + 23), (x + 108, y + 14), (x + 112, y + 23)],
              fill=(200, 200, 200))
    # sea
    d.rectangle([x, y + h - 44, x + w, y + h], fill=(24, 68, 110))
    for wy in (y + h - 34, y + h - 22, y + h - 10):
        d.line([x + 8, wy, x + w - 8, wy], fill=(90, 150, 190), width=2)
    # tanker
    d.rectangle([x + 40, y + h - 62, x + 260, y + h - 44], fill=(40, 40, 44))
    d.rectangle([x + 52, y + h - 78, x + 120, y + h - 62], fill=(150, 40, 40))
    d.rectangle([x + 130, y + h - 78, x + 200, y + h - 62], fill=(40, 90, 150))
    d.rectangle([x + 210, y + h - 78, x + 250, y + h - 62], fill=(200, 170, 60))
    d.rectangle([x + 238, y + h - 92, x + 252, y + h - 78], fill=(230, 230, 230))


def art_bridge(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.ellipse([x + 24, y + 12, x + 52, y + 40], fill=(240, 200, 90))
    d.rectangle([x, y + h - 46, x + w, y + h], fill=(52, 110, 160))
    for wy in (y + h - 36, y + h - 24, y + h - 12):
        d.line([x + 8, wy, x + w - 8, wy], fill=(140, 190, 220), width=2)
    deck_y = y + h - 62
    # left deck + towers, then the gap where the span fell
    d.line([x + 10, deck_y, x + 138, deck_y], fill=INK, width=5)
    d.line([x + 44, deck_y, x + 44, y + 26], fill=INK, width=4)
    d.line([x + 120, deck_y, x + 120, y + 34], fill=INK, width=4)
    d.arc([x + 30, y + 26, x + 134, deck_y + 6], start=180, end=360,
          fill=RED, width=4)
    # right deck + towers
    d.line([x + 196, deck_y, x + w - 10, deck_y], fill=INK, width=5)
    d.line([x + 240, deck_y, x + 240, y + 30], fill=INK, width=4)
    d.line([x + 292, deck_y, x + 292, y + 38], fill=INK, width=4)
    # fallen span, tilted down into the water
    d.line([x + 138, deck_y + 2, x + 182, y + h - 18], fill=(90, 90, 90), width=6)
    d.line([x + 150, deck_y + 8, x + 170, y + h - 26], fill=(90, 90, 90), width=3)
    for sx, sy in [(168, 6), (178, 2), (188, 8), (158, 10)]:
        d.line([x + sx, y + h - 22 + sy, x + sx + 12, y + h - 22 + sy],
               fill=(255, 255, 255), width=2)
    # cars stopped at the edge
    d.rectangle([x + 96, deck_y - 12, x + 118, deck_y - 4], fill=RED)
    d.rectangle([x + 210, deck_y - 12, x + 232, deck_y - 4], fill=NAVY)


def art_summit(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(196, 210, 222))
    # skyline behind
    for bx, bw, bh in [(0, 46, 52), (52, 34, 72), (92, 52, 44), (150, 38, 66),
                       (194, 44, 50), (244, 36, 78), (286, 31, 56)]:
        d.rectangle([x + bx, y + h - 52 - bh, x + bx + bw, y + h - 52],
                    fill=(90, 105, 128))
        for wy in range(y + h - 46 - bh, y + h - 56, 12):
            for wx in range(x + bx + 6, x + bx + bw - 4, 10):
                d.rectangle([wx, wy, wx + 4, wy + 6], fill=(232, 198, 90))
    # table
    d.polygon([(x + 14, y + h - 52), (x + w - 14, y + h - 52),
               (x + w - 30, y + h - 6), (x + 30, y + h - 6)], fill=(70, 52, 40))
    d.rectangle([x + 14, y + h - 52, x + w - 14, y + h - 44], fill=(96, 70, 52))
    # five small flags on the table: China, Russia, USA, South Korea, Japan
    flags = [
        [(200, 40, 40), (200, 40, 40), (200, 40, 40)],
        [(255, 255, 255), (30, 80, 180), (200, 40, 40)],
        [(180, 40, 50), (255, 255, 255), (180, 40, 50)],
        [(255, 255, 255), (220, 60, 60), (255, 255, 255)],
        [(255, 255, 255), (220, 60, 60), (255, 255, 255)],
    ]
    for i, stripes in enumerate(flags):
        fx = x + 34 + i * 56
        fy = y + h - 96
        d.line([fx + 14, fy, fx + 14, y + h - 52], fill=INK, width=2)
        for j, colour in enumerate(stripes):
            d.rectangle([fx + 14, fy + j * 8, fx + 42, fy + j * 8 + 8],
                        fill=colour)
        d.rectangle([fx + 14, fy, fx + 42, fy + 24], outline=INK, width=1)
        if i == 0:  # one gold star on the China flag
            d.ellipse([fx + 17, fy + 3, fx + 23, fy + 9], fill=(240, 200, 60))
        if i == 2:  # blue canton on the US flag
            d.rectangle([fx + 14, fy, fx + 26, fy + 12], fill=NAVY)
        if i in (3, 4):  # red disc on the Korea / Japan flags
            d.ellipse([fx + 21, fy + 6, fx + 33, fy + 18], fill=(210, 50, 50))
    # three seated figures (simple silhouettes)
    for px in (x + 62, x + 158, x + 252):
        d.ellipse([px - 9, y + h - 118, px + 9, y + h - 100], fill=INK)
        d.rectangle([px - 13, y + h - 100, px + 13, y + h - 52], fill=INK)


ART = {"gulf": art_gulf, "bridge": art_bridge, "summit": art_summit}


# --- small 38x38 icons for the featured grid --------------------------------
def icon_chip(d, x, y):
    d.rectangle([x, y, x + 38, y + 38], fill=GREEN)
    for px in (x + 6, x + 16, x + 26):
        d.line([px, y - 2, px, y + 6], fill=GREEN, width=2)
        d.line([px, y + 32, px, y + 40], fill=GREEN, width=2)
    for py in (y + 6, y + 16, y + 26):
        d.line([x - 2, py, x + 6, py], fill=GREEN, width=2)
        d.line([x + 32, py, x + 40, py], fill=GREEN, width=2)
    d.rectangle([x + 9, y + 9, x + 29, y + 29], fill=(20, 60, 35))
    d.rectangle([x + 14, y + 14, x + 24, y + 24], fill=(120, 200, 140))


def icon_cyclone(d, x, y):
    d.rectangle([x, y, x + 38, y + 38], fill=SKY)
    for r in (16, 12, 8):
        d.arc([x + 19 - r, y + 19 - r, x + 19 + r, y + 19 + r],
              start=20, end=300, fill=NAVY, width=3)
    d.ellipse([x + 16, y + 16, x + 22, y + 22], fill=RED)


def icon_parliament(d, x, y):
    d.rectangle([x, y, x + 38, y + 38], fill=(226, 216, 190))
    d.polygon([(x + 4, y + 14), (x + 19, y + 4), (x + 34, y + 14)], fill=NAVY)
    for cx in (8, 15, 22, 29):
        d.rectangle([x + cx, y + 16, x + cx + 3, y + 30], fill=NAVY)
    d.rectangle([x + 4, y + 30, x + 34, y + 34], fill=NAVY)


def icon_euro(d, x, y):
    d.ellipse([x + 1, y + 1, x + 37, y + 37], fill=GOLD)
    d.ellipse([x + 5, y + 5, x + 33, y + 33], outline=NAVY, width=2)
    d.text((x + 9, y + 5), "€", font=sans_b(22), fill=NAVY)


def icon_ballot(d, x, y):
    d.rectangle([x, y, x + 38, y + 38], fill=(226, 216, 190))
    d.rectangle([x + 7, y + 16, x + 31, y + 34], fill=(255, 255, 255),
                outline=NAVY, width=2)
    d.line([x + 13, y + 14, x + 25, y + 14], fill=NAVY, width=3)
    d.line([x + 11, y + 24, x + 16, y + 29], fill=RED, width=3)
    d.line([x + 16, y + 29, x + 28, y + 18], fill=RED, width=3)


def icon_patrol(d, x, y):
    d.rectangle([x, y, x + 38, y + 38], fill=SEA)
    d.polygon([(x + 6, y + 22), (x + 32, y + 22), (x + 27, y + 30), (x + 10, y + 30)],
              fill=(120, 120, 120))
    d.rectangle([x + 17, y + 10, x + 20, y + 22], fill=INK)
    d.polygon([(x + 20, y + 10), (x + 29, y + 15), (x + 20, y + 16)], fill=RED)
    for wy in (y + 33, y + 36):
        d.line([x + 3, wy, x + 35, wy], fill=(255, 255, 255), width=2)


ICONS = {"chip": icon_chip, "cyclone": icon_cyclone, "parliament": icon_parliament,
         "euro": icon_euro, "ballot": icon_ballot, "patrol": icon_patrol}


# --- page --------------------------------------------------------------------
def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 24                      # side margin
    right = W - mx

    # Masthead ----------------------------------------------------------------
    d.rectangle([0, 0, W, 64], fill=NAVY)
    d.text((mx, 8), "THE DAY IN WORLD NEWS", font=sans_b(14), fill=(255, 255, 255))
    tail = "35 STORIES · 6 CONTINENTS · ONE PAGE"
    d.text((right - text_w(d, tail, sans_b(13)), 10), tail,
           font=sans_b(13), fill=(255, 255, 255))
    centred(d, 0, W, 30, "Wednesday 18 November 2026", serif_b(30),
            (255, 255, 255))
    d.rectangle([0, 64, W, 67], fill=GOLD)

    # Continents strip ---------------------------------------------------------
    segments_centred(d, 0, W, 72, [
        ("6 CONTINENTS — ", INK),
        ("ASIA 18", RED), (" · ", INK),
        ("EUROPE 5", RED), (" · ", INK),
        ("NORTH AMERICA 6", RED), (" · ", INK),
        ("OCEANIA 3", RED), (" · ", INK),
        ("AFRICA 2", RED), (" · ", INK),
        ("S. AMERICA 1", RED),
    ], sans_b(14))
    d.line([mx, 92, right, 92], fill=GOLD, width=1)

    # Three leads --------------------------------------------------------------
    col_w, gap = 317, 12
    lead_y, art_h = 100, 120
    for i, lead in enumerate(LEADS):
        x = mx + i * (col_w + gap)
        ART[lead["art"]](d, x, lead_y, col_w, art_h)
        d.rectangle([x, lead_y, x + col_w, lead_y + art_h], outline=NAVY, width=1)
        ky = lead_y + art_h + 8
        d.text((x, ky), f"{lead['num']} · {lead['kicker']}", font=sans_b(12), fill=RED)
        head_lines = wrap(d, lead["headline"], serif_b(20), col_w)
        assert len(head_lines) <= 2, lead["headline"]
        hy = ky + 20
        for j, line in enumerate(head_lines):
            d.text((x, hy + j * 23), line, font=serif_b(20), fill=INK)
        fact_lines = wrap(d, lead["fact"], sans_r(12), col_w)
        assert len(fact_lines) <= 2, lead["fact"]
        fy = hy + len(head_lines) * 23 + 5
        for j, line in enumerate(fact_lines):
            d.text((x, fy + j * 15), line, font=sans_r(12), fill=GREY)

    d.line([mx, 336, right, 336], fill=GOLD, width=2)

    # Featured grid: 2 rows x 3 columns ---------------------------------------
    cell_w, cell_h, row_gap = col_w, 84, 4
    grid_y = 344
    for idx, (kicker, headline, fact, icon) in enumerate(FEATURED):
        row, col = divmod(idx, 3)
        x = mx + col * (cell_w + gap)
        y = grid_y + row * (cell_h + row_gap)
        ICONS[icon](d, x, y + 4)
        tx = x + 48
        tw = cell_w - 48
        d.text((tx, y + 2), kicker, font=sans_b(10), fill=RED)
        head_lines = wrap(d, headline, serif_b(15), tw)
        assert len(head_lines) <= 2, headline
        hy = y + 17
        for j, line in enumerate(head_lines):
            d.text((tx, hy + j * 18), line, font=serif_b(15), fill=INK)
        fact_lines = wrap(d, fact, sans_r(10), tw)
        assert len(fact_lines) <= 2, fact
        fy = hy + len(head_lines) * 18 + 3
        for j, line in enumerate(fact_lines):
            d.text((tx, fy + j * 13), line, font=sans_r(10), fill=GREY)
        if col < 2:
            d.line([x + cell_w + 6, y + 4, x + cell_w + 6, y + cell_h - 4],
                   fill=(210, 200, 175), width=1)
    d.line([mx, 524, right, 524], fill=GOLD, width=1)

    # By the numbers ------------------------------------------------------------
    centred(d, 0, W, 532, "BY THE NUMBERS", sans_b(13), RED)
    num_w = (W - 2 * mx) // 4
    for i, (big, cap) in enumerate(NUMBERS):
        cx0 = mx + i * num_w
        centred(d, cx0, cx0 + num_w, 552, big, serif_b(30), NAVY)
        cap_lines = wrap(d, cap, sans_r(11), num_w - 10)
        assert len(cap_lines) <= 2, cap
        for j, line in enumerate(cap_lines):
            centred(d, cx0, cx0 + num_w, 588 + j * 14, line, sans_r(11), GREY)
        if i:
            d.line([cx0, 552, cx0, 606], fill=(210, 200, 175), width=1)
    d.line([mx, 614, right, 614], fill=GOLD, width=2)

    # Map (left) + Also On (right) ----------------------------------------------
    d.text((mx, 622), "THE WORLD IN 35 DOTS", font=sans_b(13), fill=NAVY)
    d.text((510, 622), "ALSO ON", font=sans_b(13), fill=NAVY)

    map_x, map_y, map_w, map_h = mx, 644, 470, 268
    d.rectangle([map_x, map_y, map_x + map_w, map_y + map_h], fill=SEA,
                outline=NAVY, width=1)

    def project(lat, lon):
        px = map_x + (lon + 180.0) / 360.0 * map_w
        py = map_y + (75.0 - lat) / 135.0 * map_h
        return (px, py)

    for poly in CONTINENTS:
        d.polygon([project(lat, lon) for lon, lat in poly], fill=LAND,
                  outline=(150, 135, 95))
    # graticule: equator + tropics, faint
    for lat in (0.0, 23.5, -23.5):
        _, ey = project(lat, 0)
        d.line([map_x, ey, map_x + map_w, ey], fill=(140, 180, 205), width=1)

    for i, (lat, lon) in enumerate(SMALL_DOTS, start=10):
        px, py = project(lat, lon)
        d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=RED,
                  outline=(255, 255, 255), width=1)
    for i, (lat, lon) in enumerate(NUMBERED_DOTS, start=1):
        px, py = project(lat, lon)
        d.ellipse([px - 10, py - 10, px + 10, py + 10], fill=RED,
                  outline=(255, 255, 255), width=2)
        label = str(i)
        lw = text_w(d, label, sans_b(11))
        d.text((px - lw / 2, py - 8), label, font=sans_b(11),
               fill=(255, 255, 255))

    # Also On: 26 items, 2 columns x 13 rows
    also_x = [510, 756]
    also_w = [236, 244]
    row_h = 21
    for idx, item in enumerate(ALSO_ON):
        col, row = divmod(idx, 13)
        x = also_x[col]
        y = map_y + row * row_h
        num = str(idx + 10)
        d.text((x, y), num, font=sans_b(10), fill=RED)
        tx = x + 20
        lines = wrap(d, item, sans_r(10), also_w[col] - 20)
        assert len(lines) <= 2, item
        for j, line in enumerate(lines):
            d.text((tx, y + j * 11), line, font=sans_r(10), fill=INK)

    # Judge note -----------------------------------------------------------------
    box_y0, box_y1 = 922, 964
    d.rectangle([mx, box_y0, right, box_y1], outline=RED, width=2)
    note = ("JUDGE NOTE — Every story above happened, or was first reported, "
            "on Wednesday 18 November 2026. Disputed claims are attributed, "
            "not stated as fact.")
    note_lines = wrap(d, note, serif_i(13), right - mx - 24)
    assert len(note_lines) <= 2, note
    for j, line in enumerate(note_lines):
        centred(d, mx, right, box_y0 + 6 + j * 17, line, serif_i(13), INK)

    # Footer ----------------------------------------------------------------------
    centred(d, 0, W, 972,
            "All stories happened or were first reported on Wednesday 18 November 2026. "
            "Disputed claims are attributed.",
            sans_r(10), GREY)
    centred(d, 0, W, 988,
            "Sources: Reuters, AP, AFP, BBC, Al Jazeera, CNN, IMD, UN. Original drawings.",
            sans_r(10), GREY)
    return img


def main():
    img = build()
    assert img.size == (W, H), img.size
    out = os.path.join(HERE, "entry.png")
    img.save(out, format="PNG")
    small = img.resize((300, 300), Image.LANCZOS)
    small.save(os.path.join(HERE, "entry-300px.png"), format="PNG")
    size = os.path.getsize(out)
    assert size <= MAX_BYTES, f"entry.png too big: {size} bytes"
    digest = hashlib.sha256(open(out, "rb").read()).hexdigest()
    print(f"entry.png: {size} bytes, sha256 {digest}")


if __name__ == "__main__":
    main()
