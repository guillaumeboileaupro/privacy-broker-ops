from __future__ import annotations

from collections import Counter
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .config import resolve_profile_paths
from .models import ExposureStatus
from .repository import Repository


def create_app(db_path: Path | None = None) -> FastAPI:
    resolved_db_path = db_path or resolve_profile_paths().db_path
    app = FastAPI(title="Privacy Broker Ops")

    @app.get("/", response_class=HTMLResponse)
    def index() -> str:
        repo = Repository(resolved_db_path)
        repo.init()
        exposures = repo.list_exposures()
        counts = Counter(e.status.value for e in exposures)
        rows = "".join(
            (
                f"<tr><td>{e.id}</td><td>{e.broker_id}</td>"
                f"<td><a href='{e.url}'>{e.url}</a></td>"
                f"<td>{e.status.value}</td><td>{e.discovered_at}</td>"
                f"<td>{e.last_contact_at or ''}</td>"
                f"<td>{e.data_type}</td><td>{e.note}</td></tr>"
            )
            for e in exposures
        )
        cards = "".join(
            (
                "<div class='card'>"
                f"<strong>{status.value}</strong><br>{counts.get(status.value, 0)}"
                "</div>"
            )
            for status in ExposureStatus
        )
        return f"""
        <!doctype html>
        <html lang="fr">
        <head>
          <meta charset="utf-8">
          <title>Privacy Broker Ops</title>
          <style>
            body {{ font-family: system-ui, sans-serif; margin: 2rem; background: #f6f6f6; }}
            h1 {{ margin-bottom: .2rem; }}
            .cards {{ display: flex; flex-wrap: wrap; gap: .7rem; margin: 1rem 0; }}
            .card {{
              background: white;
              border: 1px solid #ddd;
              border-radius: 8px;
              padding: .8rem;
              min-width: 150px;
            }}
            table {{ width: 100%; border-collapse: collapse; background: white; }}
            th, td {{
              border: 1px solid #ddd;
              padding: .45rem;
              font-size: .9rem;
              vertical-align: top;
            }}
            th {{ background: #eee; text-align: left; }}
            a {{ color: #222; }}
          </style>
        </head>
        <body>
          <h1>Privacy Broker Ops</h1>
          <p>Dashboard local de suivi RGPD.</p>
          <div class="cards">
            <div class='card'><strong>Total</strong><br>{len(exposures)}</div>
            {cards}
          </div>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Broker</th>
                <th>URL</th>
                <th>Statut</th>
                <th>Découverte</th>
                <th>Dernier contact</th>
                <th>Type</th>
                <th>Note</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
        </body>
        </html>
        """

    return app


app = create_app()
