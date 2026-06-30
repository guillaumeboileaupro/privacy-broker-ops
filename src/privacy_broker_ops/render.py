from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .models import Broker, Exposure, Person

TEMPLATE_DIR = Path(__file__).parent / "templates"


def render_request(person: Person, broker: Broker, exposure: Exposure) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(default_for_string=False, default=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("request_fr.txt.j2")
    return template.render(person=person, broker=broker, exposure=exposure)


def render_reminder(person: Person, broker: Broker, exposure: Exposure, days: int) -> str:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(default_for_string=False, default=False),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("reminder_fr.txt.j2")
    return template.render(person=person, broker=broker, exposure=exposure, days=days)
