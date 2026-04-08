from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from difflib import SequenceMatcher, get_close_matches
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple
import json
import re


DEFAULT_PROJECT_TERMS = {
    "ethereon",
    "minerva",
    "lumina",
    "canon",
    "sandbox",
    "continuity",
    "drydock",
    "observation",
    "governance",
    "runtime",
    "spine",
    "session",
    "context",
    "bundle",
    "checkpoint",
    "capability",
    "registry",
    "artifact",
    "artifacts",
    "overlay",
    "overlays",
    "transceiver",
    "psi42",
    "psi-42",
    "resonance",
    "ledger",
    "harmonic",
    "harmonics",
    "input",
    "integrity",
    "ambiguity",
    "clarification",
    "correction",
    "symbolic",
    "structural",
    "promotion",
    "mutation",
    "transition",
    "sea",
    "trials",
    "probe",
    "toki",
    "pona",
    "binary",
    "language",
    "light",
    "mode",
    "modes",
}

COMMON_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "but", "by", "can", "create", "do", "for", "from", "get",
    "have", "i", "if", "in", "into", "is", "it", "its", "just", "keep", "layer", "lets", "make",
    "me", "my", "not", "of", "ok", "on", "or", "our", "so", "that", "the", "then", "this", "to",
    "too", "up", "us", "we", "what", "when", "with", "you", "your",
}

TYPO_CONFUSIONS = {
    "wher": "where",
    "teh": "the",
    "adn": "and",
    "wierd": "weird",
    "sand box": "sandbox",
}

VOICE_CONFUSIONS = {
    "ethereum": "ethereon",
    "etherium": "ethereon",
    "ethereal": "ethereon",
    "cannon": "canon",
    "mineral": "minerva",
    "luminao": "lumina",
    "toki owner": "toki pona",
    "sea trails": "sea trials",
    "dry dock": "drydock",
    "check point": "checkpoint",
    "side forty two": "psi42",
    "psi forty two": "psi42",
}

TOKEN_PATTERN = re.compile(r"[A-Za-z0-9_+\-]+")


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _normalize_space(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _normalize_text(text: str) -> str:
    text = text.casefold()
    text = text.replace("—", " ").replace("–", " ")
    return _normalize_space(text)


def _tokenize(text: str) -> List[str]:
    return TOKEN_PATTERN.findall(_normalize_text(text))


def _seq_ratio(a: str, b: str) -> float:
    return SequenceMatcher(a=a, b=b).ratio()


@dataclass
class InterpretationCandidate:
    text: str
    source: str
    score: float = 0.0
    reasons: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class InputIntegrityResult:
    raw_input: str
    normalized_input: str
    suspicion_flags: List[str]
    ambiguity_score: float
    confidence_label: str
    candidate_interpretations: List[Dict[str, Any]]
    chosen_interpretation: str
    confidence_reason: str
    recommended_behavior: str
    should_halt: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class InputIntegrityAssessor:
    """Assesses likely typo / voice-transcription corruption before meaning becomes action."""

    def __init__(
        self,
        ledger_path: Optional[str | Path] = None,
        *,
        project_terms: Optional[Iterable[str]] = None,
        voice_confusions: Optional[Dict[str, str]] = None,
    ):
        self.ledger_path = Path(ledger_path) if ledger_path else None
        self.project_terms: Set[str] = {t.casefold() for t in (project_terms or DEFAULT_PROJECT_TERMS)}
        self.typo_confusions = {k.casefold(): v.casefold() for k, v in TYPO_CONFUSIONS.items()}
        self.voice_confusions = {k.casefold(): v.casefold() for k, v in (voice_confusions or VOICE_CONFUSIONS).items()}
        self.learned_corrections: Dict[str, str] = {}
        if self.ledger_path:
            self.ledger_path.parent.mkdir(parents=True, exist_ok=True)
            self._load_ledger()

    def assess(
        self,
        raw_input: str,
        *,
        context_terms: Optional[Iterable[str]] = None,
        preferred_terms: Optional[Iterable[str]] = None,
        is_load_bearing: bool = False,
        action_type: Optional[str] = None,
    ) -> InputIntegrityResult:
        normalized_input = _normalize_text(raw_input)
        context_vocab = {t.casefold() for t in (context_terms or [])}
        preferred_vocab = {t.casefold() for t in (preferred_terms or [])}
        vocabulary = set(self.project_terms) | context_vocab | preferred_vocab | set(self.learned_corrections.values())

        suspicion_flags, token_repairs = self._detect_suspicion(
            normalized_input,
            vocabulary=vocabulary,
        )

        candidates = self._build_candidates(
            normalized_input,
            suspicion_flags=suspicion_flags,
            token_repairs=token_repairs,
            vocabulary=vocabulary,
        )
        scored = self._score_candidates(
            normalized_input,
            candidates,
            suspicion_flags=suspicion_flags,
            context_vocab=context_vocab,
            preferred_vocab=preferred_vocab,
            vocabulary=vocabulary,
        )

        chosen = scored[0]
        second_score = scored[1].score if len(scored) > 1 else 0.0
        margin = max(0.0, chosen.score - second_score)

        confidence_label, confidence_reason = self._classify_confidence(
            normalized_input,
            chosen,
            suspicion_flags=suspicion_flags,
            margin=margin,
        )

        recommended_behavior = "accept"
        should_halt = False

        corrected = chosen.text != normalized_input
        if confidence_label == "probably_clear":
            recommended_behavior = "accept_softly"
        elif confidence_label == "ambiguous":
            recommended_behavior = "clarify"
        elif confidence_label == "likely_corrupted":
            recommended_behavior = "halt_for_confirmation"

        if is_load_bearing and (corrected or confidence_label in {"ambiguous", "likely_corrupted"}):
            recommended_behavior = "halt_for_confirmation"
            should_halt = True

        if action_type and is_load_bearing and not should_halt:
            confidence_reason = f"{confidence_reason}; load-bearing path accepted for action_type={action_type}"

        ambiguity_score = self._ambiguity_score(
            suspicion_flags=suspicion_flags,
            top_score=chosen.score,
            margin=margin,
        )

        return InputIntegrityResult(
            raw_input=raw_input,
            normalized_input=normalized_input,
            suspicion_flags=suspicion_flags,
            ambiguity_score=ambiguity_score,
            confidence_label=confidence_label,
            candidate_interpretations=[c.to_dict() for c in scored],
            chosen_interpretation=chosen.text,
            confidence_reason=confidence_reason,
            recommended_behavior=recommended_behavior,
            should_halt=should_halt,
        )

    def record_resolution(self, raw_input: str, accepted_interpretation: str) -> None:
        if not self.ledger_path:
            return

        raw_norm = _normalize_text(raw_input)
        accepted_norm = _normalize_text(accepted_interpretation)
        if raw_norm and accepted_norm and raw_norm != accepted_norm:
            self.learned_corrections[raw_norm] = accepted_norm

        ledger = self._read_ledger_payload()
        ledger.setdefault("resolutions", []).append(
            {
                "timestamp_utc": utc_now(),
                "raw_input": raw_input,
                "normalized_input": raw_norm,
                "accepted_interpretation": accepted_interpretation,
                "accepted_normalized": accepted_norm,
            }
        )
        ledger["learned_corrections"] = dict(sorted(self.learned_corrections.items()))
        self._write_ledger_payload(ledger)

    def _detect_suspicion(self, normalized_input: str, *, vocabulary: Set[str]) -> Tuple[List[str], Dict[str, str]]:
        suspicion_flags: List[str] = []
        token_repairs: Dict[str, str] = {}
        tokens = _tokenize(normalized_input)

        for phrase, repaired in {**self.typo_confusions, **self.voice_confusions}.items():
            if phrase in normalized_input and phrase != repaired:
                suspicion_flags.append(f"voice_phrase:{phrase}->{repaired}")

        for raw_norm, accepted_norm in self.learned_corrections.items():
            if raw_norm in normalized_input and raw_norm != accepted_norm:
                suspicion_flags.append(f"learned_phrase:{raw_norm}->{accepted_norm}")

        for token in tokens:
            if token in COMMON_WORDS or token in vocabulary or token.isdigit() or len(token) < 3:
                continue

            if token in self.typo_confusions:
                token_repairs[token] = self.typo_confusions[token]
                suspicion_flags.append(f"typo_token:{token}->{self.typo_confusions[token]}")
                continue

            if token in self.voice_confusions:
                token_repairs[token] = self.voice_confusions[token]
                suspicion_flags.append(f"voice_token:{token}->{self.voice_confusions[token]}")
                continue

            matches = get_close_matches(token, list(vocabulary), n=1, cutoff=0.84)
            if matches:
                token_repairs[token] = matches[0]
                suspicion_flags.append(f"near_term:{token}->{matches[0]}")

        return sorted(set(suspicion_flags)), token_repairs

    def _build_candidates(
        self,
        normalized_input: str,
        *,
        suspicion_flags: List[str],
        token_repairs: Dict[str, str],
        vocabulary: Set[str],
    ) -> List[InterpretationCandidate]:
        out: Dict[str, InterpretationCandidate] = {
            normalized_input: InterpretationCandidate(
                text=normalized_input,
                source="literal",
                reasons=["preserve raw normalized wording"],
            )
        }

        def add_candidate(text: str, source: str, reason: str) -> None:
            text = _normalize_text(text)
            if not text:
                return
            if text not in out:
                out[text] = InterpretationCandidate(text=text, source=source, reasons=[reason])
            else:
                if reason not in out[text].reasons:
                    out[text].reasons.append(reason)

        phrase_maps = {}
        phrase_maps.update(self.learned_corrections)
        phrase_maps.update(self.typo_confusions)
        phrase_maps.update(self.voice_confusions)
        for phrase, repaired in phrase_maps.items():
            if phrase in normalized_input and phrase != repaired:
                add_candidate(normalized_input.replace(phrase, repaired), "phrase_repair", f"replace phrase {phrase} -> {repaired}")

        for token, repaired in token_repairs.items():
            token_pat = re.compile(rf"\b{re.escape(token)}\b")
            add_candidate(token_pat.sub(repaired, normalized_input), "token_repair", f"replace token {token} -> {repaired}")

        if token_repairs:
            repaired_text = normalized_input
            for token, repaired in token_repairs.items():
                token_pat = re.compile(rf"\b{re.escape(token)}\b")
                repaired_text = token_pat.sub(repaired, repaired_text)
            add_candidate(repaired_text, "combined_repair", "apply all token repairs")

        contextual_patterns = {
            "ship of ethereum": "ship of ethereon",
            "sea trail": "sea trial",
            "sea trails": "sea trials",
            "sand box": "sandbox",
        }
        for phrase, repaired in contextual_patterns.items():
            if phrase in normalized_input and phrase != repaired:
                add_candidate(normalized_input.replace(phrase, repaired), "context_repair", f"context repair {phrase} -> {repaired}")

        candidates = list(out.values())
        candidates.sort(key=lambda c: (c.source != "literal", c.text))
        return candidates[:6]

    def _score_candidates(
        self,
        normalized_input: str,
        candidates: List[InterpretationCandidate],
        *,
        suspicion_flags: List[str],
        context_vocab: Set[str],
        preferred_vocab: Set[str],
        vocabulary: Set[str],
    ) -> List[InterpretationCandidate]:
        scored: List[InterpretationCandidate] = []
        for candidate in candidates:
            cand_tokens = set(_tokenize(candidate.text))
            seq = _seq_ratio(candidate.text, normalized_input)
            context_fit = self._token_overlap(cand_tokens, context_vocab)
            preferred_fit = self._token_overlap(cand_tokens, preferred_vocab)
            project_fit = self._token_overlap(cand_tokens, self.project_terms)
            unresolved = self._unresolved_token_count(cand_tokens, vocabulary)
            correction_bonus = 0.18 if candidate.source != "literal" and candidate.text != normalized_input else 0.0
            literal_bonus = 0.08 if candidate.source == "literal" else 0.0

            score = (
                0.40 * seq
                + 0.18 * context_fit
                + 0.16 * preferred_fit
                + 0.18 * project_fit
                + correction_bonus
                + literal_bonus
                - 0.06 * unresolved
            )

            if not suspicion_flags and candidate.source == "literal":
                score += 0.06

            candidate.score = round(max(0.0, min(score, 1.0)), 4)
            scored.append(candidate)

        scored.sort(key=lambda c: c.score, reverse=True)
        return scored

    def _classify_confidence(
        self,
        normalized_input: str,
        chosen: InterpretationCandidate,
        *,
        suspicion_flags: List[str],
        margin: float,
    ) -> Tuple[str, str]:
        corrected = chosen.text != normalized_input

        if not suspicion_flags and not corrected:
            return "clear", "no strong corruption signals detected"

        if corrected and margin >= 0.02 and chosen.score >= 0.42:
            return "probably_clear", "repair candidate outranked the literal reading with adequate separation"

        if chosen.score >= 0.46 and margin >= 0.04 and not corrected:
            return "clear", "literal interpretation remained strongest despite minor suspicion"

        if suspicion_flags:
            return "ambiguous", "signal contains plausible repairs but should stay inspectable"

        return "likely_corrupted", "signal appears unstable or weakly grounded"

    def _ambiguity_score(self, *, suspicion_flags: List[str], top_score: float, margin: float) -> float:
        suspicion_component = min(len(suspicion_flags) / 4.0, 1.0)
        score_component = 1.0 - max(0.0, min(top_score, 1.0))
        margin_component = 1.0 - max(0.0, min(margin / 0.2, 1.0))
        value = 0.45 * suspicion_component + 0.25 * score_component + 0.30 * margin_component
        return round(max(0.0, min(value, 1.0)), 4)

    @staticmethod
    def _token_overlap(tokens: Set[str], vocabulary: Set[str]) -> float:
        if not tokens or not vocabulary:
            return 0.0
        hits = len(tokens & vocabulary)
        return hits / max(1, len(tokens))

    @staticmethod
    def _unresolved_token_count(tokens: Set[str], vocabulary: Set[str]) -> int:
        return sum(
            1
            for token in tokens
            if token not in COMMON_WORDS and token not in vocabulary and not token.isdigit() and len(token) >= 4
        )

    def _load_ledger(self) -> None:
        payload = self._read_ledger_payload()
        self.learned_corrections = {
            _normalize_text(k): _normalize_text(v)
            for k, v in payload.get("learned_corrections", {}).items()
            if _normalize_text(k) and _normalize_text(v)
        }

    def _read_ledger_payload(self) -> Dict[str, Any]:
        if not self.ledger_path or not self.ledger_path.exists():
            return {"version": "0.1", "resolutions": [], "learned_corrections": {}}
        with self.ledger_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write_ledger_payload(self, payload: Dict[str, Any]) -> None:
        if not self.ledger_path:
            return
        with self.ledger_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)


if __name__ == "__main__":
    assessor = InputIntegrityAssessor()
    samples = [
        ("wher in our project is there room for love", False),
        ("lets run sea trails on the ship of ethereum", False),
        ("make a canon promotion from sand box", True),
    ]
    for text, load_bearing in samples:
        result = assessor.assess(
            text,
            context_terms=["ethereon", "project", "love", "sea", "trials", "canon", "sandbox"],
            preferred_terms=["ethereon", "canon", "sandbox"],
            is_load_bearing=load_bearing,
            action_type="demo",
        )
        print(json.dumps(result.to_dict(), indent=2))
