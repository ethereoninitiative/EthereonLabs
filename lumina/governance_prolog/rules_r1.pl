% Lumina Governance Prolog Rules r1
% Non-authoritative probe layer

mode(continuity).
mode(drydock).
mode(sea_trial).

allowed_transition(continuity, sea_trial).
allowed_transition(sea_trial, continuity).
allowed_transition(drydock, continuity).

forbidden_action(sea_trial, canon_promotion).
forbidden_action(drydock, runtime_execution).

legal_transition(Current, Target) :-
    allowed_transition(Current, Target).

illegal_action(Mode, Action) :-
    forbidden_action(Mode, Action).
