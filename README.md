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

Initialiser le profil local par defaut :

```bash
uv run pbo init
```

Initialiser un profil nomme :

```bash
uv run pbo init --profile guillaume
```

Lister les brokers connus :

```bash
uv run pbo brokers list
```

Ajouter une exposition :

```bash
uv run pbo exposure add \
  --profile guillaume \
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
uv run pbo request generate --profile guillaume --exposure-id 1
```

Générer un brouillon `.eml` :

```bash
uv run pbo request eml --profile guillaume --exposure-id 1
```

Importer un mail recu ou un brouillon local dans le suivi :

```bash
uv run pbo mail import \
  --profile guillaume \
  --file /tmp/reponse.eml \
  --exposure-id 1
```

Lister les mails traces :

```bash
uv run pbo mail list --profile guillaume
```

Vérifier les relances à faire :

```bash
uv run pbo agent check --profile guillaume
```

Generer un brouillon de relance :

```bash
uv run pbo reminder generate --profile guillaume --exposure-id 1
```

Exporter le tracker :

```bash
uv run pbo tracker export --profile guillaume
```

Lancer le dashboard :

```bash
uv run pbo dashboard --profile guillaume
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
- Les donnees locales privees doivent rester hors du depot Git.
- Les sorties `out/` et la base `*.db` sont ignorees par Git si elles existent dans le repo.

## Configuration personnelle

Le registre versionne reste dans le repo :

```bash
data/brokers.yaml
```

Les donnees privees locales par profil vont dans :

```text
~/.local/share/privacy-broker-ops/profiles/<profile>/
```

Fichiers principaux :

```text
~/.local/share/privacy-broker-ops/profiles/<profile>/privacy_broker_ops.db
~/.local/share/privacy-broker-ops/profiles/<profile>/person.yaml
~/.local/share/privacy-broker-ops/profiles/<profile>/mail/
~/.local/share/privacy-broker-ops/profiles/<profile>/mail/inbox/
~/.local/share/privacy-broker-ops/profiles/<profile>/mail/sent/
~/.local/share/privacy-broker-ops/profiles/<profile>/mail/drafts/
~/.local/share/privacy-broker-ops/profiles/<profile>/evidence/
~/.local/share/privacy-broker-ops/profiles/<profile>/exports/
```

Creer ensuite le fichier local personne a partir de l'exemple versionne :

```bash
cp data/person.example.yaml ~/.local/share/privacy-broker-ops/profiles/default/person.yaml
```

Ou pour un profil nomme :

```bash
cp data/person.example.yaml ~/.local/share/privacy-broker-ops/profiles/guillaume/person.yaml
```

Ces fichiers ne doivent jamais etre commites.

## Suivi des mails

Les fichiers `.eml` et `.txt` importes restent hors Git dans le profil local.

La base `mail_events` conserve uniquement :

- le chemin local du fichier ;
- un hash `sha256` ;
- un extrait court du corps ;
- les metadonnees utiles : sujet, expediteur, destinataire, dates et type.

## Agent de relance

Regles par defaut :

- J+15 : relance douce
- J+30 : relance RGPD ferme
- J+45 : preparation CNIL
- aucune relance pour `CLOS`, `SUPPRESSION_CONFIRMEE`, `HOMONYME`, `REFUS`

## Tests

```bash
uv run pytest
```

Lint :

```bash
uv run ruff check .
```

Si `uv` ne peut pas ecrire dans `~/.cache/uv` dans un environnement contraint, utiliser le script du depot :

```bash
bash scripts/run-checks.sh
```

Il force un cache writable dans `.cache/uv` a la racine du projet via `UV_CACHE_DIR`.

Si `uv` ne peut pas telecharger les dependances, le script accepte aussi des fallbacks locaux deja installes :

```bash
PBO_TEST_PYTHON=/path/to/python \
PBO_RUFF_BIN=/path/to/ruff \
bash scripts/run-checks.sh
```

## Roadmap courte

Voir [`TODO.md`](TODO.md).
