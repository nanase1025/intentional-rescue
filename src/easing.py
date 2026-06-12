"""Easing primitives. All take t in [0, 1] and return f(t) in [0, 1]."""
import math


def linear(t): return t


def ease_in_cubic(t): return t * t * t


def ease_out_cubic(t):
    u = 1 - t
    return 1 - u * u * u


def ease_in_out_cubic(t):
    if t < 0.5:
        return 4 * t * t * t
    u = 2 * t - 2
    return 0.5 * u * u * u + 1


def ease_in_out_sine(t):
    return -(math.cos(math.pi * t) - 1) / 2


def ease_out_back(t, c=1.70158):
    u = t - 1
    return 1 + (c + 1) * u * u * u + c * u * u


def smoothstep(edge0, edge1, x):
    t = max(0.0, min(1.0, (x - edge0) / max(edge1 - edge0, 1e-9)))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def lerp_color(c1, c2, t):
    return (
        int(lerp(c1[0], c2[0], t)),
        int(lerp(c1[1], c2[1], t)),
        int(lerp(c1[2], c2[2], t)),
    )
