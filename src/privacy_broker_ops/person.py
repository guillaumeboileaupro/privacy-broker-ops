from __future__ import annotations

from pathlib import Path

import yaml

from .models import Person


def load_person(path: Path) -> Person:
    if not path.exists():
        raise FileNotFoundError(
            "Fichier personne introuvable: "
            f"{path}. Cree un fichier local a partir de data/person.example.yaml."
        )
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return Person.model_validate(data)
