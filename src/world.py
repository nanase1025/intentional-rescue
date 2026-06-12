"""World objects: barriers that rise from the floor, and a distractor
particle that drifts across the stage as a temptation the Hero ignores.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import pygame

from . import palette
from .easing import ease_in_out_cubic, ease_out_back, lerp, smoothstep


@dataclass
class Barrier:
    """A rectangle that rises from below the stage with an ease-out-back.

    rise_at: time (s) when the barrier starts to rise.
    rise_dur: seconds it takes to fully rise.
    """
    x: float
    y_bottom: float
    y_top: float
    width: float
    rise_at: float
    rise_dur: float = 0.9

    def progress(self, t: float) -> float:
        return smoothstep(self.rise_at, self.rise_at + self.rise_dur, t)

    def height_now(self, t: float) -> float:
        p = self.progress(t)
        if p <= 0:
            return 0
        return (self.y_bottom - self.y_top) * ease_out_back(p, 1.1)

    def draw(self, renderer, t: float):
        h = self.height_now(t)
        if h <= 0.5:
            return
        # subtle shadow + body
        x = int(self.x - self.width / 2)
        w = int(self.width)
        y = int(self.y_bottom - h)
        h = int(h)
        # soft shadow
        shadow = pygame.Surface((w + 24, h + 24), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (*palette.BARRIER, 60),
                         (12, 12, w, h), border_radius=8)
        renderer.surface.blit(shadow, (x - 12, y - 12))
        # body
        renderer.filled_rounded_rect(renderer.surface,
                                     (x, y, w, h),
                                     palette.BARRIER, radius=8)


@dataclass
class Distractor:
    """A small shiny particle drifting across the stage. The Hero must
    not be 'pulled' by it — this is the focus test."""
    start: tuple[float, float]
    end: tuple[float, float]
    t0: float
    t1: float
    color: tuple[int, int, int] = palette.GHOST

    def pos(self, t: float) -> tuple[float, float] | None:
        if t < self.t0 or t > self.t1:
            return None
        u = (t - self.t0) / (self.t1 - self.t0)
        u = ease_in_out_cubic(u)
        return (lerp(self.start[0], self.end[0], u),
                lerp(self.start[1], self.end[1], u))

    def alpha(self, t: float) -> int:
        if t < self.t0 or t > self.t1:
            return 0
        u = (t - self.t0) / (self.t1 - self.t0)
        # fade in then out
        fade = 1 - abs(2 * u - 1)
        return int(220 * fade)

    def draw(self, renderer, t: float):
        p = self.pos(t)
        if p is None:
            return
        a = self.alpha(t)
        # twinkle: small core, pulsing halo
        twink = 0.5 + 0.5 * math.sin(t * 8.0)
        renderer.soft_halo(renderer.surface, p, 9 + twink * 4,
                           (240, 220, 175), alpha=int(a * 0.6), layers=5)
        renderer.aacircle(renderer.surface, p, 3.5,
                          (240, 220, 175), alpha=a)
