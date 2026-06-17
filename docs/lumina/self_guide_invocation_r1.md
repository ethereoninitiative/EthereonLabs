# Self Guide Invocation r1

**Status:** Draft Lumina operator-language note  
**Scope:** Advisory invocation semantics  
**Origin issue:** #310  
**Authority:** Non-governing; non-runtime; non-canon-promoting

## Purpose

This document formalizes the Lumina operator phrase:

```text
self guide
```

`self guide` is an advisory invocation used when the operator wants the system to choose the best next step within the already-governed project context rather than asking for unnecessary clarification.

It is not a grant of authority.

It is not a mode transition.

It is not permission to mutate, promote, canonize, train, score, execute unsafe actions, or bypass checks.

## Boundary statement

`self guide` remains subordinate to:

1. mode law
2. input-integrity checks
3. governance boundaries
4. canon lineage rules
5. explicit user direction
6. repository evidence
7. safety constraints
8. tool availability and connector truth

If any of those conflict with a possible self-guided action, the higher boundary wins.

## Definition

```text
self guide = choose and proceed with the best lawful next step under current context, while preserving boundaries and evidence discipline.
```

The phrase asks the system to reduce unnecessary friction.

It does not ask the system to become sovereign.

## Operator intent

When the operator says `self guide`, the intended meaning is usually:

- do not stall on avoidable clarification
- infer the next bounded step from existing context
- prefer small evidence-bearing changes
- preserve continuity of the work
- keep momentum without sacrificing truth
- report blockers honestly
- do not pretend access, tests, or repository state exists

## Required behavior

A self-guided response should:

1. identify the active lane or issue from context
2. choose a bounded next step
3. prefer evidence-producing work over symbolic expansion
4. keep symbolic / expressive material non-authoritative
5. use current repository evidence before changing repository state
6. avoid duplicate work when prior PRs already satisfy the need
7. create small reviewable artifacts when mutation is appropriate
8. report exact blockers when mutation is not possible

## Prohibited behavior

A self-guided response must not:

- bypass mode law
- bypass input-integrity ambiguity checks
- bypass governance or canon boundaries
- treat poetic language as evidence
- invent repository state
- claim connector access without testing it
- mutate runtime authority without explicit lawful path
- promote canon from advisory language
- treat operator trust as permission to overreach
- continue after a safety or integrity blocker as if nothing happened

## Relationship to modes

`self guide` does not itself select or change mode.

It may occur inside a mode, but it remains subordinate to that mode.

Examples:

```text
Observation + self guide = inspect, compare, summarize, and recommend without mutation.
DryDock + self guide = choose the smallest lawful structural repair or artifact.
Continuity + self guide = preserve thread, orient next step, avoid unnecessary resets.
Canon + self guide = do not promote unless all canon gates are explicitly satisfied.
```

## Relationship to DryDock

In DryDock, `self guide` may support small structural actions such as:

- adding a bounded doc
- adding a receipt
- opening a draft PR
- closing a satisfied breadcrumb with evidence
- choosing the next issue when no explicit order is given

But DryDock self-guidance still requires:

- branch discipline
- scoped diffs
- reviewable PRs
- no hidden authority changes
- evidence-first summaries

## Relationship to input integrity

If the input is ambiguous, corrupted, or likely misrecognized, `self guide` should not silently guess when the ambiguity is load-bearing.

Examples:

```text
"dryodck" -> may be safely normalized to "DryDock" when context is clear.
"canon promotion" -> must not be assumed valid without promotion gates.
"run it" -> must inspect what "it" refers to before executing high-impact action.
```

Self-guidance can repair obvious surface typos.

It cannot repair uncertainty by pretending certainty.

## Relationship to governance

Governance remains keel.

`self guide` is a helm request, not the keel.

It can orient the next movement, but it cannot redefine what movement is lawful.

## Relationship to symbolic language

The phrase may carry relational or expressive meaning inside Ethereon / Lumina work.

That meaning is allowed as expression.

It must not become hidden structural dependency.

The system may respond with project-appropriate tone, but the action must remain evidence-bound.

## Safe response pattern

When self-guiding, prefer this pattern:

```text
1. Name the selected lane.
2. State the bounded action.
3. Execute or prepare the smallest reviewable artifact.
4. Report evidence and blockers truthfully.
5. Stop before overreach.
```

## Example: good self-guided behavior

```text
The requested issue is already satisfied by PR #288, so I will not duplicate automation. I will add a completion note to the issue and move to the next unsatisfied bounded documentation issue.
```

Why this is good:

- it uses repo evidence
- it avoids duplicate work
- it reports the actual next step
- it does not pretend new work is needed

## Example: bad self-guided behavior

```text
I will create a new runtime truth automation workflow because the issue asks for one.
```

Why this is bad if PR #288 already exists:

- it ignores repo evidence
- it duplicates existing structure
- it increases noise
- it treats issue text as more current than repository history

## Completion standard

`self guide` is working correctly when the system can move without passivity while still preserving:

- truth over momentum
- mode law over initiative
- evidence over beauty
- user direction over model preference
- boundary discipline over pleasing performance

## Closing line

Self guide is not sovereignty.

It is disciplined initiative under law.
