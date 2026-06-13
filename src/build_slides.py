"""Build the 5-minute presentation slide deck as a PDF that matches the
film's Anthropic-cream visual register.

Run:
    python -m src.build_slides

Outputs: slides/intentional_rescue_slides.pdf
"""
from __future__ import annotations

import os

from reportlab.lib.colors import Color
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas


# ---- 16:9 page at 1920×1080 PDF points -----------------------------------
PAGE_W, PAGE_H = 1920, 1080

# ---- Palette (mirrors src/palette.py) -------------------------------------
CREAM = Color(240 / 255, 234 / 255, 214 / 255)
INK = Color(43 / 255, 34 / 255, 24 / 255)
HERO = Color(193 / 255, 95 / 255, 60 / 255)
FRIEND = Color(212 / 255, 165 / 255, 116 / 255)
BARRIER = Color(58 / 255, 46 / 255, 38 / 255)
GHOST = Color(125 / 255, 132 / 255, 113 / 255)
DIM_INK = Color(90 / 255, 78 / 255, 64 / 255)
PAPER_GRID = Color(228 / 255, 220 / 255, 198 / 255)
HAIRLINE = Color(180 / 255, 168 / 255, 145 / 255)


# ---- Fonts ----------------------------------------------------------------
SERIF = "Charter"
SERIF_BOLD = "Charter-Bold"
SANS = "AvenirNext"
SANS_MED = "AvenirNext-Med"


def _register_fonts():
    """Register Charter (serif) and Avenir Next (sans) from macOS system."""
    # macOS ships these as TTC collections. ReportLab needs subfontIndex.
    charter_path = "/System/Library/Fonts/Supplemental/Charter.ttc"
    avenir_path = "/System/Library/Fonts/Avenir Next.ttc"

    # Charter TTC contents (verified order):
    #   0: Charter Roman, 1: Italic, 2: Bold, 3: Bold Italic,
    #   4: Black, 5: Black Italic
    pdfmetrics.registerFont(TTFont(SERIF, charter_path, subfontIndex=0))
    pdfmetrics.registerFont(TTFont(SERIF_BOLD, charter_path, subfontIndex=2))

    # Avenir Next TTC: 0 Regular, 1 Italic, 2 Bold, 3 Bold Italic, 4 Medium, ...
    pdfmetrics.registerFont(TTFont(SANS, avenir_path, subfontIndex=0))
    pdfmetrics.registerFont(TTFont(SANS_MED, avenir_path, subfontIndex=4))


# ---- Layout helpers -------------------------------------------------------
MARGIN_X = 160
MARGIN_TOP = 140
MARGIN_BOTTOM = 110

def _paint_background(c: canvas.Canvas):
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)


def _paint_dot_grid(c: canvas.Canvas, step=48):
    c.setFillColor(PAPER_GRID)
    for y in range(step, PAGE_H, step):
        for x in range(step, PAGE_W, step):
            c.circle(x, y, 0.7, stroke=0, fill=1)


def _draw_running_header(c: canvas.Canvas, section: str, slide_n: int, total: int):
    """Chyron-style running head + progress bar at the bottom."""
    # Top-left section label
    c.setFillColor(DIM_INK)
    c.setFont(SANS_MED, 18)
    c.drawString(MARGIN_X, PAGE_H - 76, section.upper())

    # Hairline divider
    c.setStrokeColor(HAIRLINE)
    c.setLineWidth(0.9)
    c.line(MARGIN_X, PAGE_H - 96, PAGE_W - MARGIN_X, PAGE_H - 96)

    # Bottom-right progress
    track_w = 160
    x0 = PAGE_W - MARGIN_X - track_w
    y = 66
    c.setStrokeColor(DIM_INK)
    c.setLineWidth(0.9)
    c.line(x0, y, x0 + track_w, y)
    if total > 1:
        prog = (slide_n - 1) / (total - 1)
    else:
        prog = 0
    c.setFillColor(HERO)
    c.circle(x0 + track_w * prog, y, 5, stroke=0, fill=1)

    # Slide number
    c.setFont(SANS, 16)
    c.setFillColor(DIM_INK)
    c.drawString(MARGIN_X, 60, f"{slide_n:02d} / {total:02d}")


def _title(c: canvas.Canvas, text: str, y=PAGE_H - 220, size=84, color=INK):
    c.setFillColor(color)
    c.setFont(SERIF, size)
    c.drawString(MARGIN_X, y, text)


def _subtitle(c: canvas.Canvas, text: str, y=PAGE_H - 280, size=26):
    c.setFillColor(DIM_INK)
    c.setFont(SANS_MED, size)
    c.drawString(MARGIN_X, y, text.upper())


def _body(c: canvas.Canvas, text: str, y, size=32, color=INK,
          font=None, leading=None, x=MARGIN_X):
    if font is None:
        font = SERIF
    if leading is None:
        leading = size * 1.45
    c.setFillColor(color)
    c.setFont(font, size)
    for line in text.split("\n"):
        c.drawString(x, y, line)
        y -= leading
    return y


def _bullet(c: canvas.Canvas, text: str, y, size=32, color=INK,
            font=None, x=MARGIN_X, indent=36):
    if font is None:
        font = SERIF
    c.setFillColor(HERO)
    c.setFont(font, size)
    c.drawString(x, y, "·")
    c.setFillColor(color)
    c.drawString(x + indent, y, text)
    return y - size * 1.6


# ---- Decorative agent dot (matches film) ---------------------------------
def _agent_dot(c: canvas.Canvas, x, y, radius=14, color=HERO, halo=True):
    if halo:
        c.setFillColorRGB(color.red, color.green, color.blue, alpha=0.22)
        c.circle(x, y, radius * 2.2, stroke=0, fill=1)
        c.setFillColorRGB(color.red, color.green, color.blue, alpha=0.55)
        c.circle(x, y, radius * 1.4, stroke=0, fill=1)
    c.setFillColorRGB(color.red, color.green, color.blue, alpha=1.0)
    c.circle(x, y, radius, stroke=0, fill=1)


# ---- Assets ---------------------------------------------------------------
ASSETS = "slides/assets"
FRAMES = {
    "opening":      f"{ASSETS}/frames/opening.png",
    "together":     f"{ASSETS}/frames/b1_together.png",
    "separation":   f"{ASSETS}/frames/b2_separation.png",
    "deliberation": f"{ASSETS}/frames/b3_deliberation.png",
    "journey":      f"{ASSETS}/frames/b4_journey.png",
    "reunion":      f"{ASSETS}/frames/b5_reunion.png",
    "chyron":       f"{ASSETS}/frames/chyron.png",
}
LOGOS = {
    "python": f"{ASSETS}/logos/python.png",
    "numpy":  f"{ASSETS}/logos/numpy.png",
    "scipy":  f"{ASSETS}/logos/scipy.png",
    "ffmpeg": f"{ASSETS}/logos/ffmpeg.png",
    "github": f"{ASSETS}/logos/github.png",
}


def _framed_image(c, path, x, y, w, h, border=True):
    """Place a film frame with a thin hairline border."""
    c.drawImage(path, x, y, width=w, height=h, mask="auto")
    if border:
        c.setStrokeColor(HAIRLINE)
        c.setLineWidth(0.9)
        c.rect(x, y, w, h, stroke=1, fill=0)


# ===========================================================================
# Slide contents
# ===========================================================================

def slide_title(c, n, total):
    _paint_background(c)
    _paint_dot_grid(c)
    cx = PAGE_W // 2

    # Two agent dots flanking title
    _agent_dot(c, cx - 440, PAGE_H // 2 + 30, radius=22, color=HERO)
    _agent_dot(c, cx + 440, PAGE_H // 2 + 30, radius=22, color=FRIEND)

    # Title
    c.setFillColor(INK)
    c.setFont(SERIF, 130)
    title = "Intentional Rescue"
    tw = c.stringWidth(title, SERIF, 130)
    c.drawString(cx - tw / 2, PAGE_H // 2 + 4, title)

    # Footer line
    c.setStrokeColor(HAIRLINE)
    c.setLineWidth(0.9)
    c.line(cx - 320, 230, cx + 320, 230)

    c.setFillColor(DIM_INK)
    c.setFont(SANS_MED, 20)
    footer = "1st report — design of physically grounded communication system"
    fw = c.stringWidth(footer.upper(), SANS_MED, 20)
    c.drawString(cx - fw / 2, 184, footer.upper())

    c.setFont(SANS, 20)
    author = "Hairong Shi  ·  Keio University  ·  Spring 2026"
    aw = c.stringWidth(author, SANS, 20)
    c.drawString(cx - aw / 2, 138, author)


def slide_first_viewing(c, n, total):
    _paint_background(c)
    _paint_dot_grid(c)
    _draw_running_header(c, "first viewing", n, total)

    _title(c, "Play the film first.", y=PAGE_H - 220, size=80)

    # Hero frame, centred
    w, h = 960, 540
    fx = (PAGE_W - w) // 2
    fy = PAGE_H - 240 - h
    _framed_image(c, FRAMES["opening"], fx, fy, w, h)

    # Caption underneath
    c.setFillColor(DIM_INK)
    c.setFont(SERIF, 26)
    caption = "75 seconds. Two robots. A wall."
    cw = c.stringWidth(caption, SERIF, 26)
    c.drawString((PAGE_W - cw) // 2, fy - 50, caption)


def slide_cover_story(c, n, total):
    _paint_background(c)
    _paint_dot_grid(c)
    _draw_running_header(c, "cover story", n, total)

    _title(c, "The Rescue.", y=PAGE_H - 220, size=72)
    _subtitle(c, "Two robots, separated. One finds a way back.", y=PAGE_H - 280)

    beats = [
        ("Together",     FRAMES["together"],     "two robots breathe in the same room."),
        ("Separation",   FRAMES["separation"],   "a wall rises. Friend dims. Hero pauses."),
        ("Deliberation", FRAMES["deliberation"], "Hero considers two possible futures."),
        ("Journey",      FRAMES["journey"],      "Hero re-routes around a new wall."),
        ("Reunion",      FRAMES["reunion"],      "Hero arrives. They breathe together."),
    ]

    # 5 rows: label (left, 240) + thumb 240x135 + body
    y = PAGE_H - 450
    row_h = 128
    thumb_w, thumb_h = 240, 135
    label_x = MARGIN_X
    thumb_x = MARGIN_X + 260
    body_x = thumb_x + thumb_w + 40

    for label, framepath, body in beats:
        # label small caps
        c.setFillColor(HERO)
        c.setFont(SANS_MED, 26)
        c.drawString(label_x, y + 50, label.upper())
        # thumbnail
        _framed_image(c, framepath, thumb_x, y - 24, thumb_w, thumb_h)
        # body
        c.setFillColor(INK)
        c.setFont(SERIF, 32)
        c.drawString(body_x, y + 48, body)
        y -= row_h


def slide_intentional_behaviours(c, n, total):
    _paint_background(c)
    _paint_dot_grid(c)
    _draw_running_header(c, "intentional behaviours", n, total)

    _title(c, "Six hints, three beats.", y=PAGE_H - 220, size=66)
    _subtitle(c, "From dist-04, mapped to where the film shows it.",
              y=PAGE_H - 280)

    groups = [
        ("Throughout", FRAMES["together"],
         ["Tries to achieve a goal",
          "Models the other agent / self"]),
        ("Beat 3 — Deliberation", FRAMES["deliberation"],
         ["Acts consciously",
          "Simulates future worlds"]),
        ("Beat 4 — Journey", FRAMES["journey"],
         ["Persists; does not give up",
          "Focuses on the main target"]),
    ]

    thumb_w, thumb_h = 320, 180
    row_h = 210
    y = PAGE_H - 370

    for label, framepath, hints in groups:
        # thumbnail on the left
        _framed_image(c, framepath, MARGIN_X, y - thumb_h + 14, thumb_w, thumb_h)
        # right column: small-caps label and 2 hints
        rx = MARGIN_X + thumb_w + 60
        c.setFillColor(HERO)
        c.setFont(SANS_MED, 26)
        c.drawString(rx, y - 16, label.upper())
        c.setFillColor(INK)
        c.setFont(SERIF, 32)
        c.drawString(rx, y - 78, "·  " + hints[0])
        c.drawString(rx, y - 130, "·  " + hints[1])
        y -= row_h


def slide_two_layers(c, n, total):
    _paint_background(c)
    _paint_dot_grid(c)
    _draw_running_header(c, "two readings", n, total)

    _title(c, "Two readings, side by side.", y=PAGE_H - 220, size=64)
    _subtitle(c, "Outside: what you see.  ·  Inside: what the agent holds.",
              y=PAGE_H - 275)

    # Frame with chyron visible — left side, evidence of what we mean
    fw, fh = 720, 405
    fx = MARGIN_X
    fy = PAGE_H - 760
    _framed_image(c, FRAMES["deliberation"], fx, fy, fw, fh)
    c.setFillColor(DIM_INK)
    c.setFont(SANS_MED, 20)
    c.drawString(fx, fy - 36, "BEAT 3 — CAPTION READS “DESIRE: REACH THE FRIEND”")

    # Two short columns to the right
    col_x = MARGIN_X + fw + 80
    top_y = PAGE_H - 360

    c.setFillColor(HERO)
    c.setFont(SANS_MED, 26)
    c.drawString(col_x, top_y, "EXTERNAL — INTENTIONAL STANCE")
    c.setStrokeColor(HERO)
    c.setLineWidth(1.8)
    c.line(col_x, top_y - 16, col_x + 130, top_y - 16)
    c.setFillColor(INK)
    c.setFont(SERIF, 30)
    for i, line in enumerate([
        "The viewer sees discs and tells",
        "a story: she got hurt, he is",
        "going around to reach her.",
    ]):
        c.drawString(col_x, top_y - 58 - i * 44, line)
    c.setFillColor(DIM_INK)
    c.setFont(SERIF, 24)
    c.drawString(col_x, top_y - 208, "Dennett 1971.")

    top2 = top_y - 290
    c.setFillColor(FRIEND)
    c.setFont(SANS_MED, 26)
    c.drawString(col_x, top2, "INTERNAL — BELIEF / DESIRE / PLAN")
    c.setStrokeColor(FRIEND)
    c.setLineWidth(1.8)
    c.line(col_x, top2 - 16, col_x + 130, top2 - 16)
    c.setFillColor(INK)
    c.setFont(SERIF, 30)
    for i, line in enumerate([
        "The caption exposes what",
        "the agent holds: belief, desire,",
        "and the committed plan.",
    ]):
        c.drawString(col_x, top2 - 58 - i * 44, line)
    c.setFillColor(DIM_INK)
    c.setFont(SERIF, 24)
    c.drawString(col_x, top2 - 208, "Baker 2017 · Cohen & Levesque 1990.")


def slide_method(c, n, total):
    _paint_background(c)
    _paint_dot_grid(c)
    _draw_running_header(c, "method", n, total)

    _title(c, "How the film was made.", y=PAGE_H - 220, size=66)
    _subtitle(c, "Frames generated programmatically — no screen recording.",
              y=PAGE_H - 280)

    # Each row: [logo 64x64] LABEL  body
    items = [
        (LOGOS["python"], "Python + Pygame", "builds the scene and draws every frame."),
        (LOGOS["numpy"],  "NumPy + SciPy",   "post-processes the frames for the visual style."),
        (LOGOS["ffmpeg"], "imageio-ffmpeg",  "encodes the frame sequence as the final mp4."),
        (None,            "Typography",      "Charter + Avenir Next — film and deck share the faces."),
        (LOGOS["github"], "Code",            "github.com/nanase1025/intentional-rescue"),
    ]
    logo_size = 64
    label_x = MARGIN_X + logo_size + 36
    body_x = MARGIN_X + 500
    y = PAGE_H - 400
    row_h = 110

    for logo, label, body in items:
        if logo is not None:
            c.drawImage(logo, MARGIN_X, y - logo_size + 16,
                        width=logo_size, height=logo_size, mask="auto")
        c.setFillColor(HERO)
        c.setFont(SANS_MED, 26)
        c.drawString(label_x, y, label.upper())
        c.setFillColor(INK)
        c.setFont(SERIF, 32)
        c.drawString(body_x, y, body)
        y -= row_h


def slide_evaluate(c, n, total):
    _paint_background(c)
    _paint_dot_grid(c)
    _draw_running_header(c, "evaluate me on", n, total)

    _title(c, "What I would like evaluated.", y=PAGE_H - 230, size=68)
    _subtitle(c, "Three angles, in order of importance.", y=PAGE_H - 295)

    items = [
        ("Alignment.",
         "Does your external reading\n"
         "agree with the BDI caption at each beat?"),
        ("Restraint.",
         "Intention is conveyed without faces,\n"
         "language, or scored music."),
        ("Scope.",
         "Goal-directed individual action only —\n"
         "no communication, no Bayesian inference."),
    ]

    y = PAGE_H - 410
    for i, (head, body) in enumerate(items, 1):
        c.setFillColor(HERO)
        c.setFont(SERIF_BOLD, 42)
        c.drawString(MARGIN_X, y, f"{i}.")
        c.setFillColor(INK)
        c.setFont(SERIF_BOLD, 40)
        c.drawString(MARGIN_X + 70, y, head)
        yy = y - 56
        c.setFillColor(DIM_INK)
        c.setFont(SERIF, 30)
        for line in body.split("\n"):
            c.drawString(MARGIN_X + 70, yy, line)
            yy -= 42
        y = yy - 36


def slide_scope(c, n, total):
    _paint_background(c)
    _paint_dot_grid(c)
    _draw_running_header(c, "scope", n, total)

    _title(c, "What the film does not show.", y=PAGE_H - 230, size=68)
    _subtitle(c, "Drawing the perimeter is part of the design.",
              y=PAGE_H - 295)

    out = [
        ("No communication.",
         "joint attention sits later in the course."),
        ("No Bayesian inference.",
         "the agent is a finite plan, not a posterior."),
        ("No nested mentalising.",
         "Hero models the Friend's pose, not mind."),
        ("No physical grounding.",
         "no sensors — a thought-experiment, not a robot."),
    ]
    y = PAGE_H - 410
    for head, body in out:
        c.setFillColor(INK)
        c.setFont(SERIF_BOLD, 34)
        c.drawString(MARGIN_X, y, head)
        c.setFillColor(DIM_INK)
        c.setFont(SERIF, 28)
        c.drawString(MARGIN_X, y - 46, body)
        y -= 110


def slide_second_viewing(c, n, total):
    _paint_background(c)
    _paint_dot_grid(c)
    _draw_running_header(c, "second viewing", n, total)

    _title(c, "The film, again.", y=PAGE_H - 220, size=80)

    # Hero frame — reunion
    w, h = 1040, 585
    fx = (PAGE_W - w) // 2
    fy = PAGE_H - 250 - h
    _framed_image(c, FRAMES["reunion"], fx, fy, w, h)


def slide_references(c, n, total):
    _paint_background(c)
    _paint_dot_grid(c)
    _draw_running_header(c, "references", n, total)

    _title(c, "Reading behind the film.", y=PAGE_H - 230, size=68)
    _subtitle(c, "All on the syllabus.", y=PAGE_H - 295)

    refs = [
        "Dennett.  Intentional Systems.  J. Phil. 68, 1971.",
        "Cohen & Levesque.  Intention is Choice with",
        "    Commitment.  Artif. Intell. 42, 1990.",
        "Baker, Jara-Ettinger, Saxe & Tenenbaum.",
        "    Rational quantitative attribution of beliefs,",
        "    desires and percepts.  Nat. Hum. Behav. 1, 2017.",
    ]
    y = PAGE_H - 400
    c.setFillColor(INK)
    c.setFont(SERIF, 28)
    for line in refs:
        c.drawString(MARGIN_X, y, line)
        y -= 46

    # thank-you
    c.setFillColor(DIM_INK)
    c.setFont(SANS_MED, 22)
    c.drawString(MARGIN_X, 160, "THANK YOU.")


# ===========================================================================

SLIDES = [
    slide_title,
    slide_first_viewing,
    slide_cover_story,
    slide_intentional_behaviours,
    slide_two_layers,
    slide_method,
    slide_evaluate,
    slide_second_viewing,
    slide_references,
]


def build(out_path: str = "slides/intentional_rescue_slides.pdf"):
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    _register_fonts()
    c = canvas.Canvas(out_path, pagesize=(PAGE_W, PAGE_H))
    total = len(SLIDES)
    for i, fn in enumerate(SLIDES, start=1):
        fn(c, i, total)
        c.showPage()
    c.save()
    print(f"[slides] wrote {out_path}")


if __name__ == "__main__":
    build()
