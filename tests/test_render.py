from privacy_broker_ops.models import Broker, Exposure, ExposureStatus, Person
from privacy_broker_ops.render import render_request


def test_render_request_contains_name_and_url() -> None:
    person = Person(full_name="Guillaume Boileau", email="g@example.com")
    broker = Broker(
        id="test",
        name="Test Broker",
        category="people_search",
        request_channel="email",
        contact_email="privacy@example.com",
    )
    exposure = Exposure(
        id=1,
        broker_id="test",
        url="https://example.com/profile",
        status=ExposureStatus.CONFIRME,
        data_type="profil public",
        discovered_at="2026-06-30T00:00:00+00:00",
    )
    body = render_request(person, broker, exposure)
    assert "Guillaume Boileau" in body
    assert "https://example.com/profile" in body
    assert "RGPD" in body
