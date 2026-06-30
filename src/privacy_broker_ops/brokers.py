from __future__ import annotations

from pathlib import Path

import yaml

from .models import Broker


def load_brokers(path: Path) -> list[Broker]:
    if not path.exists():
        raise FileNotFoundError(f"Registre brokers introuvable: {path}")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
    return [Broker.model_validate(item) for item in data]


def broker_by_id(path: Path, broker_id: str) -> Broker:
    for broker in load_brokers(path):
        if broker.id == broker_id:
            return broker
    raise ValueError(f"Broker introuvable: {broker_id}")
