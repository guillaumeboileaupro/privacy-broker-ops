from datetime import UTC, datetime, timedelta

from privacy_broker_ops.followup import evaluate_exposure
from privacy_broker_ops.models import Exposure, ExposureStatus


def test_followup_recommends_reminder_after_30_days() -> None:
    last_contact = (datetime.now(UTC) - timedelta(days=31)).replace(microsecond=0).isoformat()
    exposure = Exposure(
        id=1,
        broker_id="idcrawl",
        url="https://example.com/profile",
        status=ExposureStatus.ENVOYE,
        discovered_at="2026-06-01T00:00:00+00:00",
        last_contact_at=last_contact,
    )
    decision = evaluate_exposure(exposure)
    assert decision.recommended_status == ExposureStatus.RELANCE_A_FAIRE
    assert decision.urgency == "urgent"
