# Privacy Broker Ops

Outil local pour suivre les demandes RGPD de suppression/opposition auprès de data brokers, annuaires, moteurs de recherche et sites de recherche de personnes.

Le principe est simple : on centralise les expositions trouvées, on génère des demandes propres, on garde les preuves, on suit les délais, puis on prépare les relances. En V0, l’outil **ne fait aucun envoi automatique** : il prépare des fichiers et brouillons pour validation humaine.

## Objectifs

- Inventorier les sites qui exposent des informations personnelles.
- Distinguer clairement les fiches confirmées, les homonymes et les cas à vérifier.
- Générer des demandes RGPD en français.
- Générer des brouillons `.eml` prêts à importer/envoyer.
- Suivre les statuts et les relances dans une base SQLite locale.
- Afficher un dashboard local très simple.

## Stack

- Python 3.12+
- `uv`
- Typer pour la CLI
- SQLite local
- Pydantic pour les modèles
- Jinja2 pour les templates
- Rich pour le terminal
- FastAPI/Uvicorn pour le dashboard local

## Installation

```bash
uv sync
```

Vérifier la CLI :

```bash
uv run pbo --help
```

## Démarrage rapide

Initialiser la base locale :

```bash
uv run pbo init
```

Lister les brokers connus :

```bash
uv run pbo brokers list
```

Ajouter une exposition :

```bash
uv run pbo exposure add \
  --broker idcrawl \
  --url "https://example.com/profile" \
  --status A_VERIFIER \
  --data-type "profil public" \
  --note "À vérifier avant toute demande"
```

Lister les expositions :

```bash
uv run pbo exposure list
```

Générer une demande RGPD :

```bash
uv run pbo request generate --exposure-id 1 --out out/requests
```

Générer un brouillon `.eml` :

```bash
uv run pbo request eml --exposure-id 1 --out out/eml
```

Vérifier les relances à faire :

```bash
uv run pbo agent check
```

Exporter le tracker :

```bash
uv run pbo tracker export --out out/tracker.csv
```

Lancer le dashboard :

```bash
uv run pbo dashboard
```

Puis ouvrir :

```text
http://127.0.0.1:8080
```

## Statuts

- `A_VERIFIER`
- `HOMONYME`
- `CONFIRME`
- `DEMANDE_PREPAREE`
- `ENVOYE`
- `REPONSE_RECUE`
- `SUPPRESSION_CONFIRMEE`
- `REFUS`
- `JUSTIFICATIF_DEMANDE`
- `RELANCE_A_FAIRE`
- `CNIL_A_ENVISAGER`
- `CLOS`

## Règles de sécurité

- Ne jamais traiter un homonyme comme une fiche confirmée.
- Ne jamais envoyer d’email automatiquement en V0.
- Toujours garder l’URL, la date et le statut.
- Ne pas stocker de documents sensibles inutiles dans le dépôt.
- Le fichier `data/person.yaml` est ignoré par Git.
- Les sorties `out/` et la base `*.db` sont ignorées par Git.

## Configuration personnelle

Copier l’exemple :

```bash
cp data/person.example.yaml data/person.yaml
```

Puis modifier `data/person.yaml`. Ce fichier ne doit pas être commité.

## Tests

```bash
uv run pytest
```

Lint :

```bash
uv run ruff check .
```

## Roadmap courte

Voir [`TODO.md`](TODO.md).
