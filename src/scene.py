"""The 75-second film, beat by beat.

Stage layout (1280 × 720):
              0           640          1280
        0  ┌────────────────────────────────┐
            │   title area                   │
       120 │ . . . . . . . . . . . . . . . .│ stage_top
            │                                │
       360 │   Hero            Friend         │ stage_mid
            │                                │
       580 │ . . . . . . . . . . . . . . . .│ stage_bot
            │   chyron area                  │
       720 └────────────────────────────────┘

The Hero travels left → right; a wall rises in the middle; Hero deliberates
between an upper and lower detour, commits, ignores a distractor sparkle,
re-plans around a second wall, reaches the Friend.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import List

import pygame

from . import palette
from .agents import Agent, chain_at_length, chain_length, lerp_pos
from .chyron import ChyronEntry, TitleCard, draw_chyron, draw_title_card
from .easing import (ease_in_out_cubic, ease_in_out_sine, ease_out_cubic,
                     lerp, smoothstep)
from .render import Renderer, RenderConfig, font, font_serif
from .world import Barrier, Distractor


W = 1280
H = 720
STAGE_TOP = 120
STAGE_BOT = 580

HERO_HOME = (310, 360)
FRIEND_HOME = (970, 360)

# Beat timing (seconds)
B_TOGETHER = (0.0, 10.0)
B_SEPARATE = (10.0, 20.0)
B_DELIBER = (20.0, 35.0)
B_JOURNEY = (35.0, 55.0)
B_REUNION = (55.0, 75.0)

DURATION = 75.0

# Walls
WALL1 = Barrier(x=640, y_bottom=580, y_top=160, width=24, rise_at=10.4, rise_dur=1.0)
WALL2 = Barrier(x=860, y_bottom=350, y_top=110, width=22, rise_at=43.5, rise_dur=0.9)

# Distractor (after Hero commits to path)
DISTRACT = Distractor(start=(1180, 200), end=(140, 240),
                      t0=37.5, t1=43.0)

# Hero path waypoints
UPPER_PATH = [(310, 360), (450, 170), (760, 170), (970, 360)]
LOWER_PATH = [(310, 360), (450, 555), (760, 555), (970, 360)]
# After wall 2 forces a re-plan, the upper path can't get through at x=860;
# Hero detours downward and arcs around.
# After wall 2 forces a re-plan, Hero detours below it and parks
# left-of-Friend at the parked position so the reunion reads clearly.
PARKED = (FRIEND_HOME[0] - 58, FRIEND_HOME[1] + 4)
REROUTE = [(760, 170), (810, 305), (820, 470), (900, 505), PARKED]


# ---------------------------------------------------------------------------

def render_film(out_path: str, fps: int = 30, width: int = W, height: int = H):
    import imageio.v2 as imageio

    cfg = RenderConfig(width=width, height=height, fps=fps,
                       trail_decay=0.93, bloom_sigma=12.0, bloom_strength=0.55)
    r = Renderer(cfg)

    hero = Agent("Hero", HERO_HOME, palette.HERO, radius=15.5,
                 breath_speed=0.45, breath_amp=1.4, glow_alpha=70, phase=0.0)
    friend = Agent("Friend", FRIEND_HOME, palette.FRIEND, radius=15.5,
                   breath_speed=0.42, breath_amp=1.5, glow_alpha=70, phase=2.2)

    chyrons = build_chyrons()
    start_card = TitleCard("Intentional Rescue",
                           "a study in stance", show_at=0.4, hide_at=4.0,
                           fade=1.2)
    end_card = TitleCard("Intentional Rescue",
                         "a study in stance", show_at=71.6, hide_at=75.0,
                         fade=1.2, size="small")

    n_frames = int(round(DURATION * fps))

    writer = imageio.get_writer(out_path, fps=fps, codec="libx264",
                                quality=8, macro_block_size=1,
                                pixelformat="yuv420p")

    try:
        for i in range(n_frames):
            t = i / fps
            r.begin_frame()

            # subtle paper grid (drawn each frame so it sits below everything)
            _paper_grid(r, t)

            _update_and_draw_world(r, t, hero, friend)

            draw_chyron(r, chyrons, t, width, height)
            draw_title_card(r, start_card, t, width, height)
            draw_title_card(r, end_card, t, width, height)

            # progress dot in the corner — a tiny editorial flourish
            _progress_mark(r, t, width, height)

            frame = r.composite_frame()
            writer.append_data(frame)

            if i % 30 == 0:
                print(f"[scene] frame {i}/{n_frames}  t={t:5.1f}s")
    finally:
        writer.close()

    print(f"[scene] wrote {out_path}")


# ---------------------------------------------------------------------------

def build_chyrons() -> List[ChyronEntry]:
    return [
        # Deliberation beat
        ChyronEntry("Belief", "friend is on the other side",
                    show_at=21.0, hide_at=26.5, fade=0.7),
        ChyronEntry("Desire", "reach the friend",
                    show_at=24.5, hide_at=30.5, fade=0.7),
        ChyronEntry("Plan", "go above",
                    show_at=29.5, hide_at=34.5, fade=0.7),
        # Journey beat — re-planning around wall 2
        ChyronEntry("Belief", "new barrier ahead",
                    show_at=45.0, hide_at=49.5, fade=0.6),
        ChyronEntry("Plan", "re-routing",
                    show_at=47.5, hide_at=52.5, fade=0.6),
    ]


# ---------------------------------------------------------------------------

def _update_and_draw_world(r: Renderer, t: float, hero: Agent, friend: Agent):
    # ----- Friend dimming during Separation, brightening at Reunion ---------
    if t < 14.0:
        friend.dim = 0.0
    elif t < 18.0:
        friend.dim = smoothstep(14.0, 18.0, t) * 0.75
    elif t < 64.0:
        friend.dim = 0.75
    elif t < 68.0:
        friend.dim = 0.75 * (1 - smoothstep(64.0, 68.0, t))
    else:
        friend.dim = 0.0

    # ----- Hero position and trail -----------------------------------------
    hero.pos = _hero_position(t)
    _stamp_hero_trail(r, hero, t)

    # ----- Ghost paths during Deliberation ---------------------------------
    if 21.5 <= t <= 32.5:
        _draw_ghost_paths(r, t)

    # ----- Walls ------------------------------------------------------------
    WALL1.draw(r, t)
    WALL2.draw(r, t)

    # ----- Distractor sparkle ----------------------------------------------
    DISTRACT.draw(r, t)

    # ----- Agents themselves -----------------------------------------------
    friend.draw(r, t)
    hero.draw(r, t)

    # ----- Soft connection line between agents at the reunion --------------
    if t > 65.0:
        a = smoothstep(65.0, 68.0, t)
        _draw_breath_link(r, hero, friend, t, a)
    elif t < 9.5:
        # Beat 1: a quiet breath link between the pair, foreshadowing what
        # the wall will sever.
        a = smoothstep(2.5, 6.0, t) * (1 - smoothstep(8.5, 9.5, t))
        _draw_breath_link(r, hero, friend, t, a * 0.55)

    # ----- Friend wakeup pulse (a single soft halo bloom at t=64.5) ---------
    if 64.0 <= t <= 67.0:
        u = smoothstep(64.0, 67.0, t)
        # ring of growing radius, fading
        ring_r = 18 + 70 * u
        ring_a = int(160 * (1 - u))
        r.soft_halo(r.surface, friend.pos, ring_r, palette.FRIEND,
                    alpha=ring_a, layers=3)


def _hero_position(t: float) -> tuple[float, float]:
    """Drive Hero through the timeline as a piecewise motion."""
    if t < 10.5:
        # gentle idle bob
        bob = math.sin(t * 0.7) * 4
        return (HERO_HOME[0], HERO_HOME[1] + bob)

    if t < 14.0:
        # paused, looking at the wall — tiny rocking
        rock = math.sin((t - 10.5) * 1.3) * 1.8
        return (HERO_HOME[0] + rock, HERO_HOME[1])

    if t < 35.0:
        # holding still while deliberating, slight breath bob
        bob = math.sin((t - 14.0) * 0.45) * 2
        return (HERO_HOME[0], HERO_HOME[1] + bob)

    # ----- Journey: move along upper path until wall 2 forces a detour -----
    # Plan: travel upper path; just before wall 2 we'll arc into the reroute.
    # We use arc-length parameterisation so the speed feels steady.
    if t < 44.5:
        # 35.0 → 44.5 = 9.5 s along upper path, but we'll only traverse
        # the segment up to (760, 170), then halt briefly at wall 2.
        seg = [UPPER_PATH[0], UPPER_PATH[1], UPPER_PATH[2]]
        L = chain_length(seg)
        u = smoothstep(35.0, 44.5, t)
        # ease so motion looks deliberate
        u = ease_in_out_cubic(u)
        return chain_at_length(seg, u * L)

    if t < 46.5:
        # paused in front of wall 2
        rock = math.sin((t - 44.5) * 1.6) * 1.4
        base = UPPER_PATH[2]
        return (base[0] + rock, base[1])

    if t < 60.5:
        # follow REROUTE
        L = chain_length(REROUTE)
        u = smoothstep(46.5, 60.5, t)
        u = ease_in_out_cubic(u)
        return chain_at_length(REROUTE, u * L)

    # Reunion: settle next to Friend with a small breath
    bob = math.sin((t - 60.5) * 0.55) * 3
    return (PARKED[0], PARKED[1] + bob)


def _stamp_hero_trail(r: Renderer, hero: Agent, t: float):
    """Only stamp while Hero is actually travelling — idle/wait frames
    shouldn't leave persistent marks, otherwise the room looks busy."""
    moving = (35.0 < t < 44.5) or (46.5 < t < 60.5)
    if not moving:
        return
    p = hero.pos

    def stamp(layer):
        r.soft_halo(layer, p, 10, palette.HERO, alpha=55, layers=5)
        r.aacircle(layer, p, 5, palette.HERO, alpha=110)
    r.stamp_trail(stamp)


# ---------------------------------------------------------------------------

def _draw_ghost_paths(r: Renderer, t: float):
    """Two candidate routes flicker as Hero simulates. The chosen one
    eventually firms up while the other fades."""
    # symmetric flicker in [21.5, 28.5], then commit upper from 28.5 to 32.5
    if t < 28.5:
        flicker = (math.sin(t * 11.0) * 0.5 + 0.5)
        upper_a = 110 + int(70 * flicker)
        lower_a = 110 + int(70 * (1 - flicker))
    else:
        commit = smoothstep(28.5, 32.5, t)
        upper_a = int(180 + 60 * commit)
        lower_a = int(180 * (1 - commit))

    _draw_path(r, UPPER_PATH, upper_a, weight=2)
    _draw_path(r, LOWER_PATH, lower_a, weight=2)


def _draw_path(r: Renderer, points, alpha: int, weight: int = 2):
    if alpha <= 4:
        return
    # dashed-ish: draw as soft segments with light circles at joints
    for a, b in zip(points, points[1:]):
        pygame.draw.aaline(r.surface,
                           (*palette.GHOST, alpha),
                           a, b)
        # a thicker but lower-alpha overlay for body
        pygame.draw.line(r.surface,
                         (*palette.GHOST, max(0, alpha - 60)),
                         a, b, weight)
    for p in points:
        r.aacircle(r.surface, p, 3, palette.GHOST, alpha=alpha)


def _draw_breath_link(r: Renderer, hero: Agent, friend: Agent,
                      t: float, alpha_mult: float):
    """A breathing line between the reunited pair."""
    pulse = 0.5 + 0.5 * math.sin((t - 65.0) * 1.4)
    a = int(110 * alpha_mult * (0.4 + 0.6 * pulse))
    pygame.draw.aaline(r.surface,
                       (*palette.HERO, a),
                       hero.pos, friend.pos)


# ---------------------------------------------------------------------------

def _paper_grid(r: Renderer, t: float):
    """Very faint warm dots, dot-grid, for an editorial-paper feel."""
    step = 36
    color = (*palette.PAPER_GRID, 110)
    for y in range(step, H, step):
        for x in range(step, W, step):
            pygame.gfxdraw.pixel(r.surface, x, y, color)


def _progress_mark(r: Renderer, t: float, w: int, h: int):
    """Tiny progress dot in the bottom-right corner."""
    pad = 28
    radius = 3
    track_w = 90
    x0 = w - pad - track_w
    y = h - pad
    # track
    pygame.draw.aaline(r.surface, (*palette.DIM_INK, 80),
                       (x0, y), (x0 + track_w, y))
    # marker
    prog = t / DURATION
    mx = int(x0 + track_w * prog)
    r.aacircle(r.surface, (mx, y), radius, palette.HERO, alpha=200)
