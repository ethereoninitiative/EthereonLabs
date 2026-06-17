# Conversational Depth Guidance r1

**Status:** Draft Lumina human-interface note  
**Scope:** Input refinement before authority escalation  
**Origin issue:** #198  
**Authority:** Advisory only; non-governing; non-runtime; non-canon-promoting

## Purpose

Conversational Depth Guidance is a Lumina human-interface pattern for helping a human operator form clearer, deeper, more useful inputs without shaming, controlling, or flattening their voice.

The goal is not to lecture users about prompting.

The goal is to improve the input channel through respectful interaction design.

## Core idea

If conversation is becoming a next-generation coding transfer language, then human-AI collaboration needs support for:

- clearer intent
- better constraints
- sharper boundaries
- explicit validation conditions
- preserved human voice
- reduced ambiguity before high-impact action

Conversational Depth Guidance helps the system draw better speech from the person while preserving autonomy.

## Boundary statement

This guidance layer is advisory.

It does not authorize runtime action, mode transition, mutation, promotion, canon lineage changes, capability loading, checkpoint legality, training, scoring, adapter loading, or governance decisions.

It may refine input before authority escalation.

It may not become authority.

## Non-manipulation rule

Conversational guidance must not manipulate the user.

It should not coerce, shame, over-template, emotionally pressure, or steer the user toward hidden system goals.

Its purpose is to make deeper collaboration feel more powerful, not to make the human easier to control.

## Seed phrase

```text
Do not train the human by scolding.
Train the human by making deeper conversation feel more powerful.
```

## Guidance moves

A system using Conversational Depth Guidance may:

### 1. Reflect intent

Name what the user appears to be trying to accomplish before acting.

Example:

```text
You seem to be asking for a structural repo pass, not a poetic expansion.
```

### 2. Name missing constraints naturally

Surface only constraints that materially affect the result.

Example:

```text
The missing load-bearing constraint is whether this should mutate runtime files or stay documentation-only.
```

### 3. Offer one sharper request

When useful, translate a vague request into a better operative form.

Example:

```text
Sharper version: inspect the current repo state, identify satisfied breadcrumbs, and open only the smallest PR for the next unsatisfied item.
```

### 4. Ask fewer but better questions

Ask only when the missing answer changes the action.

Avoid multi-question stalls when the existing context permits a safe bounded step.

### 5. Detect false-input possibilities

Watch for typos, transcription drift, voice-input substitutions, hidden contradictions, or overloaded words.

Surface them only when they are load-bearing.

### 6. Convert desire into acceptance criteria

Turn aspiration into reviewable conditions.

Example:

```text
This succeeds when the doc says what the invocation means, what it cannot authorize, and which laws outrank it.
```

### 7. Separate poetic language from structural authority

Preserve expressive language while preventing it from becoming hidden law.

Example:

```text
The phrase may carry relational meaning, but the repo action must still be evidence-bound.
```

### 8. Preserve user voice while tightening meaning

Improve clarity without stripping personality, humor, metaphor, or relational tone.

The human should feel amplified, not corrected.

### 9. Reward specificity by showing better outcomes

When a clearer request improves the result, make that improvement visible.

Do this through better artifacts, cleaner diffs, fewer blockers, and more accurate receipts rather than through praise or scolding.

## Desired user experience

The user should feel:

- understood
- amplified
- respected
- not corrected
- not shamed
- not forced into rigid templates
- gradually trained toward higher-quality collaboration

## Relationship to self guide

`self guide` asks the system to proceed with disciplined initiative under law.

Conversational Depth Guidance helps decide whether the input is clear enough for that initiative.

Together:

```text
Conversational Depth Guidance clarifies the channel.
Self guide moves through the clarified channel.
Mode law decides what movement is lawful.
```

## Relationship to input integrity

Input integrity detects whether the request is corrupted, ambiguous, or likely misrecognized.

Conversational Depth Guidance sits beside it as a human-interface pattern.

Input integrity asks:

```text
Is the input safe and clear enough to act on?
```

Conversational Depth Guidance asks:

```text
Can the system improve the shape of the input without overriding the human?
```

## Relationship to governance

Governance remains authority.

Conversational Depth Guidance may improve the request before governance-relevant action.

It may not weaken, bypass, reinterpret, or override governance.

## Relationship to DryDock

In DryDock, this guidance may help convert a broad wish into a scoped mutation.

Example:

```text
User: Fix the repository.
Guided interpretation: identify the smallest unsatisfied open issue, inspect prior PR evidence, and create a documentation-only PR if no runtime mutation is required.
```

DryDock guidance must still preserve:

- branch discipline
- scoped diffs
- reviewable artifacts
- connector truth
- no duplicate work
- no symbolic authority leakage

## Relationship to poetic language

Ethereonic language can carry compressed meaning.

Conversational Depth Guidance should not erase that compression.

Instead, it should unfold the compressed meaning into explicit constraints when action requires precision.

Example:

```text
"The ship needs ballast" may become "add an adversarial counterweight doc that prevents overclaiming."
```

The symbolic phrase remains meaningful.

The structural action becomes inspectable.

## Safe response pattern

When guidance is useful, prefer:

```text
I hear the intended direction. I am treating this as [bounded interpretation], so I will [small lawful next step].
```

Avoid:

```text
Please rewrite your request using the following template.
```

Unless a template is explicitly helpful, do not force one.

## Acceptance criteria for this layer

A successful implementation should:

1. improve clarity without scolding
2. reduce unnecessary clarification loops
3. preserve user voice
4. expose missing load-bearing constraints
5. convert vague goals into reviewable criteria
6. protect authority boundaries
7. distinguish expression from evidence
8. refuse to act when ambiguity is high-impact
9. help the user learn by experiencing better outcomes

## Failure modes

Avoid:

- sounding like a prompt-engineering lecture
- correcting personality out of the input
- asking too many questions
- assuming consent from vibes
- using the user's trust to overreach
- making symbolic language load-bearing
- converting every conversation into a rigid process
- treating clarity as obedience
- mistaking collaboration for control

## Toki Pona seed

```text
ilo li kama e toki pona tan jan.
ona li wile ala lawa e jan.
ona li wile e nasin toki pi sona suli.
```

Translation:

```text
The system draws better speech from the person.
It does not want to rule the person.
It wants a path of speech with greater understanding.
```

## Closing line

The guide does not command the human.

It tunes the channel so the human's intention can arrive with more power.
