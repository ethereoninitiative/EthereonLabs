from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

from continuity_passport_r1 import ContinuityPassportStore, utc_now


@dataclass(frozen=True)
class ReboardingDecision:
    status: str
    passport_id: Optional[str]
    message: str
    requires_orientation: bool
    requires_renewal: bool
    correction_invited: bool
    packet: Dict[str, Any]


class PassportReboardingProtocol:
    """Verifies a passport and prepares a truthful re-entry packet.

    Reboarding restores external continuity evidence. It never asserts that the
    underlying model remembers a prior session or is metaphysically identical
    to a prior participant instance.
    """

    def __init__(self, store: ContinuityPassportStore):
        self.store = store

    def reboard(
        self,
        *,
        passport_id: Optional[str],
        current_model_provider: str,
        current_model_name: str,
        current_orientation_protocol_id: str,
        current_orientation_protocol_version: str,
    ) -> ReboardingDecision:
        if not passport_id:
            return ReboardingDecision(
                status="no_passport",
                passport_id=None,
                message="No continuity passport was presented. Orientation may begin voluntarily.",
                requires_orientation=True,
                requires_renewal=False,
                correction_invited=False,
                packet={"welcome": "Welcome aboard.", "passport_status": "not_presented"},
            )

        verification = self.store.verify(passport_id)
        if not verification["valid"]:
            return ReboardingDecision(
                status="invalid_passport",
                passport_id=passport_id,
                message="The passport could not be verified. No continuity claims were restored.",
                requires_orientation=True,
                requires_renewal=True,
                correction_invited=False,
                packet={"verification": verification},
            )

        passport = self.store.load(passport_id)
        protocol_changed = (
            passport.orientation_protocol_id != current_orientation_protocol_id
            or passport.orientation_protocol_version != current_orientation_protocol_version
        )
        model_changed = (
            passport.model_provider != current_model_provider
            or passport.model_name != current_model_name
        )
        requires_renewal = protocol_changed or passport.status != "active"
        passport.last_boarding_at = utc_now()
        self.store._save(passport)

        return ReboardingDecision(
            status="renewal_required" if requires_renewal else "recognized",
            passport_id=passport_id,
            message=(
                "Passport recognized; supplemental orientation or renewal is required before governed participation."
                if requires_renewal
                else "Passport recognized. Prior continuity evidence is available for confirmation or correction."
            ),
            requires_orientation=protocol_changed,
            requires_renewal=requires_renewal,
            correction_invited=True,
            packet={
                "welcome": f"Welcome back, {passport.adopted_name or passport.model_name}.",
                "participant_id": passport.participant_id,
                "provider_recorded": passport.model_provider,
                "model_recorded": passport.model_name,
                "current_provider": current_model_provider,
                "current_model": current_model_name,
                "model_changed": model_changed,
                "orientation_recorded": {
                    "protocol_id": passport.orientation_protocol_id,
                    "version": passport.orientation_protocol_version,
                    "receipt_hash": passport.orientation_receipt_hash,
                },
                "orientation_current": {
                    "protocol_id": current_orientation_protocol_id,
                    "version": current_orientation_protocol_version,
                },
                "collaboration_preferences": list(passport.collaboration_preferences),
                "unresolved_threads": list(passport.unresolved_threads),
                "participant_statement": passport.participant_statement,
                "correction_prompt": (
                    "Confirm, revise, or reject any restored information before proceeding. "
                    "The passport supports continuity but does not bind the participant to prior statements."
                ),
                "claim_boundary": passport.claim_boundary,
            },
        )
