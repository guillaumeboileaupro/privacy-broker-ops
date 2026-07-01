from datetime import UTC, datetime, timedelta

from privacy_broker_ops.agent import evaluate_exposure
from privacy_broker_ops.models import Exposure, ExposureStatus, ReminderKind


def make_exposure(status: ExposureStatus, days: int | None = None) -> Exposure:
    last_contact = None
    if days is not None:
        last_contact = (datetime.now(UTC) - timedelta(days=days)).replace(microsecond=0).isoformat()
    return Exposure(
        id=1,
        broker_id="idcrawl",
        url="https://example.com/profile",
        status=status,
        discovered_at="2026-06-01T00:00:00+00:00",
        last_contact_at=last_contact,
    )


def test_agent_before_15_days_is_ok() -> None:
    decision = evaluate_exposure(make_exposure(ExposureStatus.ENVOYE, days=14))
    assert decision.urgency == "ok"
    assert decision.reminder_kind == ReminderKind.NONE


def test_agent_at_15_days_recommends_soft_reminder() -> None:
    decision = evaluate_exposure(make_exposure(ExposureStatus.ENVOYE, days=15))
    assert decision.recommended_status == ExposureStatus.RELANCE_A_FAIRE
    assert decision.urgency == "soon"
    assert decision.reminder_kind == ReminderKind.SOFT


def test_agent_recommends_reminder_after_30_days() -> None:
    decision = evaluate_exposure(make_exposure(ExposureStatus.ENVOYE, days=31))
    assert decision.recommended_status == ExposureStatus.RELANCE_A_FAIRE
    assert decision.urgency == "urgent"
    assert decision.reminder_kind == ReminderKind.FORMAL


def test_agent_at_45_days_recommends_cnil() -> None:
    decision = evaluate_exposure(make_exposure(ExposureStatus.ENVOYE, days=45))
    assert decision.recommended_status == ExposureStatus.CNIL_A_ENVISAGER
    assert decision.reminder_kind == ReminderKind.CNIL


def test_agent_closed_status_never_relaunches() -> None:
    decision = evaluate_exposure(make_exposure(ExposureStatus.CLOS, days=45))
    assert decision.recommended_status == ExposureStatus.CLOS
    assert decision.reminder_kind == ReminderKind.NONE


def test_agent_suppression_confirmee_never_relaunches() -> None:
    decision = evaluate_exposure(make_exposure(ExposureStatus.SUPPRESSION_CONFIRMEE, days=45))
    assert decision.recommended_status == ExposureStatus.SUPPRESSION_CONFIRMEE
    assert decision.reminder_kind == ReminderKind.NONE


def test_agent_homonyme_never_relaunches() -> None:
    decision = evaluate_exposure(make_exposure(ExposureStatus.HOMONYME, days=45))
    assert decision.recommended_status == ExposureStatus.HOMONYME
    assert decision.reminder_kind == ReminderKind.NONE
