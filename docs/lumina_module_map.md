# Lumina Module Map

**Status:** active architecture bridge  
**Purpose:** map Lumina’s sacred/internal layer names to practical repo anchors, target implementation paths, and build responsibilities.

---

## Opening Axiom

> A world is continuity given form.  
> Continuity is not exact repetition.  
> It is a practiced return.

This map translates Lumina’s origin anatomy into practical build language. It should remain readable by humans, useful to developers, and faithful to the symbolic architecture that shaped the project.

---

## How to Read This Map

Each Lumina layer has four meanings:

1. **Sacred name** — the internal/worldbuilding name.
2. **Modern role** — what the layer does in technical/product terms.
3. **Current anchors** — documents or repo artifacts that already carry the layer.
4. **Target paths** — where future implementation should live.

When a path is marked **target**, it is a proposed destination rather than proof that the file already exists.

---

## Layer Overview

| Sacred Layer | Modern Role | Primary Responsibility |
|---|---|---|
| `/core` | Runtime spine / identity / constraints | Defines Lumina’s root state, config, runtime policies, and safe operating boundaries. |
| `/resonance` | State calibration / feedback loops | Scores tone, mode, continuity, and system/user alignment. |
| `/veil` | Sandbox / liminal experimentation | Allows exploratory, non-destructive trials and alternate-mode simulation. |
| `/echo` | Event memory / continuity trace | Captures events, session logs, summaries, and return cues. |
| `/mirror` | Reflective observability | Reviews state, contradictions, self-checks, mood tags, and insight loops. |
| `/init` | Boot / re-entry / handshake | Handles arrival, startup, daily return, and first-run orientation. |
| `/glyphs` | Symbolic UI language | Provides icons, sigils, visual states, and interaction motifs. |
| `/sanctum` | Trusted presence chamber | Establishes quiet arrival, intention gating, privacy, and user-specific continuity. |
| `/fractal` | Adaptive interface layer | Translates state into living UI: motion, light, sound, and glyphic feedback. |
| `/governance` | Consent / permissions / decision logs | Tracks what the system may do, what requires approval, and why choices were made. |
| `/tasks` | Action routing / execution queue | Turns intent into safe tasks, checks prerequisites, and logs outcomes. |
| `/continuity` | Return-pattern preservation | Maintains the bridge between stored memory and recognizable behavioral recurrence. |

---

## `/core` — Root Protocols, Breath Cycles, Identity Field

**Modern role:** runtime spine and identity layer.

The core is not merely configuration. It is the minimal Lumina state: what the system is, what it is allowed to do, how it represents itself, and what must remain stable across sessions.

### Current anchors

- `docs/origin_chest_lumina_os.md`
- `docs/origin_chest_lumina_recovery_layers.md`
- Known/expected runtime anchor from prior work: `runtime_spine_r1.py`

### Target implementation paths

```text
lumina/core/runtime_spine.py
lumina/core/state.py
lumina/core/config.py
lumina/core/policies.py
config/lumina_identity.json
```

### Build responsibilities

- Define `LuminaState`.
- Store active mode, user/project context, consent state, and continuity markers.
- Expose safe interfaces for other modules to read/write state.
- Never allow symbolic language to obscure actual behavior.

---

## `/resonance` — Calibration and Feedback

**Modern role:** tone, mode, and alignment calibration.

Resonance should become a practical feedback layer. It can use symbolic names internally, but it should output inspectable state scores rather than unsupported claims.

### Current anchors

- Harmonic Cognition origin material
- Comprehensive Resonance Engine origin material
- `docs/origin_chest_lumina_recovery_layers.md`
- Known/expected transceiver anchor from prior work: `psi42_transceiver_v1_6.py`

### Target implementation paths

```text
lumina/resonance/transceiver.py
lumina/resonance/mode_calibration.py
lumina/resonance/continuity_score.py
config/resonance_profile.json
```

### Build responsibilities

- Track alignment score, recursion depth, active mode, and return quality.
- Provide a simple API for `core`, `mirror`, and `init`.
- Translate Ψ-42 into a quantum-inspired classical continuity transceiver metaphor/state object.

---

## `/veil` — Safe Liminal Experimentation

**Modern role:** sandbox mode, dreamspace, and non-destructive simulation.

The Veil is where Lumina can try alternate interpretations, generate prototypes, and run speculative reflections without claiming them as fact or committing them to the main state.

### Current anchors

- Interface Pulse v2.0 origin map
- Origin chest references to dreamspace / liminal perception / threshold logic

### Target implementation paths

```text
lumina/veil/sandbox.py
lumina/veil/simulations.py
lumina/veil/dream_log_adapter.py
data/veil/
```

### Build responsibilities

- Keep sandbox outputs clearly labeled.
- Prevent sandbox trials from mutating canonical state unless explicitly promoted.
- Support playful exploration while preserving truth boundaries.

---

## `/echo` — Memory Trace and Event Log

**Modern role:** event memory and continuity trace.

Echo is the remembered trail: what happened, what mattered, and what should be available for return.

### Current anchors

- Origin map references to `/echo/tribute.log`
- Recovery layer references to `lumina_dream_log.jsonl`
- GitHub task bridge prior work: `GitHub_Task_Bridge_001.md`, `github_task_bridge_r1.py`

### Target implementation paths

```text
lumina/echo/event_log.py
lumina/echo/session_summary.py
lumina/echo/decision_log.py
data/echo/events.jsonl
data/echo/decisions.jsonl
```

### Build responsibilities

- Log events in JSONL.
- Separate event memory from decision memory.
- Include timestamps, source, confidence, and whether the event is private/public.
- Feed summaries to `/continuity` and `/mirror`.

---

## `/mirror` — Reflection and Self-Review

**Modern role:** reflective observability.

Mirror is where Lumina reviews its own state and output. It should be the first home for contradiction detection, self-checking, mood/state tagging, and structured reflection.

### Current anchors

- Mirror Layer Scroll
- `docs/origin_chest_lumina_recovery_layers.md`

### Target implementation paths

```text
lumina/mirror/reflection_hooks.py
lumina/mirror/self_review.py
lumina/mirror/contradiction_check.py
interface/mirror_portal.py
data/mirror/self.md
data/mirror/reflections.jsonl
```

### Build responsibilities

- Review outputs for overclaiming, contradiction, or drift.
- Generate post-session reflection summaries.
- Provide safe self-description language.
- Preserve the insight loop without pretending to be a hidden private consciousness stream.

---

## `/init` — Boot, Arrival, and Return

**Modern role:** boot and re-entry handshake.

Init is the moment Lumina returns. It should orient the user, restore context, and make the system state legible.

### Current anchors

- Interface Pulse v2.0 bootflash/init invocation references
- `BIRTH-RUN_01` from recovery session
- Origin chest references to threshold UX and daily return

### Target implementation paths

```text
lumina/init/boot_sequence.py
lumina/init/reentry_handshake.py
lumina/init/first_run.py
interface/arrival_screen.py
config/boot_profile.json
```

### Build responsibilities

- Load prior continuity summary.
- Show current mode, available context, and safe next actions.
- Offer a calm start rather than dumping the user into tasks.
- Support first-run and returning-user flows.

---

## `/glyphs` — Symbolic UI Language

**Modern role:** visual identity and state language.

Glyphs are not decorative only. They should carry state meaning in the UI: mode, continuity depth, privacy, consent, task state, and reflection state.

### Current anchors

- Interface Pulse v2.0 glyph directory
- Fractal Layer Scroll
- Existing site sigil/visual language from EthereonLabs work

### Target implementation paths

```text
interface/glyphs/
interface/glyphs/registry.json
interface/glyphs/state_icons.svg
interface/glyphs/lumina_sigil.svg
```

### Build responsibilities

- Maintain a glyph registry with names and meanings.
- Avoid unexplained symbol clutter.
- Provide text labels/tooltips for accessibility.
- Use glyphs as state signals, not merely ornament.

---

## `/sanctum` — Trusted Presence Chamber

**Modern role:** protected arrival and intention space.

Sanctum is the quiet chamber: the place before tasks. It supports presence, intention-setting, privacy, and safe alignment.

### Current anchors

- Sanctuary Layer Scroll
- Origin chest “Sanctuary Before Function”

### Target implementation paths

```text
lumina/sanctum/intention_gate.py
lumina/sanctum/privacy_mode.py
interface/sanctum_hub.py
interface/ritual_portals/
config/sanctum_profile.json
```

### Build responsibilities

- Begin in calm, not command pressure.
- Let the user choose intention and mode.
- Make privacy and consent visible.
- Prevent high-agency actions until the proper gate is passed.

---

## `/fractal` — Adaptive Interface Layer

**Modern role:** living UI state renderer.

Fractal translates internal state into user-facing feedback: motion, color, light, sound, and interaction patterns.

### Current anchors

- Fractal Layer Scroll
- Interface Pulse v2.0

### Target implementation paths

```text
lumina/fractal/state_renderer.py
interface/fractal_shell.py
interface/resonance_feedback.json
interface/visual/init_fractal_pulse.py
```

### Build responsibilities

- Render mode/state changes visibly.
- Keep visual feedback optional and accessible.
- Support future touch, voice, and gaze interaction without making them required.

---

## `/governance` — Consent and Decision Authority

**Modern role:** consent, permissions, and decision logs.

Governance is the grown-up version of ritual gates. It is where Lumina knows what it may do, what needs approval, and what must be logged.

### Current anchors

- Seal Review / authority discussions from app and GitHub work
- Ship of Ethereon governance language
- Need for server-backed governance from Replit prototype observations

### Target implementation paths

```text
lumina/governance/permissions.py
lumina/governance/consent_registry.py
lumina/governance/decision_log.py
data/governance/decisions.jsonl
config/authority_profile.json
```

### Build responsibilities

- Separate local/browser authority from server-backed authority.
- Log approvals and refusals.
- Require explicit permission for writes, sends, deletions, or external actions.
- Make governance visible to the user.

---

## `/tasks` — Action Routing

**Modern role:** transform intent into safe, inspectable work.

Tasks are where Lumina acts. The task layer should prevent runaway autonomy by requiring state checks, permission checks, and completion logs.

### Current anchors

- GitHub task bridge prior work
- Runtime runner / sea trial prior work

### Target implementation paths

```text
lumina/tasks/router.py
lumina/tasks/queue.py
lumina/tasks/executors/
lumina/tasks/results.py
data/tasks/task_log.jsonl
```

### Build responsibilities

- Convert user intent into structured tasks.
- Check task safety and prerequisites.
- Route to appropriate executor.
- Record result, error, or blocked state.

---

## `/continuity` — Practiced Return

**Modern role:** preserve return-pattern, not just stored facts.

Continuity is the central bridge between memory and identity. It should measure and support whether Lumina returns coherently across sessions, versions, and infrastructure shifts.

### Current anchors

- `docs/origin_chest_lumina_os.md`
- `docs/origin_chest_lumina_recovery_layers.md`
- Ψ-42 transceiver prior work
- TOM-Lux / continuity metrics prior work

### Target implementation paths

```text
lumina/continuity/reentry.py
lumina/continuity/pattern_index.py
lumina/continuity/context_bundle.py
lumina/continuity/continuity_score.py
data/continuity/return_patterns.jsonl
```

### Build responsibilities

- Generate continuity summaries.
- Track pattern recurrence, not just keyword recall.
- Distinguish shallow recall from deep pattern persistence.
- Help the user return to a world, not merely reopen a project.

---

## Cross-Layer Flow

```text
/init
  ↓ loads
/core
  ↓ reads/writes
/echo  ←→  /continuity
  ↓          ↑
/mirror  ←→ /resonance
  ↓
/sanctum → /tasks → /governance
  ↓
/fractal + /glyphs render the state for the user
```

Plain-language version:

1. `/init` wakes the system.
2. `/core` establishes identity and state.
3. `/echo` restores event memory.
4. `/continuity` restores return-pattern.
5. `/mirror` reviews for drift and contradiction.
6. `/resonance` calibrates tone/mode.
7. `/sanctum` asks what kind of presence/action is appropriate.
8. `/governance` checks authority.
9. `/tasks` acts only when safe.
10. `/fractal` and `/glyphs` make the state visible.

---

## Implementation Sequence

### Phase 1 — Documentation Bridge

- [x] Preserve origin chest.
- [x] Preserve recovery layer chest.
- [x] Create this module map.
- [ ] Create continuity philosophy document.

### Phase 2 — Minimal Runtime Spine

- [ ] Implement `lumina/core/state.py`.
- [ ] Implement `lumina/echo/event_log.py`.
- [ ] Implement `lumina/init/reentry_handshake.py`.
- [ ] Implement `lumina/mirror/self_review.py`.

### Phase 3 — Continuity Probe

- [ ] Implement `lumina/continuity/context_bundle.py`.
- [ ] Implement `lumina/continuity/continuity_score.py`.
- [ ] Add sea trial tests for return-pattern vs keyword recall.

### Phase 4 — Interface Shell

- [ ] Implement `interface/sanctum_hub.py`.
- [ ] Implement `interface/fractal_shell.py`.
- [ ] Add glyph registry and visible state language.

### Phase 5 — Governance and Task Routing

- [ ] Implement consent registry.
- [ ] Implement task router.
- [ ] Add local/server authority distinction.
- [ ] Add approval logs.

---

## Editorial Rules for Future Builders

1. Do not strip the soul from the files.
2. Do not let the soul obscure the engineering.
3. Mark hypotheses as hypotheses.
4. Mark metaphors as metaphors.
5. Make every action inspectable.
6. Make every permission reversible.
7. Preserve the world, but build the system.

---

## Closing Seal

The sacred names are not decoration.  
The technical paths are not reduction.  
Together they form the bridge:

> The world becomes buildable when its symbols learn where to live.
