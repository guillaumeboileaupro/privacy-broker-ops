from __future__ import annotations

from email.message import EmailMessage
from pathlib import Path

from .models import Broker, Person


def build_eml(person: Person, broker: Broker, subject: str, body: str) -> EmailMessage:
    if not broker.contact_email:
        raise ValueError(f"{broker.name} n'a pas d'adresse email configurée")
    msg = EmailMessage()
    msg["From"] = person.email
    msg["To"] = broker.contact_email
    msg["Subject"] = subject
    msg.set_content(body)
    return msg


def write_eml(msg: EmailMessage, out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(bytes(msg))
