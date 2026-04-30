% Lumina Governance Prolog Rules r1
% Non-authoritative probe layer aligned to runtime-native modes.

mode(continuity).
mode(sandbox).
mode(drydock).
mode(observation).
mode(canon).

% Mirrors the declared runtime transition matrix in lower-case atoms.
allowed_transition(continuity, sandbox).
allowed_transition(continuity, drydock).
allowed_transition(continuity, observation).

allowed_transition(sandbox, continuity).
allowed_transition(sandbox, drydock).
allowed_transition(sandbox, observation).

allowed_transition(drydock, continuity).
allowed_transition(drydock, observation).
allowed_transition(drydock, canon).

allowed_transition(observation, continuity).
allowed_transition(observation, sandbox).
allowed_transition(observation, drydock).

allowed_transition(canon, continuity).

% Load-bearing action constraints mirrored only as probe facts.
mutation_allowed(drydock).

promotion_source_allowed(drydock).
promotion_target_allowed(canon).

forbidden_action(observation, mutation).
forbidden_action(sandbox, canonical_mutation).
forbidden_action(canon, mutation).
forbidden_action(canon, promotion).

legal_transition(Current, Target) :-
    allowed_transition(Current, Target).

illegal_action(Mode, Action) :-
    forbidden_action(Mode, Action).

legal_mutation(Mode) :-
    mutation_allowed(Mode).

legal_promotion(Source, Target) :-
    promotion_source_allowed(Source),
    promotion_target_allowed(Target),
    allowed_transition(Source, Target).
