from __future__ import annotations

from datetime import UTC, datetime

from dateutil.parser import isoparse

from .models import AgentDecision, Exposure, ExposureStatus, ReminderKind


def days_since(iso: str) -> int:
    dt = isoparse(iso)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return (datetime.now(UTC) - dt).days


def evaluate_exposure(exposure: Exposure) -> AgentDecision:
    if exposure.status in {
        ExposureStatus.CLOS,
        ExposureStatus.SUPPRESSION_CONFIRMEE,
        ExposureStatus.HOMONYME,
        ExposureStatus.REFUS,
    }:
        return AgentDecision(
            exposure_id=exposure.id,
            broker_id=exposure.broker_id,
            current_status=exposure.status,
            recommended_status=exposure.status,
            reason="Aucune relance a generer pour ce statut.",
            reminder_kind=ReminderKind.NONE,
            urgency="ok",
        )

    if exposure.status != ExposureStatus.ENVOYE or not exposure.last_contact_at:
        return AgentDecision(
            exposure_id=exposure.id,
            broker_id=exposure.broker_id,
            current_status=exposure.status,
            recommended_status=exposure.status,
            reason="Aucune relance sans date d'envoi valide.",
            reminder_kind=ReminderKind.NONE,
            urgency="ok",
        )

    days = days_since(exposure.last_contact_at)
    if days >= 45:
        return AgentDecision(
            exposure_id=exposure.id,
            broker_id=exposure.broker_id,
            current_status=exposure.status,
            recommended_status=ExposureStatus.CNIL_A_ENVISAGER,
            reason="Aucune réponse après 45 jours : envisager une escalade CNIL.",
            reminder_kind=ReminderKind.CNIL,
            urgency="urgent",
            days_since_last_contact=days,
        )
    if days >= 30:
        return AgentDecision(
            exposure_id=exposure.id,
            broker_id=exposure.broker_id,
            current_status=exposure.status,
            recommended_status=ExposureStatus.RELANCE_A_FAIRE,
            reason="Aucune réponse après 30 jours : relance RGPD ferme recommandée.",
            reminder_kind=ReminderKind.FORMAL,
            urgency="urgent",
            days_since_last_contact=days,
        )
    if days >= 15:
        return AgentDecision(
            exposure_id=exposure.id,
            broker_id=exposure.broker_id,
            current_status=exposure.status,
            recommended_status=ExposureStatus.RELANCE_A_FAIRE,
            reason="Aucune réponse après 15 jours : relance douce recommandée.",
            reminder_kind=ReminderKind.SOFT,
            urgency="soon",
            days_since_last_contact=days,
        )
    return AgentDecision(
        exposure_id=exposure.id,
        broker_id=exposure.broker_id,
        current_status=exposure.status,
        recommended_status=exposure.status,
        reason="Délai de réponse encore raisonnable.",
        reminder_kind=ReminderKind.NONE,
        urgency="ok",
        days_since_last_contact=days,
    )
