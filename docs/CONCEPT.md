# Reading the Film

A guide to what *Intentional Rescue* is trying to show, and how each beat maps to the concepts Prof. Imai laid out in the first four lectures.

## The brief, in one line

> *Make a video in which an object or objects move as if they had intention. > 1 min.*

The film answers this twice. First, externally: the viewer watches two small geometric robots and naturally narrates a story of separation and rescue — the **intentional stance** in action, in the spirit of Heider & Simmel (1944). Second, internally: a low-key documentary chyron exposes the Hero's belief, desire, and plan — the **BDI** primitives behind that narration. The pedagogical point sits in the gap between those two readings: when intention is attributed from the outside, it is not an illusion; it tracks a structure inside.

## The six intentional behaviours, beat by beat

Prof. Imai's hints in `dist-04-dennet-stance` give a six-point definition of what an agent shows when it has intention. The film hits each one on a specific beat:

| Hint | Where it appears | How it reads |
|---|---|---|
| **Tries to achieve a goal** | Throughout | The Hero's whole trajectory is goal-directed: it always moves toward where the Friend is. Friend's dimming makes the goal feel urgent. |
| **Does it consciously** | Beat 3 — Deliberation | The Hero pauses before moving. Two ghost paths flicker as candidate futures. The pause is the conscious moment. |
| **Does not stop pursuing the goal easily** | Beat 4 — Journey, late | When the second wall rises and blocks the chosen route, the Hero does not return home. It pauses, re-plans, and detours. This is Cohen's *persistent goal* in cartoon form. |
| **Focuses on the main target** | Beat 4 — Journey, mid | A gold distractor sparkle drifts past the Hero's line of travel. The Hero does not deviate. Salient but irrelevant. |
| **Simulates future worlds** | Beat 3 — Deliberation | The two ghost paths *are* the future-world simulation, made visible. One commits, the other fades. |
| **Simulated worlds include the other agent / self** | Throughout the Journey | The chyron reads BELIEF: *friend is on the other side.* The Hero's plan is computed against the Friend's location, not against the empty room. |

## Two readings in parallel

The film deliberately runs two interpretive layers at once.

**External — the intentional stance.**
The viewer sees two coloured discs in a cream room and produces a narrative: *the one on the left is trying to reach the one on the right; a wall got in the way; the other got hurt or stuck; the first one is going around; oh, that sparkle was a distraction but it ignored it; finally they are back together.* This is exactly Dennett's claim — that an entity's behaviour becomes intelligible the moment we treat it *as if* it had beliefs and desires. Heider & Simmel's 1944 finding is that viewers do this **spontaneously** for geometric shapes. The film leans on that.

**Internal — the belief/desire/plan readout.**
At intentional moments a small lower-third chyron appears. It reads, in succession:

- **BELIEF** — *friend is on the other side*
- **DESIRE** — *reach the friend*
- **PLAN** — *go above*
- **BELIEF** — *new barrier ahead*
- **PLAN** — *re-routing*

These are the three primitives that recur across the readings on the syllabus: Cohen's BDI agents, Baker, Jara-Ettinger, Saxe & Tenenbaum's Bayesian Theory of Mind, and the modal-logic BDI formalisation in the later possible-world lectures. The chyron does not replace the viewer's reading — it sits below it, the way subtitles sit under a film. It says: *what you just attributed has a name and a shape inside the agent.*

The point is the **alignment** between the two layers. If a viewer's intentional reading is well-tuned, it should agree with the chyron — and on every beat in the film, it does.

## Dennett's three stances in the room

Each of Dennett's three stances applies to *something* on screen, and the film tries to make this distribution visible.

- **Physical stance.** The walls are walls. They rise on a timer, follow an easing curve, occupy space. Their behaviour needs no mentalising.
- **Design stance.** The walls are also *designed*: they appear at exactly the moments that make the rescue interesting. The viewer, if they choose, can notice the dramaturgy.
- **Intentional stance.** The Hero and the Friend cannot be explained either physically (no force pushes them) or by design (they are not described as machines following a script). They are only intelligible when treated as agents with beliefs and desires.

The three stances stratify the same scene. The film does not declare which is correct; it makes all three available.

## Tying back to the rest of the course

The film is meant to sit downstream of the first four lectures and prefigure the rest:

- **dist-01 (intro).** Establishes Real World / Embodiment / Intention as the keywords. The film stays in a *symbolic* room, not a physical one, but the BDI machinery is the same.
- **dist-02 (SHRDLU).** Plan → Action. The Hero's commitment to a plan, and its re-plan, is exactly the SHRDLU grammar moved out of a block world into a 2D stage.
- **dist-03 (SSA / ANA).** Goal-oriented vs. environment-oriented. The film is squarely goal-oriented; environment-emergent behaviour (à la Sonja) is out of scope.
- **dist-04 (Dennett's stance + Theory of Mind).** The film's central reference. The intentional-stance / BDI duality above is the through-line.
- **dist-05–07 (possible worlds, modal logic, BDI choice).** The Beat 3 ghost paths are a cartoon of the modal-logic notion of a choice across possible worlds. The model is not built; it is *gestured at*.

## What the film does **not** show

Calling out the limits gives the talk room to breathe and matches the way Imai himself partitions the lectures.

- **No communication.** Joint attention, communicative intention, social commitment — all later in the course. Hero and Friend never signal each other.
- **No real Bayesian inference.** The chyron uses the words of BToM but the underlying agent is not running posterior updates. It is a finite-state plan with a hand-authored re-plan trigger.
- **No multi-agent mentalising.** The Hero models the Friend's *location*, not the Friend's *mind*. There is no nested theory of mind.
- **No physical grounding.** No sensors, no actuators, no embodiment. The film is a thought-experiment, not a robot demo.

## How the talk can use the film

The five-minute presentation slot asks for: cover story, intentional behaviours observed, method, the angle on which to be evaluated, then the film again. The cleanest framing is:

1. *Play the film cold.* Let the viewer attribute intention first.
2. *Cover story* in one line. Two robots, separated, one finds a way back.
3. *Intentional behaviours.* Walk the six-hint table above, point at the specific beat for each.
4. *Method.* Pygame for drawing, NumPy/SciPy for bloom and trails, imageio-ffmpeg for encoding. All frames generated programmatically — no screen recording.
5. *Evaluate me on.* The alignment of external attribution and internal BDI exposure — the two readings agreeing — and on the restraint with which intention is staged (no faces, no language, no scoring music).
6. *Play it again.* The second viewing usually reads differently, because the labels are now in the viewer's head.

## References on the syllabus that this film leans on

- Dennett, *Intentional Systems*, J. Phil. 68, 1971.
- Cohen & Levesque, *Intention is Choice with Commitment*, Artif. Intell. 42, 1990 (the BDI / P-GOAL grammar in `dist-07`).
- Baker, Jara-Ettinger, Saxe & Tenenbaum, *Rational quantitative attribution of beliefs, desires and percepts in human mentalizing*, Nature Human Behaviour 1, 64, 2017.
- Heider & Simmel, *An Experimental Study of Apparent Behavior*, Am. J. Psych. 57, 1944.
- Epley, Waytz & Cacioppo, *On Seeing Human: A Three-Factor Theory of Anthropomorphism*, Psych. Review 114, 2007.
