from __future__ import annotations

from pathlib import Path

import typer
import uvicorn
from rich.console import Console
from rich.table import Table

from .agent import evaluate_exposure
from .brokers import broker_by_id, load_brokers
from .config import DEFAULT_BROKERS_PATH, DEFAULT_DB_PATH, DEFAULT_PERSON_PATH
from .mail import build_eml, write_eml
from .models import ExposureCreate, ExposureStatus
from .person import load_person
from .render import render_request
from .repository import Repository

app = typer.Typer(help="Privacy Broker Ops — suivi local des demandes RGPD.")
brokers_app = typer.Typer(help="Gestion du registre des brokers.")
exposure_app = typer.Typer(help="Gestion des expositions trouvées.")
request_app = typer.Typer(help="Génération des demandes RGPD.")
tracker_app = typer.Typer(help="Export et suivi.")
agent_app = typer.Typer(help="Agent local de suivi des relances.")

app.add_typer(brokers_app, name="brokers")
app.add_typer(exposure_app, name="exposure")
app.add_typer(request_app, name="request")
app.add_typer(tracker_app, name="tracker")
app.add_typer(agent_app, name="agent")
console = Console()


@app.command()
def init(db: Path = typer.Option(DEFAULT_DB_PATH, help="Chemin de la base SQLite.")) -> None:
    """Initialise la base locale."""
    Repository(db).init()
    console.print(f"[green]Base initialisée :[/green] {db}")


@brokers_app.command("list")
def brokers_list(path: Path = typer.Option(DEFAULT_BROKERS_PATH, help="Registre brokers YAML.")) -> None:
    """Liste les brokers connus."""
    table = Table(title="Brokers")
    table.add_column("ID")
    table.add_column("Nom")
    table.add_column("Canal")
    table.add_column("Email")
    table.add_column("Opt-out")
    for broker in load_brokers(path):
        table.add_row(broker.id, broker.name, broker.request_channel, broker.contact_email, broker.optout_url)
    console.print(table)


@exposure_app.command("add")
def exposure_add(
    broker: str = typer.Option(..., help="ID du broker."),
    url: str = typer.Option(..., help="URL de la fiche trouvée."),
    status: ExposureStatus = typer.Option(ExposureStatus.A_VERIFIER, help="Statut initial."),
    data_type: str = typer.Option("", help="Type de donnée exposée."),
    note: str = typer.Option("", help="Note libre."),
    db: Path = typer.Option(DEFAULT_DB_PATH, help="Base SQLite."),
) -> None:
    """Ajoute une exposition trouvée."""
    repo = Repository(db)
    repo.init()
    exposure_id = repo.add_exposure(
        ExposureCreate(broker_id=broker, url=url, status=status, data_type=data_type, note=note)
    )
    console.print(f"[green]Exposition ajoutée :[/green] #{exposure_id}")


@exposure_app.command("list")
def exposure_list(db: Path = typer.Option(DEFAULT_DB_PATH, help="Base SQLite.")) -> None:
    """Liste les expositions enregistrées."""
    repo = Repository(db)
    repo.init()
    table = Table(title="Expositions")
    table.add_column("ID")
    table.add_column("Broker")
    table.add_column("Statut")
    table.add_column("URL")
    table.add_column("Dernier contact")
    for item in repo.list_exposures():
        table.add_row(str(item.id), item.broker_id, item.status.value, item.url, item.last_contact_at or "")
    console.print(table)


@request_app.command("generate")
def request_generate(
    exposure_id: int = typer.Option(..., help="ID exposition."),
    out: Path = typer.Option(Path("out/requests"), help="Dossier de sortie."),
    db: Path = typer.Option(DEFAULT_DB_PATH, help="Base SQLite."),
    brokers_path: Path = typer.Option(DEFAULT_BROKERS_PATH, help="Registre brokers YAML."),
    person_path: Path = typer.Option(DEFAULT_PERSON_PATH, help="Fichier personne YAML."),
) -> None:
    """Génère une demande RGPD en .txt."""
    repo = Repository(db)
    repo.init()
    exposure = repo.get_exposure(exposure_id)
    broker = broker_by_id(brokers_path, exposure.broker_id)
    person = load_person(person_path)
    body = render_request(person, broker, exposure)
    out.mkdir(parents=True, exist_ok=True)
    target = out / f"request_{exposure.id}_{broker.id}.txt"
    target.write_text(body, encoding="utf-8")
    repo.mark_prepared(exposure_id)
    console.print(f"[green]Demande générée :[/green] {target}")


@request_app.command("eml")
def request_eml(
    exposure_id: int = typer.Option(..., help="ID exposition."),
    out: Path = typer.Option(Path("out/eml"), help="Dossier de sortie."),
    db: Path = typer.Option(DEFAULT_DB_PATH, help="Base SQLite."),
    brokers_path: Path = typer.Option(DEFAULT_BROKERS_PATH, help="Registre brokers YAML."),
    person_path: Path = typer.Option(DEFAULT_PERSON_PATH, help="Fichier personne YAML."),
) -> None:
    """Génère un brouillon .eml sans l'envoyer."""
    repo = Repository(db)
    repo.init()
    exposure = repo.get_exposure(exposure_id)
    broker = broker_by_id(brokers_path, exposure.broker_id)
    person = load_person(person_path)
    body = render_request(person, broker, exposure)
    subject = f"Demande d'effacement / opposition RGPD - {person.full_name}"
    msg = build_eml(person, broker, subject, body)
    target = out / f"request_{exposure.id}_{broker.id}.eml"
    write_eml(msg, target)
    repo.mark_prepared(exposure_id)
    console.print(f"[green]Brouillon .eml généré :[/green] {target}")


@agent_app.command("check")
def agent_check(db: Path = typer.Option(DEFAULT_DB_PATH, help="Base SQLite.")) -> None:
    """Analyse les demandes et signale les relances utiles."""
    repo = Repository(db)
    repo.init()
    decisions = [evaluate_exposure(item) for item in repo.list_exposures()]
    table = Table(title="Agent de suivi")
    table.add_column("ID")
    table.add_column("Broker")
    table.add_column("Actuel")
    table.add_column("Recommandé")
    table.add_column("Urgence")
    table.add_column("Raison")
    for d in decisions:
        table.add_row(
            str(d.exposure_id),
            d.broker_id,
            d.current_status.value,
            d.recommended_status.value,
            d.urgency,
            d.reason,
        )
    console.print(table)


@tracker_app.command("export")
def tracker_export(
    out: Path = typer.Option(Path("out/tracker.csv"), help="Fichier CSV de sortie."),
    db: Path = typer.Option(DEFAULT_DB_PATH, help="Base SQLite."),
) -> None:
    """Exporte le tracker en CSV."""
    repo = Repository(db)
    repo.init()
    repo.export_csv(out)
    console.print(f"[green]Tracker exporté :[/green] {out}")


@app.command()
def dashboard(
    host: str = typer.Option("127.0.0.1", help="Adresse d'écoute."),
    port: int = typer.Option(8080, help="Port local."),
) -> None:
    """Lance le dashboard local."""
    console.print(f"[green]Dashboard :[/green] http://{host}:{port}")
    uvicorn.run("privacy_broker_ops.dashboard:app", host=host, port=port, reload=False)
