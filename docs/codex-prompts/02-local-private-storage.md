# Prompt Codex — 02 — Stockage local privé par profil

Tu travailles sur le projet `privacy-broker-ops`.

Objectif : corriger l’architecture de stockage pour séparer strictement les fichiers versionnés et les données personnelles locales privées.

Règle principale : le dépôt Git ne doit contenir aucune donnée personnelle réelle, aucun email réel, aucune DB réelle, aucune preuve réelle.

Données versionnées dans le repo :
- `data/brokers.yaml`
- `data/person.example.yaml`
- migrations SQL si le projet en utilise
- tests avec données fictives

Données locales privées hors Git :
- `~/.local/share/privacy-broker-ops/profiles/<profile>/privacy_broker_ops.db`
- `~/.local/share/privacy-broker-ops/profiles/<profile>/person.yaml`
- `~/.local/share/privacy-broker-ops/profiles/<profile>/mail/`
- `~/.local/share/privacy-broker-ops/profiles/<profile>/evidence/`
- `~/.local/share/privacy-broker-ops/profiles/<profile>/exports/`

À faire :
1. Ajouter la notion de profil utilisateur avec profil par défaut `default` et option `--profile <name>`.
2. Ajouter `pbo init`, `pbo init --profile guillaume`, `pbo exposure add --profile guillaume`, `pbo agent check --profile guillaume`, `pbo dashboard --profile guillaume`.
3. Centraliser la résolution du chemin de profil.
4. Corriger `.gitignore` pour exclure instance/, *.db, *.sqlite, *.sqlite3, data/person.yaml, out/, exports/, evidence/, screenshots/, mail/, *.eml, .env, .env.*.
5. Vérifier que les tests utilisent `tmp_path / "test.db"`.
6. Mettre à jour README, TODO, AGENT, .gitignore et code DB.
7. Ajouter tests profil default, profil nommé, création dossier profil, DB temporaire.
8. Lancer `uv run pytest` et `uv run ruff check .`.

Ne fais pas de commit. Ne crée pas de branche. Ne pousse rien.
