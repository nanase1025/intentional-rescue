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

    # Subtitle
    c.setFillColor(DIM_INK)
    c.setFont(SANS_MED, 28)
    sub = "a study in stance"
    sw = c.stringWidth(sub.upper(), SANS_MED, 28)
    c.drawString(cx - sw / 2, PAGE_H // 2 - 70, sub.upper())

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

    _title(c, "Play the film first.", y=PAGE_H - 300, size=96)
    _subtitle(c, "No explanation. Let the room read it.", y=PAGE_H - 380, size=28)

    c.setFillColor(DIM_INK)
    c.setFont(SERIF, 34)
    note = ("75 seconds. Two robots. A wall.\n"
            "We attribute intention to the shapes before any\n"
            "commentary — that attribution is the subject of the talk.")
    y = PAGE_H - 500
    for line in note.split("\n"):
        c.drawString(MARGIN_X, y, line)
        y -= 52


def slide_cover_story(c, n, total):
    _paint_background(c)
    _paint_dot_grid(c)
    _draw_running_header(c, "cover story", n, total)

    _title(c, "The Rescue.", y=PAGE_H - 240)
    _subtitle(c, "Two robots, separated. One finds a way back.", y=PAGE_H - 310)

    y = PAGE_H - 430
    beats = [
        ("Together", "two robots breathe in the same room."),
        ("Separation", "a wall rises. Friend dims. Hero pauses."),
        ("Deliberation", "Hero considers two possible futures."),
        ("Journey", "Hero ignores a sparkle, re-routes around a new wall."),
        ("Reunion", "Hero arrives. Friend brightens. They breathe together."),
    ]
    for label, body in beats:
        c.setFillColor(HERO)
        c.setFont(SANS_MED, 22)
        c.drawString(MARGIN_X, y, label.upper())
        c.setFillColor(INK)
        c.setFont(SERIF, 34)
        c.drawString(MARGIN_X + 320, y, body)
        y -= 88


def slide_intentional_behaviours(c, n, total):
    _paint_background(c)
    _paint_dot_grid(c)
    _draw_running_header(c, "intentional behaviours", n, total)

    _title(c, "Six hints, five beats.", y=PAGE_H - 230, size=72)
    _subtitle(c, "From dist-04, mapped to where the film shows it.",
              y=PAGE_H - 295)

    rows = [
        ("Tries to achieve a goal", "Throughout. Hero moves only toward Friend."),
        ("Acts consciously", "Beat 3. Hero pauses before moving."),
        ("Persists; does not give up", "Beat 4. Wall 2 rises; Hero re-plans."),
        ("Focuses on the main target", "Beat 4. The sparkle drifts past, ignored."),
        ("Simulates future worlds", "Beat 3. Two ghost paths flicker."),
        ("Models other agent / self", "Throughout. Plan is against Friend's pose."),
    ]

    y = PAGE_H - 410
    col1 = MARGIN_X
    col2 = MARGIN_X + 720
    # column headers
    c.setFillColor(DIM_INK)
    c.setFont(SANS_MED, 18)
    c.drawString(col1, y + 44, "INTENTION HINT")
    c.drawString(col2, y + 44, "WHERE IT APPEARS")
    c.setStrokeColor(HAIRLINE)
    c.setLineWidth(0.9)
    c.line(col1, y + 28, PAGE_W - MARGIN_X, y + 28)

    for hint, where in rows:
        c.setFillColor(INK)
        c.setFont(SERIF_BOLD, 28)
        c.drawString(col1, y, hint)
        c.setFillColor(INK)
        c.setFont(SERIF, 28)
        c.drawString(col2, y, where)
        y -= 78


def slide_two_layers(c, n, total):
    _paint_background(c)
    _paint_dot_grid(c)
    _draw_running_header(c, "two readings", n, total)

    _title(c, "Two readings, side by side.", y=PAGE_H - 230, size=72)
    _subtitle(c, "The viewer attributes; the chyron confirms.",
              y=PAGE_H - 295)

    # Two columns
    col_w = (PAGE_W - 2 * MARGIN_X - 100) / 2
    left_x = MARGIN_X
    right_x = MARGIN_X + col_w + 100
    top_y = PAGE_H - 410

    def col(title, body, x, accent_color):
        c.setFillColor(accent_color)
        c.setFont(SANS_MED, 20)
        c.drawString(x, top_y + 44, title.upper())
        c.setStrokeColor(accent_color)
        c.setLineWidth(1.8)
        c.line(x, top_y + 26, x + 100, top_y + 26)
        c.setFillColor(INK)
        c.setFont(SERIF, 28)
        yy = top_y - 24
        for line in body.split("\n"):
            c.drawString(x, yy, line)
            yy -= 46
        return yy

    col("External — intentional stance",
        "The viewer sees discs\n"
        "and tells a story: she\n"
        "got hurt, he is going\n"
        "around to reach her.\n\n"
        "Heider & Simmel, 1944.\n"
        "Dennett, 1971.",
        left_x, HERO)
    col("Internal — belief / desire / plan",
        "A chyron exposes what\n"
        "the agent holds:\n"
        "  belief: friend is across\n"
        "  desire: reach the friend\n"
        "  plan: go above\n\n"
        "Baker et al., 2017.",
        right_x, FRIEND)

    # Bottom: the alignment claim
    c.setFillColor(DIM_INK)
    c.setFont(SERIF, 26)
    c.drawString(MARGIN_X, 170,
                 "The point is the alignment:")
    c.drawString(MARGIN_X, 130,
                 "what the chyron names, the viewer's reading also names.")


def slide_method(c, n, total):
    _paint_background(c)
    _paint_dot_grid(c)
    _draw_running_header(c, "method", n, total)

    _title(c, "How the film was made.", y=PAGE_H - 230, size=72)
    _subtitle(c, "Frames generated programmatically — no screen recording.",
              y=PAGE_H - 295)

    y = PAGE_H - 420
    items = [
        ("Pygame", "anti-aliased discs and lines."),
        ("NumPy / SciPy", "bloom, motion trails, paper grain."),
        ("imageio-ffmpeg", "streams frames to mp4 — 75 s at 30 fps."),
        ("Typography", "Charter + Avenir Next (deck and film share the same faces)."),
        ("Code", "github.com/nanase1025/intentional-rescue"),
    ]
    for label, body in items:
        c.setFillColor(HERO)
        c.setFont(SANS_MED, 22)
        c.drawString(MARGIN_X, y, label.upper())
        c.setFillColor(INK)
        c.setFont(SERIF, 30)
        yy = y
        for line in body.split("\n"):
            c.drawString(MARGIN_X + 380, yy, line)
            yy -= 44
        y = yy - 48


def slide_evaluate(c, n, total):
    _paint_background(c)
    _paint_dot_grid(c)
    _draw_running_header(c, "evaluate me on", n, total)

    _title(c, "What I would like evaluated.", y=PAGE_H - 230, size=68)
    _subtitle(c, "Three angles, in order of importance.", y=PAGE_H - 295)

    items = [
        ("Alignment.",
         "Does your external reading\n"
         "agree with the BDI chyron at each beat?"),
        ("Restraint.",
         "Intention is conveyed without faces,\n"
         "language, or scored music."),
        ("Scope.",
         "I stop at goal-directed individual action.\n"
         "Communication is deliberately out of frame."),
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

    _title(c, "Watch it again.", y=PAGE_H - 300, size=96)
    _subtitle(c, "Now the labels are in your head.", y=PAGE_H - 380, size=28)

    c.setFillColor(DIM_INK)
    c.setFont(SERIF, 34)
    note = ("Same 75 seconds. Same shapes.\n"
            "The reading shifts — each attribution\n"
            "is now tied to a belief, desire, or plan.")
    y = PAGE_H - 500
    for line in note.split("\n"):
        c.drawString(MARGIN_X, y, line)
        y -= 52


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
        "Heider & Simmel.  Apparent Behavior.",
        "    Am. J. Psych. 57, 1944.",
        "Epley, Waytz & Cacioppo.  On Seeing Human.",
        "    Psych. Review 114, 2007.",
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
    slide_scope,
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
