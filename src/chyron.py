"""Lower-third 'documentary' chyron: BELIEF / DESIRE / PLAN labels
fade in only at intentional moments, then fade out. Never a heavy HUD.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

import pygame

from . import palette
from .easing import smoothstep
from .render import font, font_serif


@dataclass
class ChyronEntry:
    label: str       # small caps, e.g. "BELIEF"
    body: str        # serif body, e.g. "friend is on the other side"
    show_at: float
    hide_at: float
    fade: float = 0.6   # seconds of fade in/out


def draw_chyron(renderer, entries: List[ChyronEntry], t: float,
                screen_w: int, screen_h: int):
    visible = []
    for e in entries:
        a = _alpha(e, t)
        if a > 0:
            visible.append((e, a))
    if not visible:
        return

    label_f = font(20)
    body_f = font_serif(38)
    line_h = 80
    top = screen_h - 60 - line_h * len(visible)
    left = 110

    # tiny vertical accent line
    accent_x = left - 28
    accent_top = top - 6
    accent_bot = top + line_h * len(visible) - 18
    accent_alpha = max((a for _, a in visible), default=0)
    pygame.draw.line(renderer.surface,
                     (*palette.DIM_INK, int(accent_alpha * 180)),
                     (accent_x, accent_top), (accent_x, accent_bot), 1)

    for i, (e, a) in enumerate(visible):
        y = top + i * line_h
        renderer.text(renderer.surface, e.label.upper(), (left, y),
                      label_f, color=palette.DIM_INK, alpha=int(a * 200))
        renderer.text(renderer.surface, e.body, (left, y + 28),
                      body_f, color=palette.INK, alpha=int(a * 255))


def _alpha(e: ChyronEntry, t: float) -> float:
    if t < e.show_at - e.fade or t > e.hide_at + e.fade:
        return 0.0
    if t < e.show_at:
        return smoothstep(e.show_at - e.fade, e.show_at, t)
    if t > e.hide_at:
        return 1 - smoothstep(e.hide_at, e.hide_at + e.fade, t)
    return 1.0


@dataclass
class TitleCard:
    title: str
    subtitle: str
    show_at: float
    hide_at: float
    fade: float = 1.0
    size: str = "large"     # "large" = poster, "small" = end-credit


def draw_title_card(renderer, card: TitleCard, t: float,
                    screen_w: int, screen_h: int):
    a = _alpha(ChyronEntry("", "", card.show_at, card.hide_at, card.fade), t)
    if a <= 0:
        return
    if card.size == "small":
        title_f = font_serif(40)
        sub_f = font(14)
        cy = 90
        sub_dy = 38
    else:
        title_f = font_serif(64)
        sub_f = font(18)
        cy = 168
        sub_dy = 56
    renderer.text(renderer.surface, card.title, (screen_w // 2, cy),
                  title_f, color=palette.INK, alpha=int(a * 255),
                  anchor="center")
    if card.subtitle:
        renderer.text(renderer.surface, card.subtitle.upper(),
                      (screen_w // 2, cy + sub_dy),
                      sub_f, color=palette.DIM_INK, alpha=int(a * 200),
                      anchor="center")
