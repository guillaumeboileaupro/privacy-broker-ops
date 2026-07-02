from __future__ import annotations

from collections import Counter
from html import escape
from pathlib import Path
from urllib.parse import urlencode

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse

from .agent import evaluate_exposure
from .brokers import broker_by_id
from .config import DEFAULT_BROKERS_PATH, ProfilePaths, resolve_profile_paths
from .models import Exposure, ExposureStatus, ReminderKind
from .person import load_person
from .render import render_reminder_kind, render_request
from .repository import Repository


def resolve_dashboard_paths(profile: str, db_path: Path | None) -> ProfilePaths:
    if db_path is None:
        return resolve_profile_paths(profile)

    root = db_path.parent
    return ProfilePaths(
        profile=profile,
        root=root,
        db_path=db_path,
        person_path=root / "person.yaml",
        mail_dir=root / "mail",
        evidence_dir=root / "evidence",
        exports_dir=root / "exports",
    )


def page_template(title: str, content: str, *, readonly: bool) -> str:
    mode = "Lecture seule" if readonly else "Mode local"
    return f"""
    <!doctype html>
    <html lang="fr">
    <head>
      <meta charset="utf-8">
      <title>{escape(title)}</title>
      <style>
        body {{
          font-family: system-ui, sans-serif;
          margin: 2rem;
          background: #f6f6f6;
          color: #222;
        }}
        h1, h2 {{ margin-bottom: .3rem; }}
        nav {{ display: flex; flex-wrap: wrap; gap: .8rem; margin-bottom: 1rem; }}
        nav a {{ text-decoration: none; color: #0b4a6f; }}
        .banner {{
          background: #fff3cd;
          border: 1px solid #f1d58c;
          padding: .7rem;
          border-radius: 8px;
        }}
        .cards {{ display: flex; flex-wrap: wrap; gap: .7rem; margin: 1rem 0; }}
        .card {{
          background: white;
          border: 1px solid #ddd;
          border-radius: 8px;
          padding: .8rem;
          min-width: 150px;
        }}
        .panel {{
          background: white;
          border: 1px solid #ddd;
          border-radius: 8px;
          padding: 1rem;
          margin: 1rem 0;
        }}
        table {{ width: 100%; border-collapse: collapse; background: white; }}
        th, td {{ border: 1px solid #ddd; padding: .45rem; font-size: .9rem; vertical-align: top; }}
        th {{ background: #eee; text-align: left; }}
        .actions {{ display: flex; flex-wrap: wrap; gap: .6rem; margin-top: .8rem; }}
        .actions form, .actions a {{ margin: 0; }}
        .btn {{
          display: inline-block;
          background: #0b4a6f;
          color: white;
          border: none;
          border-radius: 6px;
          padding: .55rem .8rem;
          text-decoration: none;
          cursor: pointer;
        }}
        .btn.secondary {{ background: #5f6b72; }}
        .btn[disabled] {{ background: #999; cursor: not-allowed; }}
        .muted {{ color: #666; font-size: .9rem; }}
        code {{ background: #f1f1f1; padding: .1rem .3rem; border-radius: 4px; }}
      </style>
    </head>
    <body>
      <h1>Privacy Broker Ops</h1>
      <p class="muted">Dashboard local RGPD. {mode}. Aucun envoi automatique.</p>
      <nav>
        <a href="/">Accueil</a>
        <a href="/exposures">Expositions</a>
        <a href="/reminders">Relances a faire</a>
      </nav>
      {content}
    </body>
    </html>
    """


def build_exposure_rows(exposures: list[Exposure]) -> str:
    return "".join(
        (
            "<tr>"
            f"<td>{exposure.id}</td>"
            f"<td>{escape(exposure.broker_id)}</td>"
            f"<td><a href='/exposures/{exposure.id}'>{escape(exposure.url)}</a></td>"
            f"<td>{escape(exposure.status.value)}</td>"
            f"<td>{escape(exposure.discovered_at)}</td>"
            f"<td>{escape(exposure.last_contact_at or '')}</td>"
            f"<td>{escape(exposure.data_type)}</td>"
            f"<td>{escape(exposure.note)}</td>"
            "</tr>"
        )
        for exposure in exposures
    )


def action_forms(exposure_id: int, *, readonly: bool) -> str:
    if readonly:
        return "<p class='muted'>Mode lecture seule: actions d'ecriture desactivees.</p>"

    return f"""
    <div class="actions">
      <form method="post" action="/actions/request/{exposure_id}">
        <button class="btn" type="submit">Generer demande</button>
      </form>
      <form method="post" action="/actions/reminder/{exposure_id}">
        <button class="btn" type="submit">Generer relance</button>
      </form>
      <form method="post" action="/actions/export-csv">
        <button class="btn secondary" type="submit">Exporter CSV</button>
      </form>
    </div>
    """


def export_form(*, readonly: bool) -> str:
    if readonly:
        return "<p class='muted'>Mode lecture seule: export desactive.</p>"

    return """
    <div class="actions">
      <form method="post" action="/actions/export-csv">
        <button class="btn secondary" type="submit">Exporter CSV</button>
      </form>
    </div>
    """


def require_write_access(readonly: bool) -> None:
    if readonly:
        raise HTTPException(status_code=403, detail="Dashboard en lecture seule.")


def create_app(
    db_path: Path | None = None,
    *,
    profile: str = "default",
    readonly: bool = False,
) -> FastAPI:
    paths = resolve_dashboard_paths(profile, db_path)
    resolved_db_path = paths.db_path
    app = FastAPI(title="Privacy Broker Ops")
    app.state.readonly = readonly

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        repo = Repository(resolved_db_path)
        repo.init()
        exposures = repo.list_exposures()
        counts = Counter(e.status.value for e in exposures)
        broker_counts = Counter(e.broker_id for e in exposures)
        cards = "".join(
            (
                "<div class='card'>"
                f"<strong>{status.value}</strong><br>{counts.get(status.value, 0)}"
                "</div>"
            )
            for status in ExposureStatus
        )
        broker_rows = "".join(
            (
                "<tr>"
                f"<td>{escape(broker_id)}</td>"
                f"<td>{count}</td>"
                "</tr>"
            )
            for broker_id, count in broker_counts.most_common()
        )
        content = f"""
        {'<div class="banner">Mode lecture seule actif.</div>' if readonly else ''}
        <div class="cards">
          <div class='card'><strong>Total</strong><br>{len(exposures)}</div>
          {cards}
        </div>
        <div class="panel">
          <h2>Compteurs par broker</h2>
          <table>
            <thead><tr><th>Broker</th><th>Expositions</th></tr></thead>
            <tbody>{broker_rows}</tbody>
          </table>
        </div>
        <div class="panel">
          <h2>Expositions recentes</h2>
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Broker</th><th>URL</th><th>Statut</th>
                <th>Decouverte</th><th>Dernier contact</th><th>Type</th><th>Note</th>
              </tr>
            </thead>
            <tbody>{build_exposure_rows(exposures[:10])}</tbody>
          </table>
        </div>
        """
        return page_template("Privacy Broker Ops", content, readonly=readonly)

    @app.get("/exposures", response_class=HTMLResponse)
    def exposures(status: str | None = None) -> str:
        repo = Repository(resolved_db_path)
        repo.init()
        items = repo.list_exposures()
        selected_status = None
        if status:
            try:
                selected_status = ExposureStatus(status)
            except ValueError as exc:
                raise HTTPException(status_code=400, detail="Statut de filtre invalide.") from exc
            items = [item for item in items if item.status == selected_status]
        filter_links = " ".join(
            f"<a href='/exposures?{urlencode({'status': item.value})}'>{item.value}</a>"
            for item in ExposureStatus
        )
        if selected_status is not None:
            filter_links += " <a href='/exposures'>Tous</a>"
        content = f"""
        <div class="panel">
          <h2>Liste des expositions</h2>
          <p class="muted">Filtres: {filter_links}</p>
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Broker</th><th>URL</th><th>Statut</th>
                <th>Decouverte</th><th>Dernier contact</th><th>Type</th><th>Note</th>
              </tr>
            </thead>
            <tbody>{build_exposure_rows(items)}</tbody>
          </table>
        </div>
        """
        return page_template("Expositions", content, readonly=readonly)

    @app.get("/exposures/{exposure_id}", response_class=HTMLResponse)
    def exposure_detail(exposure_id: int) -> str:
        repo = Repository(resolved_db_path)
        repo.init()
        exposure = repo.get_exposure(exposure_id)
        decision = evaluate_exposure(exposure)
        mail_rows = "".join(
            (
                "<tr>"
                f"<td>{event.id}</td>"
                f"<td>{escape(event.direction.value)}</td>"
                f"<td>{escape(event.kind.value)}</td>"
                f"<td>{escape(event.subject)}</td>"
                f"<td>{escape(event.body_excerpt)}</td>"
                f"<td>{escape(event.sha256[:12])}</td>"
                "</tr>"
            )
            for event in repo.list_mail_events(exposure_id=exposure_id)
        )
        reminder_hint = (
            "Aucune relance recommandee."
            if decision.reminder_kind == ReminderKind.NONE
            else f"Relance recommandee: {decision.reminder_kind.value} ({decision.urgency})."
        )
        command_lines = "\n".join(
            [
                f"uv run pbo request generate --profile {profile} --exposure-id {exposure.id}",
                f"uv run pbo reminder generate --profile {profile} --exposure-id {exposure.id}",
                f"uv run pbo tracker export --profile {profile}",
            ]
        )
        content = f"""
        <div class="panel">
          <h2>Exposition #{exposure.id}</h2>
          <p><strong>Broker:</strong> {escape(exposure.broker_id)}</p>
          <p><strong>URL:</strong> <a href="{escape(exposure.url)}">{escape(exposure.url)}</a></p>
          <p><strong>Statut:</strong> {escape(exposure.status.value)}</p>
          <p><strong>Decouverte:</strong> {escape(exposure.discovered_at)}</p>
          <p><strong>Dernier contact:</strong> {escape(exposure.last_contact_at or '')}</p>
          <p><strong>Type:</strong> {escape(exposure.data_type)}</p>
          <p><strong>Note:</strong> {escape(exposure.note)}</p>
          <p><strong>Suivi:</strong> {escape(reminder_hint)}</p>
          {action_forms(exposure.id, readonly=readonly)}
        </div>
        <div class="panel">
          <h2>Mails traces</h2>
          <p class="muted">Seul un extrait court est affiche, jamais le contenu complet.</p>
          <table>
            <thead>
              <tr><th>ID</th><th>Direction</th><th>Type</th><th>Objet</th><th>Extrait</th><th>SHA256</th></tr>
            </thead>
            <tbody>{mail_rows}</tbody>
          </table>
        </div>
        <div class="panel">
          <h2>Commandes locales equivalentes</h2>
          <pre><code>{escape(command_lines)}</code></pre>
        </div>
        """
        return page_template(f"Exposition {exposure.id}", content, readonly=readonly)

    @app.get("/reminders", response_class=HTMLResponse)
    def reminders() -> str:
        repo = Repository(resolved_db_path)
        repo.init()
        decisions = [
            decision
            for decision in (evaluate_exposure(item) for item in repo.list_exposures())
            if decision.reminder_kind != ReminderKind.NONE
        ]
        rows = "".join(
            (
                "<tr>"
                f"<td><a href='/exposures/{decision.exposure_id}'>{decision.exposure_id}</a></td>"
                f"<td>{escape(decision.broker_id)}</td>"
                f"<td>{escape(decision.recommended_status.value)}</td>"
                f"<td>{escape(decision.reminder_kind.value)}</td>"
                f"<td>{escape(decision.urgency)}</td>"
                f"<td>{escape(decision.reason)}</td>"
                "</tr>"
            )
            for decision in decisions
        )
        content = f"""
        <div class="panel">
          <h2>Relances a faire</h2>
          <table>
            <thead>
              <tr>
                <th>ID</th><th>Broker</th><th>Statut recommande</th>
                <th>Brouillon</th><th>Urgence</th><th>Raison</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
          {export_form(readonly=readonly)}
        </div>
        """
        return page_template("Relances", content, readonly=readonly)

    @app.post("/actions/request/{exposure_id}")
    def generate_request(exposure_id: int) -> RedirectResponse:
        require_write_access(readonly)
        repo = Repository(resolved_db_path)
        repo.init()
        exposure = repo.get_exposure(exposure_id)
        broker = broker_by_id(DEFAULT_BROKERS_PATH, exposure.broker_id)
        person = load_person(paths.person_path)
        body = render_request(person, broker, exposure)
        target = paths.requests_dir / f"request_{exposure.id}_{broker.id}.txt"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        repo.mark_prepared(exposure_id)
        return RedirectResponse(url=f"/exposures/{exposure_id}", status_code=303)

    @app.post("/actions/reminder/{exposure_id}")
    def generate_reminder(exposure_id: int) -> RedirectResponse:
        require_write_access(readonly)
        repo = Repository(resolved_db_path)
        repo.init()
        exposure = repo.get_exposure(exposure_id)
        decision = evaluate_exposure(exposure)
        if decision.reminder_kind == ReminderKind.NONE:
            raise HTTPException(status_code=400, detail="Aucune relance recommandee.")
        broker = broker_by_id(DEFAULT_BROKERS_PATH, exposure.broker_id)
        person = load_person(paths.person_path)
        body = render_reminder_kind(
            person=person,
            broker=broker,
            exposure=exposure,
            days=decision.days_since_last_contact or 0,
            reminder_kind=decision.reminder_kind,
        )
        suffix = decision.reminder_kind.value.lower()
        target = paths.reminders_dir / f"reminder_{exposure.id}_{broker.id}_{suffix}.txt"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")
        return RedirectResponse(url=f"/exposures/{exposure_id}", status_code=303)

    @app.post("/actions/export-csv")
    def export_csv() -> RedirectResponse:
        require_write_access(readonly)
        repo = Repository(resolved_db_path)
        repo.init()
        repo.export_csv(paths.tracker_path)
        return RedirectResponse(url="/exposures", status_code=303)

    return app


app = create_app()
