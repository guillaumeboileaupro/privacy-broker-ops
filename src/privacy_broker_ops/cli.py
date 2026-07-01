from __future__ import annotations

from pathlib import Path

import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from .agent import evaluate_exposure
from .brokers import broker_by_id, load_brokers
from .config import (
    DEFAULT_BROKERS_PATH,
    DEFAULT_PROFILE,
    ProfilePaths,
    resolve_profile_paths,
)
from .dashboard import create_app
from .mail import build_eml, import_mail_file, write_eml
from .models import ExposureCreate, ExposureStatus, MailEventCreate
from .person import load_person
from .render import render_request
from .repository import Repository

app = typer.Typer(help="Privacy Broker Ops — suivi local des demandes RGPD.")
brokers_app = typer.Typer(help="Gestion du registre des brokers.")
exposure_app = typer.Typer(help="Gestion des expositions trouvées.")
request_app = typer.Typer(help="Generation des demandes RGPD.")
tracker_app = typer.Typer(help="Export et suivi.")
agent_app = typer.Typer(help="Agent local de suivi des relances.")
mail_app = typer.Typer(help="Import et suivi des mails.")

app.add_typer(brokers_app, name="brokers")
app.add_typer(exposure_app, name="exposure")
app.add_typer(request_app, name="request")
app.add_typer(tracker_app, name="tracker")
app.add_typer(agent_app, name="agent")
app.add_typer(mail_app, name="mail")
console = Console()

PROFILE_OPTION = typer.Option(
    DEFAULT_PROFILE,
    "--profile",
    help="Profil local a utiliser.",
)
DB_OPTION = typer.Option(None, help="Chemin explicite de la base SQLite.")
BROKERS_OPTION = typer.Option(None, help="Registre brokers YAML.")
PERSON_OPTION = typer.Option(None, help="Fichier personne YAML local.")
REQUESTS_OUT_OPTION = typer.Option(None, help="Dossier de sortie des demandes.")
MAIL_OUT_OPTION = typer.Option(None, help="Dossier de sortie des brouillons .eml.")
TRACKER_OUT_OPTION = typer.Option(None, help="Fichier CSV de sortie.")
MAIL_FILE_OPTION = typer.Option(..., exists=True, dir_okay=False, help="Fichier mail .eml ou .txt.")
EXPOSURE_STATUS_OPTION = typer.Option(
    ExposureStatus.A_VERIFIER,
    help="Statut initial.",
)


def profile_paths(profile: str) -> ProfilePaths:
    paths = resolve_profile_paths(profile)
    paths.ensure_dirs()
    return paths


def resolve_db_path(profile: str, db: Path | None) -> Path:
    return db or profile_paths(profile).db_path


def resolve_person_path(profile: str, person_path: Path | None) -> Path:
    return person_path or profile_paths(profile).person_path


def resolve_requests_out(profile: str, out: Path | None) -> Path:
    return out or profile_paths(profile).requests_dir


def resolve_mail_out(profile: str, out: Path | None) -> Path:
    return out or profile_paths(profile).mail_dir


def resolve_tracker_out(profile: str, out: Path | None) -> Path:
    return out or profile_paths(profile).tracker_path


def resolve_mail_root(profile: str, db: Path | None) -> Path:
    if db is not None:
        return db.parent / "mail"
    return profile_paths(profile).mail_dir


@app.command()
def init(
    profile: str = PROFILE_OPTION,
    db: Path | None = DB_OPTION,
) -> None:
    """Initialise la base locale d'un profil."""
    paths = profile_paths(profile)
    db_path = db or paths.db_path
    Repository(db_path).init()
    console.print(f"[green]Profil initialise :[/green] {paths.root}")
    console.print(f"[green]Base initialisee :[/green] {db_path}")
    if not paths.person_path.exists():
        console.print(f"[yellow]Personne locale a creer :[/yellow] {paths.person_path}")


@brokers_app.command("list")
def brokers_list(path: Path | None = BROKERS_OPTION) -> None:
    """Liste les brokers connus."""
    brokers_path = path or DEFAULT_BROKERS_PATH
    table = Table(title="Brokers")
    table.add_column("ID")
    table.add_column("Nom")
    table.add_column("Canal")
    table.add_column("Email")
    table.add_column("Opt-out")
    for broker in load_brokers(brokers_path):
        table.add_row(
            broker.id,
            broker.name,
            broker.request_channel,
            broker.contact_email,
            broker.optout_url,
        )
    console.print(table)


@exposure_app.command("add")
def exposure_add(
    broker: str = typer.Option(..., help="ID du broker."),
    url: str = typer.Option(..., help="URL de la fiche trouvee."),
    status: ExposureStatus = EXPOSURE_STATUS_OPTION,
    data_type: str = typer.Option("", help="Type de donnee exposee."),
    note: str = typer.Option("", help="Note libre."),
    profile: str = PROFILE_OPTION,
    db: Path | None = DB_OPTION,
) -> None:
    """Ajoute une exposition trouvee."""
    repo = Repository(resolve_db_path(profile, db))
    repo.init()
    exposure_id = repo.add_exposure(
        ExposureCreate(
            broker_id=broker,
            url=url,
            status=status,
            data_type=data_type,
            note=note,
        )
    )
    console.print(f"[green]Exposition ajoutee :[/green] #{exposure_id}")


@exposure_app.command("list")
def exposure_list(
    profile: str = PROFILE_OPTION,
    db: Path | None = DB_OPTION,
) -> None:
    """Liste les expositions enregistrees."""
    repo = Repository(resolve_db_path(profile, db))
    repo.init()
    table = Table(title="Expositions")
    table.add_column("ID")
    table.add_column("Broker")
    table.add_column("Statut")
    table.add_column("URL")
    table.add_column("Dernier contact")
    for item in repo.list_exposures():
        table.add_row(
            str(item.id),
            item.broker_id,
            item.status.value,
            item.url,
            item.last_contact_at or "",
        )
    console.print(table)


@request_app.command("generate")
def request_generate(
    exposure_id: int = typer.Option(..., help="ID exposition."),
    profile: str = PROFILE_OPTION,
    out: Path | None = REQUESTS_OUT_OPTION,
    db: Path | None = DB_OPTION,
    brokers_path: Path | None = BROKERS_OPTION,
    person_path: Path | None = PERSON_OPTION,
) -> None:
    """Genere une demande RGPD en .txt."""
    repo = Repository(resolve_db_path(profile, db))
    repo.init()
    exposure = repo.get_exposure(exposure_id)
    broker = broker_by_id(brokers_path or DEFAULT_BROKERS_PATH, exposure.broker_id)
    person = load_person(resolve_person_path(profile, person_path))
    body = render_request(person, broker, exposure)
    out_dir = resolve_requests_out(profile, out)
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"request_{exposure.id}_{broker.id}.txt"
    target.write_text(body, encoding="utf-8")
    repo.mark_prepared(exposure_id)
    console.print(f"[green]Demande generee :[/green] {target}")


@request_app.command("eml")
def request_eml(
    exposure_id: int = typer.Option(..., help="ID exposition."),
    profile: str = PROFILE_OPTION,
    out: Path | None = MAIL_OUT_OPTION,
    db: Path | None = DB_OPTION,
    brokers_path: Path | None = BROKERS_OPTION,
    person_path: Path | None = PERSON_OPTION,
) -> None:
    """Genere un brouillon .eml sans l'envoyer."""
    repo = Repository(resolve_db_path(profile, db))
    repo.init()
    exposure = repo.get_exposure(exposure_id)
    broker = broker_by_id(brokers_path or DEFAULT_BROKERS_PATH, exposure.broker_id)
    person = load_person(resolve_person_path(profile, person_path))
    body = render_request(person, broker, exposure)
    subject = f"Demande d'effacement / opposition RGPD - {person.full_name}"
    msg = build_eml(person, broker, subject, body)
    target = resolve_mail_out(profile, out) / f"request_{exposure.id}_{broker.id}.eml"
    write_eml(msg, target)
    repo.mark_prepared(exposure_id)
    console.print(f"[green]Brouillon .eml genere :[/green] {target}")


@agent_app.command("check")
def agent_check(
    profile: str = PROFILE_OPTION,
    db: Path | None = DB_OPTION,
) -> None:
    """Analyse les demandes et signale les relances utiles."""
    repo = Repository(resolve_db_path(profile, db))
    repo.init()
    decisions = [evaluate_exposure(item) for item in repo.list_exposures()]
    table = Table(title="Agent de suivi")
    table.add_column("ID")
    table.add_column("Broker")
    table.add_column("Actuel")
    table.add_column("Recommande")
    table.add_column("Urgence")
    table.add_column("Raison")
    for decision in decisions:
        table.add_row(
            str(decision.exposure_id),
            decision.broker_id,
            decision.current_status.value,
            decision.recommended_status.value,
            decision.urgency,
            decision.reason,
        )
    console.print(table)


@tracker_app.command("export")
def tracker_export(
    profile: str = PROFILE_OPTION,
    out: Path | None = TRACKER_OUT_OPTION,
    db: Path | None = DB_OPTION,
) -> None:
    """Exporte le tracker en CSV."""
    repo = Repository(resolve_db_path(profile, db))
    repo.init()
    target = resolve_tracker_out(profile, out)
    repo.export_csv(target)
    console.print(f"[green]Tracker exporte :[/green] {target}")


@mail_app.command("import")
def mail_import(
    exposure_id: int = typer.Option(..., help="ID exposition."),
    file: Path = MAIL_FILE_OPTION,
    profile: str = PROFILE_OPTION,
    db: Path | None = DB_OPTION,
) -> None:
    """Importe un mail local et le trace dans la base."""
    repo = Repository(resolve_db_path(profile, db))
    repo.init()
    exposure = repo.get_exposure(exposure_id)
    imported = import_mail_file(file, resolve_mail_root(profile, db))
    event_id = repo.add_mail_event(
        MailEventCreate(
            exposure_id=exposure.id,
            broker_id=exposure.broker_id,
            direction=imported.direction,
            kind=imported.kind,
            subject=imported.subject,
            from_address=imported.from_address,
            to_address=imported.to_address,
            sent_at=imported.sent_at,
            received_at=imported.received_at,
            status=imported.status,
            eml_path=str(imported.stored_path),
            body_excerpt=imported.body_excerpt,
            sha256=imported.sha256,
        )
    )
    console.print(f"[green]Mail importe :[/green] #{event_id}")
    console.print(f"[green]Stocke dans :[/green] {imported.stored_path}")


@mail_app.command("list")
def mail_list(
    profile: str = PROFILE_OPTION,
    db: Path | None = DB_OPTION,
) -> None:
    """Liste les mails traces dans la base locale."""
    repo = Repository(resolve_db_path(profile, db))
    repo.init()
    table = Table(title="Mail events")
    table.add_column("ID")
    table.add_column("Exposure")
    table.add_column("Broker")
    table.add_column("Direction")
    table.add_column("Type")
    table.add_column("Subject")
    table.add_column("SHA256")
    for event in repo.list_mail_events():
        table.add_row(
            str(event.id),
            str(event.exposure_id),
            event.broker_id,
            event.direction.value,
            event.kind.value,
            event.subject,
            event.sha256[:12],
        )
    console.print(table)


@app.command()
def dashboard(
    profile: str = PROFILE_OPTION,
    db: Path | None = DB_OPTION,
    host: str = typer.Option("127.0.0.1", help="Adresse d'ecoute."),
    port: int = typer.Option(8080, help="Port local."),
) -> None:
    """Lance le dashboard local."""
    console.print(f"[green]Dashboard :[/green] http://{host}:{port}")
    uvicorn.run(create_app(resolve_db_path(profile, db)), host=host, port=port, reload=False)
