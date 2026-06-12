# Intentional Rescue

A short animated film for the 1st report of *Design of Physically Grounded Communication System* (Keio Univ., Prof. Michita Imai, 2026 Spring).

The brief: **make a video in which an object or objects move as if they had intention** (> 1 min).

This project takes the brief through the lens of Dennett's three stances — physical, design, **intentional** — and Baker et al.'s Bayesian Theory of Mind. The cover story is *The Rescue*: one small robot must reach another after the world separates them.

## Cover story — "The Rescue"

| t (s) | Beat | Intentional behaviour shown |
|------:|------|-----------------------------|
| 0–10  | **Together.** Two robots breathe together in a warm room. | — |
| 10–20 | **Separation.** A wall rises. Friend dims. Hero pauses. | — |
| 20–35 | **Deliberation.** Belief & desire fade in. Ghost paths flicker as Hero simulates options. | future simulation, belief/desire |
| 35–55 | **Journey.** Hero ignores a drifting distractor and re-plans when a new barrier rises. | focus, goal persistence |
| 55–75 | **Reunion.** Hero reaches Friend. They breathe together again. | — |

The viewer naturally attributes intention from the outside (the intentional stance); a low-key chyron exposes the underlying belief / desire / plan so both layers can be read together.

A longer reading of the film — beat-by-beat mapping to Imai's intention hints, Dennett's three stances, and BToM — is in [`docs/CONCEPT.md`](docs/CONCEPT.md).

## Visual language

| | |
|---|---|
| Background | `#F0EAD6` warm cream |
| Ink | `#2B2218` deep warm black |
| Hero | `#C15F3C` terracotta |
| Friend | `#D4A574` soft gold |
| Barrier | `#3A2E26` dark umber |
| Ghost path | `#7D8471` muted sage |
| Title type | serif (Source Serif / IBM Plex Serif) |
| Chyron type | sans, small caps (Inter / IBM Plex Sans) |

Anti-aliased shapes, soft bloom, motion trails, eased curves, generous negative space — an editorial / announcement-style register.

## Running

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
python -m src.main           # outputs output/intentional_rescue.mp4
python -m src.smoke          # short POC verifying the visual style
```

The pipeline renders frames headlessly with Pygame, applies bloom + trail post-processing with NumPy / SciPy, and writes mp4 via imageio-ffmpeg. Nothing is screen-recorded.

## TODO

- [x] Decide concept, story, and visual language
- [x] Scaffold project, dependencies, repo
- [ ] Rendering pipeline POC (cream BG + glowing dot + trail + bloom)
- [ ] Beat 1 — Together
- [ ] Beat 2 — Separation
- [ ] Beat 3 — Deliberation (belief / desire chyron, ghost paths)
- [ ] Beat 4 — Journey (distractor ignored, barrier re-plan)
- [ ] Beat 5 — Reunion
- [ ] Title card and end card
- [ ] Final colour grade and audio (silent OK)
- [ ] 5-minute English presentation slide
- [ ] Submit video + slide to K LMS (deadline 2026-06-15 23:59)

## Repo notes

- Course slides live one directory up under `slide/` and are **deliberately excluded** from this repo (course materials, not mine to publish).
- Final mp4 is committed under `output/` once it lands.
- `slides/` here is for *my* presentation, not the lecturer's.

## Reading behind the project

- Dennett, *Intentional Systems*, J. Phil. 68 (1971).
- Baker, Jara-Ettinger, Saxe, Tenenbaum, *Rational quantitative attribution of beliefs, desires and percepts in human mentalizing*, Nat. Hum. Behav. 1, 64 (2017).
- Heider & Simmel, *An Experimental Study of Apparent Behavior*, Am. J. Psych. 57 (1944).
- Epley, Waytz, Cacioppo, *On Seeing Human*, Psych. Review 114 (2007).
