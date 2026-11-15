#!/usr/bin/env python3
"""
ZAY KEYS installer - asset generator.
Renders every bitmap used by the installer UI (Frutiger Aero / dark blue + cyan)
and emits the shared layout/payload includes consumed by ZayKeysInstaller.iss.

Requires: Python 3.9+, Pillow, numpy.   Usage:  python tools/build_assets.py
"""
import hashlib, json, math, random, sys
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / "assets" / "generated"
PAYLOAD = ROOT / "payload"
GEN.mkdir(parents=True, exist_ok=True)

W, H, S = 860, 560, 2          # window size, supersampling
R_WIN = 22                      # window corner radius
PANEL = (30, 52, 830, 504)
KB_ORG = (60, 350)              # keyboard assembly origin
KEYS_X, KEYS_Y = 80, 380        # key area origin (abs)
KW, NW, KH, BH, BW = 25, 28, 96, 60, 16

FONT_DIR = ["/usr/share/fonts/truetype/google-fonts/", "C:/Windows/Fonts/"]
def font(name, px):
    for d in FONT_DIR:
        p = Path(d) / name
        if p.exists():
            return ImageFont.truetype(str(p), int(px * S))
    return ImageFont.load_default()

# ---------------------------------------------------------------- helpers
def vgrad(w, h, stops):
    ys = np.linspace(0, 1, max(h, 1))
    arr = np.zeros((h, w, 4), np.float32)
    pos = [s[0] for s in stops]
    for c in range(4):
        col = np.interp(ys, pos, [(s[1] + (255,))[c] if len(s[1]) == 3 else s[1][c] for s in stops])
        arr[:, :, c] = col[:, None]
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")

def hgrad(w, h, stops):
    col = np.array(vgrad(1, w, stops))            # (w,1,4)
    return Image.fromarray(np.ascontiguousarray(col.transpose(1, 0, 2).repeat(h, 0)), "RGBA")

def rmask(w, h, r, top_square=False):
    m = Image.new("L", (w, h), 0)
    d = ImageDraw.Draw(m)
    if top_square:
        d.rounded_rectangle((0, -r * 2, w - 1, h - 1), r, fill=255)
    else:
        d.rounded_rectangle((0, 0, w - 1, h - 1), r, fill=255)
    return m

def over(base, layer, xy=(0, 0), mask=None):
    if mask is not None:
        layer = layer.copy()
        a = ImageChops.multiply(layer.getchannel("A"), mask)
        layer.putalpha(a)
    base.alpha_composite(layer, (int(xy[0]), int(xy[1])))

def blur(img, r):
    return img.filter(ImageFilter.GaussianBlur(r * S))

def glow_ellipse(size, cx, cy, rx, ry, color, alpha):
    w, h = size
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2)
    a = np.clip(1 - d, 0, 1) ** 2 * alpha
    arr = np.zeros((h, w, 4), np.uint8)
    arr[..., 0], arr[..., 1], arr[..., 2] = color
    arr[..., 3] = a.astype(np.uint8)
    return Image.fromarray(arr, "RGBA")

def spaced_text(layer_size, txt, fnt, x, y, spacing, fill=255):
    m = Image.new("L", layer_size, 0)
    d = ImageDraw.Draw(m)
    cx = x
    for ch in txt:
        d.text((cx, y), ch, font=fnt, fill=fill)
        cx += d.textlength(ch, font=fnt) + spacing
    return m, cx - spacing - x

def text_width(txt, fnt, spacing):
    d = ImageDraw.Draw(Image.new("L", (4, 4)))
    return sum(d.textlength(c, font=fnt) + spacing for c in txt) - spacing

# ---------------------------------------------------------------- base background
def build_base():
    w, h = W * S, H * S
    img = vgrad(w, h, [(0, (2, 8, 24)), (0.45, (4, 28, 72)), (1, (2, 12, 38))])
    over(img, glow_ellipse((w, h), 430 * S, 470 * S, 520 * S, 240 * S, (0, 170, 255), 120))
    over(img, glow_ellipse((w, h), 130 * S, 40 * S, 380 * S, 200 * S, (60, 200, 255), 85))
    over(img, glow_ellipse((w, h), 780 * S, 120 * S, 260 * S, 200 * S, (30, 110, 255), 70))
    # light beams (top-left)
    beams = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(beams)
    for x0, wd, a in [(60, 110, 34), (240, 70, 26), (420, 150, 20), (640, 60, 18)]:
        d.polygon([(x0 * S, 0), ((x0 + wd) * S, 0), ((x0 + wd + 420) * S, h), ((x0 + 300) * S, h)], fill=(150, 225, 255, a))
    over(img, blur(beams, 14))
    # flowing cyan light lines
    lines = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(lines)
    for k, (base, amp, ph, a) in enumerate([(430, 70, 0.0, 150), (470, 90, 1.3, 110), (390, 55, 2.4, 90)]):
        pts = [(x * S, (base - x * 0.18 + amp * math.sin(x / 150 + ph)) * S) for x in range(0, W + 8, 6)]
        d.line(pts, fill=(80, 220, 255, a), width=int(1.5 * S))
    over(img, blur(lines, 5))
    over(img, lines)
    # bokeh
    rnd = random.Random(7)
    bok = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(bok)
    for _ in range(16):
        cx, cy, r = rnd.randint(0, W), rnd.randint(30, H), rnd.randint(14, 58)
        a = rnd.randint(14, 34)
        d.ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), fill=(90, 210, 255, a), outline=(170, 240, 255, a * 2))
    over(img, blur(bok, 1.2))
    # glass panel
    pw, ph = (PANEL[2] - PANEL[0]) * S, (PANEL[3] - PANEL[1]) * S
    pm = rmask(pw, ph, 26 * S)
    fill = vgrad(pw, ph, [(0, (190, 235, 255, 46)), (0.5, (60, 150, 230, 26)), (1, (10, 70, 150, 40))])
    over(img, fill, (PANEL[0] * S, PANEL[1] * S), pm)
    gl = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    ImageDraw.Draw(gl).ellipse((-pw // 3, -ph * 2 // 3, pw + pw // 3, ph // 3), fill=(255, 255, 255, 16))
    gl = gl.filter(ImageFilter.GaussianBlur(10 * S))
    over(img, gl, (PANEL[0] * S, PANEL[1] * S), pm)
    bd = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
    ImageDraw.Draw(bd).rounded_rectangle((0, 0, pw - 1, ph - 1), 26 * S, outline=(150, 230, 255, 120), width=2 * S)
    over(img, bd, (PANEL[0] * S, PANEL[1] * S))
    # window frame
    fr = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(fr).rounded_rectangle((0, 0, w - 1, h - 1), R_WIN * S, outline=(90, 200, 255, 150), width=2 * S)
    over(img, fr)
    # title bar: mini logo + wordmark
    over(img, icon_mark(30 * S), (24 * S, 10 * S))
    f1, f2 = font("Poppins-Bold.ttf", 15), font("Poppins-Medium.ttf", 10.5)
    t = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    m, wd = spaced_text((w, h), "ZAY KEYS", f1, 64 * S, 11 * S, 2 * S)
    over(t, Image.new("RGBA", (w, h), (255, 255, 255, 255)), mask=m)
    m2, _ = spaced_text((w, h), "INSTALLER", f2, int(64 * S + wd + 12 * S), 15 * S, 3 * S)
    over(t, Image.new("RGBA", (w, h), (90, 220, 255, 255)), mask=m2)
    over(img, t)
    # footer line
    d = ImageDraw.Draw(img)
    d.line((40 * S, 509 * S, (W - 40) * S, 509 * S), fill=(110, 210, 255, 50), width=S)
    return img

# ---------------------------------------------------------------- icon mark
def icon_mark(size):
    s = size
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    m = rmask(s, s, int(s * 0.24))
    bg = vgrad(s, s, [(0, (40, 170, 255)), (0.55, (8, 70, 170)), (1, (3, 22, 70))])
    over(img, bg, mask=m)
    d = ImageDraw.Draw(img)
    kx0, kx1, ky0, ky1 = s * 0.16, s * 0.84, s * 0.40, s * 0.82
    n = 5
    kw = (kx1 - kx0) / n
    for i in range(n):
        d.rounded_rectangle((kx0 + i * kw + 0.8, ky0, kx0 + (i + 1) * kw - 0.8, ky1), max(1, int(s * 0.04)), fill=(238, 248, 255, 255))
    for i in (0, 1, 3):
        bx = kx0 + (i + 1) * kw
        d.rectangle((bx - kw * 0.28, ky0, bx + kw * 0.28, ky0 + (ky1 - ky0) * 0.6), fill=(6, 18, 44, 255))
    hl = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    ImageDraw.Draw(hl).ellipse((-s * 0.2, -s * 0.75, s * 1.2, s * 0.5), fill=(255, 255, 255, 70))
    over(img, hl, mask=m)
    ImageDraw.Draw(img).rounded_rectangle((0, 0, s - 1, s - 1), int(s * 0.24), outline=(170, 240, 255, 200), width=max(1, s // 40))
    return img

# ---------------------------------------------------------------- 3D keyboard
def white_stops(st):
    return [[(0, (250, 253, 255)), (0.55, (222, 236, 248)), (1, (150, 182, 214))],
            [(0, (200, 244, 255)), (0.5, (110, 216, 250)), (1, (28, 148, 226))],
            [(0, (240, 255, 255)), (0.45, (150, 240, 255)), (1, (36, 190, 246))]][st]

def black_stops(st):
    return [[(0, (34, 48, 78)), (0.12, (14, 24, 48)), (1, (3, 8, 20))],
            [(0, (70, 180, 235)), (0.15, (10, 96, 168)), (1, (0, 40, 100))],
            [(0, (160, 244, 255)), (0.15, (34, 176, 244)), (1, (0, 92, 184))]][st]

def black_x(i):             # abs x (key-area coords) of black key after white i, or None
    return (i + 1) * KW - BW // 2 if (i % 7) in (0, 1, 3, 4, 5) and i < NW - 1 else None

def render_keys(st):
    w, h = KW * NW * S, KH * S
    img = Image.new("RGBA", (w, h), (4, 10, 26, 255))
    for i in range(NW):
        kw = (KW - 1) * S
        key = vgrad(kw, h, white_stops(st))
        gl = vgrad(kw, h, [(0, (255, 255, 255, 90 if st == 0 else 60)), (0.34, (255, 255, 255, 14)), (1, (255, 255, 255, 0))])
        key.alpha_composite(gl)
        ImageDraw.Draw(key).line((0, 0, 0, h), fill=(255, 255, 255, 90), width=S)
        img.alpha_composite(Image.composite(key, Image.new("RGBA", key.size, (0, 0, 0, 0)), rmask(kw, h, 4 * S, True)), (i * KW * S, 0))
    sh = Image.new("L", (w, h), 0)
    sd = ImageDraw.Draw(sh)
    for i in range(NW):
        bx = black_x(i)
        if bx is not None:
            sd.rectangle(((bx - 1) * S, 0, (bx + BW + 1) * S, (BH + 9) * S), fill=150)
    sh = sh.filter(ImageFilter.GaussianBlur(3 * S))
    over(img, Image.new("RGBA", (w, h), (0, 20, 50, 255)), mask=sh.point(lambda v: int(v * 0.62)))
    for i in range(NW):
        bx = black_x(i)
        if bx is None:
            continue
        bw, bh = BW * S, BH * S
        k = vgrad(bw, bh, black_stops(st))
        d = ImageDraw.Draw(k)
        d.rectangle((0, 0, bw, int(bh * 0.1)), fill=(255, 255, 255, 38))
        d.line((S, 0, S, bh), fill=(120, 220, 255, 110 if st else 70), width=S)
        d.line((bw - S, 0, bw - S, bh), fill=(120, 220, 255, 60), width=S)
        d.rectangle((int(bw * 0.28), S, int(bw * 0.42), int(bh * 0.72)), fill=(255, 255, 255, 40 if st == 0 else 70))
        img.alpha_composite(Image.composite(k, Image.new("RGBA", k.size, (0, 0, 0, 0)), rmask(bw, bh, 3 * S, True)), (bx * S, 0))
    return img

def keyboard_assembly(keys0):
    w, h = 740 * S, 154 * S
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    body = vgrad(720 * S, 134 * S, [(0, (30, 70, 130)), (0.2, (14, 40, 88)), (1, (4, 16, 44))])
    over(img, body, (10 * S, 10 * S), rmask(720 * S, 134 * S, 9 * S))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((10 * S, 10 * S, 730 * S - 1, 144 * S - 1), 9 * S, outline=(100, 215, 255, 150), width=S)
    d.line((22 * S, 28 * S, 718 * S, 28 * S), fill=(90, 220, 255, 150), width=S)
    d.line((22 * S, 130 * S, 718 * S, 130 * S), fill=(90, 220, 255, 90), width=S)
    f = font("Poppins-Bold.ttf", 8.5)
    m, _ = spaced_text((w, h), "ZAY KEYS", f, 28 * S, 14 * S, 2 * S)
    over(img, Image.new("RGBA", (w, h), (150, 235, 255, 255)), mask=m)
    f2 = font("Poppins-Medium.ttf", 7.5)
    tw = text_width("GOLDMINE AUDIO", f2, 2 * S)
    m, _ = spaced_text((w, h), "GOLDMINE AUDIO", f2, int(712 * S - tw), 15 * S, 2 * S)
    over(img, Image.new("RGBA", (w, h), (90, 170, 215, 255)), mask=m)
    for i in range(5):
        d.ellipse(((330 + i * 14) * S, 16 * S, (336 + i * 14) * S, 22 * S), fill=(60, 220, 255, 200 if i < 3 else 70))
    img.alpha_composite(keys0, (20 * S, 30 * S))
    cheek = hgrad(10 * S, 100 * S, [(0, (8, 22, 52)), (1, (40, 100, 170))])
    over(img, cheek, (10 * S, 30 * S))
    over(img, cheek.transpose(Image.FLIP_LEFT_RIGHT), (720 * S, 30 * S))
    # glossy floor reflection
    ref = img.crop((0, 90 * S, w, 144 * S)).transpose(Image.FLIP_TOP_BOTTOM)
    fade = vgrad(ref.width, ref.height, [(0, (0, 0, 0, 70)), (0.35, (0, 0, 0, 20)), (1, (0, 0, 0, 0))]).getchannel("A")
    ref.putalpha(ImageChops.multiply(ref.getchannel("A"), fade))
    img.alpha_composite(ref, (0, 144 * S))
    return img

# ---------------------------------------------------------------- page decorations
def paste_keyboard(img, asm):
    img.alpha_composite(asm, (KB_ORG[0] * S, KB_ORG[1] * S))

def glass_rect(img, box, r, fill_top, fill_bot, border):
    x0, y0, x1, y1 = [v * S for v in box]
    w, h = x1 - x0, y1 - y0
    over(img, vgrad(w, h, [(0, fill_top), (1, fill_bot)]), (x0, y0), rmask(w, h, r * S))
    ImageDraw.Draw(img).rounded_rectangle((x0, y0, x1 - 1, y1 - 1), r * S, outline=border, width=S)

def page_welcome(base, asm, logo):
    img = base.copy()
    paste_keyboard(img, asm)
    img.alpha_composite(logo, (0, 0))
    return img

def build_logo():
    w, h = W * S, 250 * S
    f = font("Poppins-Bold.ttf", 82)
    txt, sp = "ZAY KEYS", 6 * S
    tw = text_width(txt, f, sp)
    x, y = (w - tw) / 2, 54 * S
    mask, _ = spaced_text((w, h), txt, f, x, y, sp)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    over(out, Image.new("RGBA", (w, h), (0, 170, 255, 255)), mask=mask.filter(ImageFilter.GaussianBlur(9 * S)).point(lambda v: min(255, int(v * 1.6))))
    stroke = mask.filter(ImageFilter.MaxFilter(5))
    over(out, Image.new("RGBA", (w, h), (2, 24, 70, 255)), mask=stroke)
    fill = vgrad(w, h, [(0, (255, 255, 255)), (0.50, (150, 235, 255)), (0.78, (40, 170, 250)), (1, (10, 80, 200))])
    fill = fill.crop((0, 0, w, h))
    over(out, fill, mask=mask)
    hl = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(hl).ellipse((x - 20 * S, y - 60 * S, x + tw + 20 * S, y + 52 * S), fill=(255, 255, 255, 120))
    over(out, hl, mask=mask)
    ref = out.crop((0, y - 2 * S, w, y + 96 * S)).transpose(Image.FLIP_TOP_BOTTOM)
    fade = vgrad(ref.width, ref.height, [(0, (0, 0, 0, 80)), (0.6, (0, 0, 0, 10)), (1, (0, 0, 0, 0))]).getchannel("A")
    ref.putalpha(ImageChops.multiply(ref.getchannel("A"), fade))
    # tagline
    f2 = font("Poppins-Medium.ttf", 12.5)
    tag = "VIRTUAL KEYBOARD INSTRUMENT   \u00b7   VST3"
    tw2 = text_width(tag, f2, 3 * S)
    m2, _ = spaced_text((w, h), tag, f2, (w - tw2) / 2, y + 96 * S, 3 * S)
    big = Image.new("RGBA", (w, H * S), (0, 0, 0, 0))
    big.alpha_composite(out, (0, 0))
    over(big, Image.new("RGBA", (w, h), (130, 215, 250, 255)), mask=m2)
    d = ImageDraw.Draw(big)
    ty = int(y + 104 * S)
    d.line(((w - tw2) / 2 - 70 * S, ty, (w - tw2) / 2 - 14 * S, ty), fill=(90, 220, 255, 170), width=S)
    d.line(((w + tw2) / 2 + 14 * S, ty, (w + tw2) / 2 + 70 * S, ty), fill=(90, 220, 255, 170), width=S)
    return big

def page_location(base, asm):
    img = base.copy()
    paste_keyboard(img, asm)
    glass_rect(img, (60, 148, 696, 188), 10, (5, 20, 48, 255), (9, 28, 58, 255), (90, 200, 250, 190))
    return img

def page_components(base, asm, n):
    img = base.copy()
    paste_keyboard(img, asm)
    for i in range(n):
        y = 112 + i * 64
        glass_rect(img, (60, y, 800, y + 54), 13, (110, 200, 255, 40), (20, 90, 170, 28), (110, 215, 255, 120))
        glass_rect(img, (78, y + 15, 102, y + 39), 7, (4, 18, 44, 255), (10, 30, 62, 255), (110, 220, 255, 230))
    return img

def page_install(base, asm):
    img = base.copy()
    paste_keyboard(img, asm)
    glass_rect(img, (60, 160, 800, 184), 12, (2, 12, 34, 255), (8, 30, 66, 255), (100, 210, 255, 200))
    ImageDraw.Draw(img).line((74 * S, 162 * S, 786 * S, 162 * S), fill=(255, 255, 255, 40), width=S)
    return img

def page_done(base, asm):
    img = base.copy()
    paste_keyboard(img, asm)
    return img

# ---------------------------------------------------------------- buttons
SLOTS = [  # name, x, y, w, h, style, page
    ("CLOSE", 818, 12, 28, 28, "close", "welcome"),
    ("MIN", 784, 12, 28, 28, "min", "welcome"),
    ("LANG", 690, 12, 84, 28, "pill", "welcome"),
    ("START", 300, 262, 260, 46, "primary", "welcome"),
    ("BACK", 560, 514, 124, 34, "secondary", "welcome"),
    ("NEXT", 696, 514, 134, 34, "primary", "welcome"),
    ("BROWSE", 708, 148, 92, 40, "secondary", "location"),
    ("DETECT", 708, 196, 92, 32, "secondary", "location"),
    ("OPEN", 230, 262, 200, 46, "secondary", "done"),
    ("FINISH", 450, 262, 180, 46, "primary", "done"),
]
AT_W, AT_ROW = 300, 50

def draw_button(style, w, h, hover):
    ww, hh = w * S, h * S
    img = Image.new("RGBA", (ww, hh), (0, 0, 0, 0))
    if style in ("close", "min"):
        a = 70 if hover else 28
        col = (255, 80, 90) if style == "close" else (120, 220, 255)
        ImageDraw.Draw(img).ellipse((0, 0, ww - 1, hh - 1), fill=col + (a,), outline=(150, 230, 255, 150 if hover else 90), width=S)
        d = ImageDraw.Draw(img)
        c = (255, 255, 255, 255)
        cx, cy, k = ww / 2, hh / 2, 5 * S
        if style == "close":
            d.line((cx - k, cy - k, cx + k, cy + k), fill=c, width=int(1.8 * S))
            d.line((cx - k, cy + k, cx + k, cy - k), fill=c, width=int(1.8 * S))
        else:
            d.line((cx - k, cy + 3 * S, cx + k, cy + 3 * S), fill=c, width=int(1.8 * S))
        return img
    r = hh // 2
    m = rmask(ww, hh, r)
    if style == "primary":
        top, bot = ((130, 242, 255), (10, 160, 245)) if hover else ((90, 225, 255), (0, 120, 225))
        edge = (215, 250, 255, 255)
    elif style == "pill":
        top, bot, edge = (30, 80, 140), (8, 32, 76), (110, 210, 255, 200)
    else:
        top, bot = ((50, 130, 200), (14, 62, 124)) if hover else ((26, 80, 140), (8, 34, 80))
        edge = (130, 225, 255, 255) if hover else (90, 195, 250, 220)
    if hover and style != "pill":
        gl = Image.new("RGBA", (ww + 40 * S, hh + 40 * S), (0, 0, 0, 0))
        ImageDraw.Draw(gl).rounded_rectangle((20 * S, 20 * S, ww + 20 * S, hh + 20 * S), r, fill=(60, 220, 255, 110))
        gl = blur(gl, 7).crop((20 * S, 20 * S, ww + 20 * S, hh + 20 * S))
        img.alpha_composite(gl)
    over(img, vgrad(ww, hh, [(0, top + (255,)), (1, bot + (255,))]), mask=m)
    hl = Image.new("RGBA", (ww, hh), (0, 0, 0, 0))
    ImageDraw.Draw(hl).rounded_rectangle((3 * S, 2 * S, ww - 3 * S, hh // 2), r, fill=(255, 255, 255, 80 if style == "primary" else 42))
    over(img, hl, mask=m)
    ImageDraw.Draw(img).rounded_rectangle((0, 0, ww - 1, hh - 1), r, outline=edge, width=S)
    return img

def build_atlas_and_pages(pages):
    atlas = Image.new("RGB", (AT_W * 2, AT_ROW * len(SLOTS)), (0, 0, 0))
    for i, (name, x, y, w, h, style, page) in enumerate(SLOTS):
        for hv in (0, 1):
            crop = pages[page].crop((x * S, y * S, (x + w) * S, (y + h) * S)).copy()
            crop.alpha_composite(draw_button(style, w, h, hv))
            crop = crop.resize((w, h), Image.LANCZOS).convert("RGB")
            atlas.paste(crop, (hv * AT_W, i * AT_ROW))
    atlas.save(GEN / "buttons.bmp")

# ---------------------------------------------------------------- outputs
def to_rgb(img):
    return img.resize((W, H), Image.LANCZOS).convert("RGB")

def emit_layout(comp_ids):
    kdefs = []
    for i in range(NW):
        x0 = i * KW
        xl = x0 + (BW // 2 if i > 0 and black_x(i - 1) is not None else 0)
        xr = x0 + KW - (BW // 2 if black_x(i) is not None else 0)
        rects = [(xl, 0, xr - xl, BH), (x0, BH, KW, KH - BH)]
        kdefs.append((x0 + KW // 2, 1, rects))
        bx = black_x(i)
        if bx is not None:
            kdefs.append((bx + BW // 2, 0, [(bx, 0, BW, BH)]))
    kdefs.sort(key=lambda k: k[0])
    L = ["// AUTO-GENERATED by tools/build_assets.py - do not edit", "const"]
    consts = dict(C_W=W, C_H=H, KB_X=KEYS_X, KB_Y=KEYS_Y, KB_N=len(kdefs), KB_H=KH,
                  PB_X=60, PB_Y=160, PB_W=740, PB_H=24, FLD_X=60, FLD_Y=148, FLD_W=636, FLD_H=40,
                  CARD_X=60, CARD_Y=112, CARD_DY=64, CARD_W=740, CARD_H=54, BOX_X=78, BOX_Y=15, BOX_S=24,
                  COMP_N=len(comp_ids), AT_W=AT_W, AT_ROW=AT_ROW, SLOT_N=len(SLOTS), RWIN=R_WIN)
    for i, s in enumerate(SLOTS):
        consts["B_" + s[0]] = i
    items = list(consts.items())
    for j, (k, v) in enumerate(items):
        L.append(f"  {k} = {v};")
    L.append("")
    L.append("procedure InitLayout;")
    L.append("begin")
    for i, s in enumerate(SLOTS):
        L.append(f"  SlX[{i}]:={s[1]}; SlY[{i}]:={s[2]}; SlW[{i}]:={s[3]}; SlH[{i}]:={s[4]};")
    for i, (cx, white, rects) in enumerate(kdefs):
        r1 = rects[1] if len(rects) > 1 else (0, 0, 0, 0)
        r0 = rects[0]
        if len(rects) == 1:
            r0, r1 = rects[0], (0, 0, 0, 0)
        L.append(f"  KCx[{i}]:={cx}; KWh[{i}]:={white}; "
                 f"KAx[{i}]:={r0[0]}; KAy[{i}]:={r0[1]}; KAw[{i}]:={r0[2]}; KAh[{i}]:={r0[3]}; "
                 f"KBx[{i}]:={r1[0]}; KBy[{i}]:={r1[1]}; KBw[{i}]:={r1[2]}; KBh[{i}]:={r1[3]};")
    for i, cid in enumerate(comp_ids):
        L.append(f"  CompId[{i}]:='{cid}';")
    L.append("end;")
    (GEN / "layout.pas").write_text("\n".join(L) + "\n", encoding="utf-8")

def emit_payload():
    mi = json.loads(__import__("re").sub(r",(\s*[}\]])", r"\1", (PAYLOAD / "ZAY KEYS.vst3/Contents/Resources/moduleinfo.json").read_text(encoding="utf-8")))
    dll = PAYLOAD / "ZAY KEYS.vst3/Contents/x86_64-win/ZAY KEYS.vst3"
    if not dll.exists():
        sys.exit("ERROR: payload DLL missing: " + str(dll))
    sha = hashlib.sha256(dll.read_bytes()).hexdigest()
    docs = (PAYLOAD / "Documentation").exists() and any((PAYLOAD / "Documentation").iterdir())
    pres = (PAYLOAD / "Presets").exists() and any(p.is_file() for p in (PAYLOAD / "Presets").rglob("*"))
    lines = ["; AUTO-GENERATED by tools/build_assets.py - do not edit",
             f'#define AppVersion "{mi["Version"]}"',
             f'#define AppVendor "{mi["Factory Info"]["Vendor"]}"',
             f'#define DllSha256 "{sha}"',
             f'#define DllSize {dll.stat().st_size}']
    if docs: lines.append("#define HAS_DOCS")
    if pres: lines.append("#define HAS_PRESETS")
    (GEN / "payload.iss").write_text("\n".join(lines) + "\n", encoding="utf-8")
    ids = ["vst3"] + (["presets"] if pres else []) + (["docs"] if docs else [])
    print("payload:", mi["Version"], sha[:16], "docs" if docs else "-", "presets" if pres else "-")
    return ids

def main():
    ids = emit_payload()
    base = build_base()
    keys = [render_keys(i) for i in range(3)]
    asm = keyboard_assembly(keys[0])
    logo = build_logo()
    pages = {"welcome": page_welcome(base, asm, logo), "location": page_location(base, asm),
             "components": page_components(base, asm, len(ids)), "install": page_install(base, asm),
             "done": page_done(base, asm)}
    for k, v in pages.items():
        to_rgb(v).save(GEN / f"bg_{k}.bmp")
    # lit key sheet: 2 states stacked (1=soft, 2=bright)
    sheet = Image.new("RGB", (KW * NW, KH * 2))
    for st in (1, 2):
        sheet.paste(keys[st].resize((KW * NW, KH), Image.LANCZOS).convert("RGB"), (0, (st - 1) * KH))
    sheet.save(GEN / "keys_lit.bmp")
    build_atlas_and_pages(pages)
    emit_layout(ids)
    ico = icon_mark(256 * 1)
    ico.save(GEN / "zaykeys.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    to_rgb(pages["welcome"]).save(GEN / "preview_welcome.png")
    print("assets OK ->", GEN)

if __name__ == "__main__":
    main()
