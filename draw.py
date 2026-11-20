#!/usr/bin/env python3
"""Draw a broadsheet newspaper front page for Friday 20 November 2026.

Pure Python 3 standard library only. No network, no font files, no
downloaded assets: the PNG is encoded by hand (zlib) and every glyph is
defined in this file as a 5x7 bitmap.

Deterministic: the same input always produces byte-identical entry.png.
Run:  python3 draw.py   -> writes entry.png (1024x1024, <= 1 MiB).
"""

import os
import struct
import zlib

W, H = 1024, 1024
MAX_BYTES = 1048576

# ---------------------------------------------------------------- font ----
# Each glyph is 7 rows of 5 bits (bit 4 = leftmost pixel). Written by hand
# for this file; no font file or copied font data is used.
FONT = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    'a': (0x00, 0x0E, 0x01, 0x0F, 0x11, 0x11, 0x0F),
    'b': (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x1E),
    'c': (0x00, 0x0E, 0x11, 0x10, 0x10, 0x11, 0x0E),
    'd': (0x01, 0x01, 0x0F, 0x11, 0x11, 0x11, 0x0F),
    'e': (0x00, 0x0E, 0x11, 0x1F, 0x10, 0x11, 0x0E),
    'f': (0x06, 0x08, 0x08, 0x1E, 0x08, 0x08, 0x08),
    'g': (0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    'h': (0x10, 0x10, 0x1E, 0x11, 0x11, 0x11, 0x11),
    'i': (0x04, 0x00, 0x0C, 0x04, 0x04, 0x04, 0x0E),
    'j': (0x02, 0x00, 0x06, 0x02, 0x02, 0x12, 0x0C),
    'k': (0x10, 0x10, 0x12, 0x14, 0x18, 0x14, 0x12),
    'l': (0x0C, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'm': (0x00, 0x1A, 0x15, 0x15, 0x15, 0x15, 0x15),
    'n': (0x00, 0x1E, 0x11, 0x11, 0x11, 0x11, 0x11),
    'o': (0x00, 0x0E, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'p': (0x00, 0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10),
    'q': (0x00, 0x0F, 0x11, 0x11, 0x0F, 0x01, 0x01),
    'r': (0x00, 0x16, 0x19, 0x10, 0x10, 0x10, 0x10),
    's': (0x00, 0x0F, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    't': (0x04, 0x04, 0x1F, 0x04, 0x04, 0x04, 0x03),
    'u': (0x00, 0x11, 0x11, 0x11, 0x11, 0x13, 0x0D),
    'v': (0x00, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'w': (0x00, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'x': (0x00, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'y': (0x00, 0x11, 0x11, 0x11, 0x0F, 0x01, 0x0E),
    'z': (0x00, 0x1F, 0x02, 0x04, 0x08, 0x10, 0x1F),
    ' ': (0, 0, 0, 0, 0, 0, 0),
    '.': (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ',': (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    '-': (0, 0, 0, 0x0E, 0, 0, 0),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    '"': (0x0A, 0x0A, 0, 0, 0, 0, 0),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    '?': (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    '%': (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '/': (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '+': (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    '=': (0, 0, 0x1F, 0, 0x1F, 0, 0),
    ';': (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    ':': (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    '*': (0, 0x04, 0x15, 0x0E, 0x15, 0x04, 0),
    '_': (0, 0, 0, 0, 0, 0, 0x1F),
    '[': (0x0E, 0x08, 0x08, 0x08, 0x08, 0x08, 0x0E),
    ']': (0x0E, 0x02, 0x02, 0x02, 0x02, 0x02, 0x0E),
    '#': (0x0A, 0x0A, 0x1F, 0x0A, 0x1F, 0x0A, 0x0A),
    '@': (0x0E, 0x11, 0x17, 0x15, 0x16, 0x10, 0x0E),
    '<': (0x02, 0x04, 0x08, 0x10, 0x08, 0x04, 0x02),
    '>': (0x08, 0x04, 0x02, 0x01, 0x02, 0x04, 0x08),
}

# ------------------------------------------------------------- canvas -----
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
NAVY = (18, 42, 86)
LIGHT = (232, 238, 246)
GREY = (90, 90, 90)
RED = (150, 30, 30)


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg * (w * h))

    def set(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.px[i:i + 3] = bytes(color)

    def rect(self, x, y, w, h, color):
        for yy in range(y, y + h):
            for xx in range(x, x + w):
                self.set(xx, yy, color)

    def hline(self, x, y, w, color):
        self.rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.rect(x, y, 1, h, color)

    def circle(self, cx, cy, r, color):
        # Midpoint circle outline.
        x, y, d = 0, r, 3 - 2 * r
        while x <= y:
            for dx, dy in ((x, y), (y, x), (-x, y), (-y, x),
                           (x, -y), (y, -x), (-x, -y), (-y, -x)):
                self.set(cx + dx, cy + dy, color)
            if d < 0:
                d += 4 * x + 6
            else:
                d += 4 * (x - y) + 10
                y -= 1
            x += 1

    def disc(self, cx, cy, r, color):
        for yy in range(cy - r, cy + r + 1):
            dx = int((r * r - (yy - cy) ** 2) ** 0.5) if abs(yy - cy) <= r else 0
            for xx in range(cx - dx, cx + dx + 1):
                self.set(xx, yy, color)


# -------------------------------------------------------------- text ------
def char_w(scale):
    return 6 * scale


def text_w(s, scale):
    return len(s) * char_w(scale)


def draw_char(cv, x, y, ch, scale, color, bold=False):
    glyph = FONT.get(ch)
    if glyph is None:
        glyph = FONT['?']
    for row in range(7):
        bits = glyph[row]
        for col in range(5):
            if bits & (1 << (4 - col)):
                for dy in range(scale):
                    for dx in range(scale):
                        cv.set(x + col * scale + dx, y + row * scale + dy, color)
                        if bold:
                            cv.set(x + col * scale + dx + 1, y + row * scale + dy, color)


def draw_text(cv, x, y, s, scale, color, bold=False):
    for i, ch in enumerate(s):
        draw_char(cv, x + i * char_w(scale), y, ch, scale, color, bold)
    return x + text_w(s, scale)


def wrap(s, max_chars):
    """Greedy word wrap; returns list of lines, each <= max_chars."""
    words, lines, cur = s.split(' '), [], ''
    for wd in words:
        trial = wd if not cur else cur + ' ' + wd
        if len(trial) <= max_chars:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    return lines


def draw_para(cv, x, y, s, scale, color, max_chars, line_h, bold=False, max_lines=None):
    lines = wrap(s, max_chars)
    if max_lines is not None:
        lines = lines[:max_lines]
    for i, ln in enumerate(lines):
        draw_text(cv, x, y + i * line_h, ln, scale, color, bold)
    return y + len(lines) * line_h

# ------------------------------------------------------------ stories -----
# Researched from live news on Friday 20 November 2026 (Reuters, BBC,
# The Hindu, Bloomberg/Hindu BusinessLine, Space.com, AP wires). Every
# headline below was first reported on 20 Nov 2026 (or is a new 20 Nov
# development of an ongoing story). Headlines <= 39 chars, summaries
# <= 39 chars, so each fits one line in a 476 px column at scale 2.

LEAD_HEADLINE = "TRUMP PUSHES IRAN WAR DECISION TO 2027"
LEAD_SUMMARY = (
    "President Trump says there is 'no rush' and he will 'see what "
    "happens' after Jan 1. US intelligence says Iran still holds at "
    "least 2,500 missiles after nine months of conflict."
)

# (section title, [(headline, summary), ...]) -- 6 sections x 5 = 30
SECTIONS = [
    ("WORLD", [
        ("EUROPE READY FOR TALKS WITH RUSSIA",
         "Leaders say they are ready to talk."),
        ("STRIKES HIT EMBASSIES IN KYIV",
         "Strikes hit Austrian, Dutch embassies."),
        ("UKRAINE HITS CRIMEAN BRIDGE",
         "Missiles halt rail traffic to Crimea."),
        ("HOUTHIS STRIKE RIYADH TOWER",
         "Wealth fund tower damaged in attack."),
        ("AUSTRALIA SANCTIONS SETTLERS",
         "Canberra acts over West Bank expansion."),
    ]),
    ("ASIA", [
        ("CYCLONE AKVAN NEARS ODISHA",
         "300,000 evacuated as landfall nears."),
        ("MODI MEETS ROYAL COUPLE",
         "PM hosts Prince and Princess of Wales."),
        ("S. KOREA CLEARS EX-PM HAN",
         "Court clears ex-PM in martial law case."),
        ("FIJI DECLARES DROUGHT DISASTER",
         "Drought forces national disaster order."),
        ("FIRE AT YUNUS FAMILY HOME",
         "Arson suspected in blaze at Yunus home."),
    ]),
    ("MARKETS", [
        ("ANTHROPIC SHARES JUMP 17% ON DEBUT",
         "Record $107.3bn IPO closes at $97.17."),
        ("DOW PLUNGES 1,101 POINTS",
         "Wall Street slides 2% in AI sell-off."),
        ("NVIDIA DOWN 28% IN NOVEMBER",
         "Shares slide after chief's departure."),
        ("SENSEX JUMPS 700 POINTS",
         "Nifty tops 25,400 in Thursday rally."),
        ("MUSK: 'I'M NOT MAGA'",
         "Musk rues $500m spent on midterm races."),
    ]),
    ("TECHNOLOGY", [
        ("GOOGLE SHIPS GEMINI 4 NEON",
         "Flagship coding at $3 per m tokens."),
        ("OPENAI CUTS MODEL PRICES 20%",
         "GPT-6.2 launches in AI price war."),
        ("GRINDR LAUNCHES $120 AI PLAN",
         "App sells AI tier reading private chats."),
        ("MICROSOFT SHIPS SEVEN MODELS",
         "Seven models target price-performance."),
        ("DEEPMIND RELEASES ALPHAGENOME 2",
         "DNA model predicts variant effects."),
    ]),
    ("SCIENCE", [
        ("VOYAGER 1 HITS LIGHT-DAY MARK",
         "Probe now a full light-day from Earth."),
        ("HAYABUSA2 DROPS ASTEROID LANDING",
         "Engine fault ends asteroid landing plan."),
        ("STAR SWALLOWS ITS COMPANION",
         "Star seen swallowing its companion."),
        ("ISLAM TO PASS CHRISTIANITY",
         "Islam to pass Christianity in a decade."),
        ("IRISHMAN HELD OVER $60M JET ATTACK",
         "Man held over axe attack on $60m US jet."),
    ]),
    ("SPORT", [
        ("NICHOLLS 113* RESCUES NEW ZEALAND",
         "Hosts reach 243 for 5 on day one."),
        ("ZVEREV BEATS FILS AT ATP FINALS",
         "German wins group-stage clash in Turin."),
        ("RAKSHITHA STUNS OLYMPIC CHAMPION",
         "Indian stuns champion at Hong Kong Open."),
        ("HOCKEY CHAMPIONS TROPHY BEGINS",
         "Women's Asian hockey trophy begins."),
        ("GTA 6 SALES TOP $1.8 BILLION",
         "Game passes Odyssey's $1.8bn box office."),
    ]),
]

# -------------------------------------------------------- illustration ----
def draw_illustration(cv, x, y, w, h):
    """A small drawn scene for the lead: globe, orbit ring, skyline."""
    cv.rect(x, y, w, h, LIGHT)
    cv.rect(x, y, w, 2, NAVY)
    cv.rect(x, y + h - 2, w, 2, NAVY)
    cx, cy, r = x + w // 2, y + 78, 58
    # Orbit ring (ellipse approximated with two circles).
    cv.circle(cx, cy, r + 12, NAVY)
    cv.circle(cx, cy, r + 13, NAVY)
    # Globe.
    cv.disc(cx, cy, r, (200, 220, 240))
    cv.circle(cx, cy, r, NAVY)
    cv.circle(cx, cy, r - 1, NAVY)
    # Meridians and parallels.
    cv.vline(cx, cy - r, 2 * r, NAVY)
    for dy in (-30, 0, 30):
        cv.hline(cx - r + 8, cy + dy, 2 * r - 16, NAVY)
    # Land masses (simple blobs).
    cv.disc(cx - 22, cy - 18, 12, (120, 170, 120))
    cv.disc(cx + 20, cy + 16, 14, (120, 170, 120))
    cv.disc(cx + 24, cy - 24, 8, (120, 170, 120))
    # Stars.
    for sx, sy in ((x + 18, y + 16), (x + w - 22, y + 20),
                   (x + 30, y + 150), (x + w - 34, y + 148)):
        cv.disc(sx, sy, 2, NAVY)
    # Skyline silhouette along the bottom (above the caption strip).
    base = y + h - 20
    heights = [26, 44, 34, 58, 40, 30, 52, 36, 46, 28]
    bw = w // len(heights)
    for i, bh in enumerate(heights):
        cv.rect(x + i * bw + 2, base - bh, bw - 4, bh, NAVY)
        # Windows.
        for wy in range(base - bh + 6, base - 6, 10):
            cv.rect(x + i * bw + 6, wy, 3, 4, (255, 220, 120))
    # Caption strip.
    cv.rect(x, y + h - 18, w, 18, NAVY)
    draw_text(cv, x + 10, y + h - 15, "WASHINGTON - TEHRAN - 20 NOV",
              1, WHITE, bold=True)


# ------------------------------------------------------------ layout ------
def build():
    cv = Canvas(W, H, WHITE)
    MX = 24                      # side margin
    CW = W - 2 * MX              # content width: 976

    # ---- Masthead ----
    title = "THE DAILY GLOBE"
    tw = text_w(title, 6)
    draw_text(cv, MX + (CW - tw) // 2, 14, title, 6, BLACK, bold=True)
    cv.hline(MX, 64, CW, BLACK)
    date_line = "FRIDAY, 20 NOVEMBER 2026"
    dw = text_w(date_line, 2)
    draw_text(cv, MX + (CW - dw) // 2, 70, date_line, 2, NAVY, bold=True)
    sub = "30 STORIES FROM AROUND THE WORLD - PRICE: FREE"
    sw = text_w(sub, 2)
    draw_text(cv, MX + (CW - sw) // 2, 88, sub, 2, GREY)
    cv.rect(MX, 106, CW, 3, BLACK)
    cv.hline(MX, 112, CW, BLACK)

    # ---- Lead story ----
    ly = 124
    kicker = "LEAD STORY"
    draw_text(cv, MX, ly, kicker, 2, RED, bold=True)
    # Illustration on the right.
    ill_x, ill_w = 700, 300
    draw_illustration(cv, ill_x, ly, ill_w, 176)
    # Headline (left of illustration).
    lead_w = ill_x - MX - 16
    max_chars = lead_w // char_w(3)
    lines = wrap(LEAD_HEADLINE, max_chars)
    hy = ly + 20
    for i, ln in enumerate(lines):
        draw_text(cv, MX, hy + i * 24, ln, 3, BLACK, bold=True)
    sy = hy + len(lines) * 24 + 8
    draw_para(cv, MX, sy, LEAD_SUMMARY, 2, BLACK, lead_w // char_w(2), 17,
              max_lines=4)
    cv.hline(MX, 312, CW, BLACK)

    # ---- Sections: 2 columns x 3 rows ----
    col_w = 476
    col_x = [MX, MX + col_w + 24]
    row_y = [324, 540, 756]
    sec_h = 204
    for idx, (name, stories) in enumerate(SECTIONS):
        cx = col_x[idx % 2]
        cy = row_y[idx // 2]
        # Header bar.
        cv.rect(cx, cy, col_w, 24, NAVY)
        draw_text(cv, cx + 8, cy + 5, name, 2, WHITE, bold=True)
        # Stories.
        sy = cy + 32
        for hline_text, summary in stories:
            draw_text(cv, cx, sy, hline_text, 2, BLACK, bold=True)
            draw_text(cv, cx, sy + 16, summary, 2, GREY)
            sy += 34
        assert sy <= cy + sec_h, "section overflow: %s" % name

    # ---- Footer ----
    foot = "Every story above was first reported on Friday 20 November 2026."
    fw = text_w(foot, 2)
    draw_text(cv, MX + (CW - fw) // 2, 976, foot, 2, BLACK)
    cv.hline(MX, 998, CW, BLACK)
    tag = "THE DAILY GLOBE - PAGE 1 - 20 NOVEMBER 2026"
    tw2 = text_w(tag, 1)
    draw_text(cv, MX + (CW - tw2) // 2, 1006, tag, 1, GREY)
    return cv


# -------------------------------------------------------------- PNG -------
def write_png(cv, path):
    raw = bytearray()
    for y in range(cv.h):
        raw.append(0)  # filter: none
        raw += cv.px[y * cv.w * 3:(y + 1) * cv.w * 3]
    comp = zlib.compress(bytes(raw), 9)

    def chunk(tag, data):
        c = struct.pack(">I", len(data)) + tag + data
        return c + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", cv.w, cv.h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", comp)
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    cv = build()
    n = sum(len(s[1]) for s in SECTIONS) + 1
    here = os.path.dirname(os.path.abspath(__file__))
    out = os.path.join(here, "entry.png")
    size = write_png(cv, out)
    print("wrote %s (%d bytes, %d stories)" % (out, size, n))
    assert size <= MAX_BYTES, "entry.png exceeds 1 MiB: %d" % size


if __name__ == "__main__":
    main()
