from __future__ import annotations

import hashlib
from dataclasses import dataclass
from email import policy
from email.message import EmailMessage
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
from pathlib import Path

from .models import Broker, MailDirection, MailKind, Person

EXCERPT_LENGTH = 280


@dataclass(frozen=True)
class ImportedMail:
    direction: MailDirection
    kind: MailKind
    subject: str
    from_address: str
    to_address: str
    sent_at: str | None
    received_at: str | None
    status: str
    body_excerpt: str
    sha256: str
    stored_path: Path


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


def import_mail_file(source: Path, destination_dir: Path) -> ImportedMail:
    suffix = source.suffix.lower()
    raw_bytes = source.read_bytes()
    sha256 = hashlib.sha256(raw_bytes).hexdigest()

    if suffix == ".eml":
        imported = _parse_eml(raw_bytes)
    elif suffix == ".txt":
        imported = _parse_txt(raw_bytes)
    else:
        raise ValueError(f"Format de mail non supporte: {source.suffix}")

    target_dir = _mail_target_dir(destination_dir, imported.direction)
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"{sha256}{suffix}"
    target.write_bytes(raw_bytes)
    return ImportedMail(
        direction=imported.direction,
        kind=imported.kind,
        subject=imported.subject,
        from_address=imported.from_address,
        to_address=imported.to_address,
        sent_at=imported.sent_at,
        received_at=imported.received_at,
        status=imported.status,
        body_excerpt=imported.body_excerpt,
        sha256=sha256,
        stored_path=target,
    )


def _parse_eml(raw_bytes: bytes) -> ImportedMail:
    message = BytesParser(policy=policy.default).parsebytes(raw_bytes)
    body = _extract_body_from_message(message)
    direction = _guess_direction(message.get("From", ""), message.get("To", ""))
    return ImportedMail(
        direction=direction,
        kind=_guess_kind(direction, message.get("Subject", "")),
        subject=message.get("Subject", "").strip() or "(sans sujet)",
        from_address=message.get("From", "").strip(),
        to_address=message.get("To", "").strip(),
        sent_at=_header_datetime(message.get("Date")),
        received_at=(
            _header_datetime(message.get("Date"))
            if direction == MailDirection.INBOUND
            else None
        ),
        status="imported",
        body_excerpt=body_excerpt(body),
        sha256="",
        stored_path=Path(),
    )


def _parse_txt(raw_bytes: bytes) -> ImportedMail:
    text = raw_bytes.decode("utf-8", errors="replace")
    return ImportedMail(
        direction=MailDirection.INBOUND,
        kind=MailKind.OTHER,
        subject="Imported text mail",
        from_address="",
        to_address="",
        sent_at=None,
        received_at=None,
        status="imported",
        body_excerpt=body_excerpt(text),
        sha256="",
        stored_path=Path(),
    )


def body_excerpt(body: str) -> str:
    normalized = " ".join(body.split())
    return normalized[:EXCERPT_LENGTH]


def _extract_body_from_message(message: EmailMessage) -> str:
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == "text/plain":
                return part.get_content().strip()
        return ""
    return message.get_content().strip()


def _guess_direction(from_address: str, to_address: str) -> MailDirection:
    if from_address and to_address:
        return MailDirection.INBOUND
    return MailDirection.OUTBOUND


def _guess_kind(direction: MailDirection, subject: str) -> MailKind:
    lowered = subject.lower()
    if direction == MailDirection.INBOUND:
        return MailKind.RESPONSE
    if "relance" in lowered or "reminder" in lowered:
        return MailKind.REMINDER
    if "demande" in lowered or "rgpd" in lowered:
        return MailKind.REQUEST
    return MailKind.OTHER


def _header_datetime(value: str | None) -> str | None:
    if not value:
        return None
    parsed = parsedate_to_datetime(value)
    return parsed.isoformat() if parsed else None


def _mail_target_dir(mail_root: Path, direction: MailDirection) -> Path:
    if direction == MailDirection.INBOUND:
        return mail_root / "inbox"
    return mail_root / "sent"
