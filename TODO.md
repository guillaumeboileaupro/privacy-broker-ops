# TODO

Ce fichier pilote le projet `privacy-broker-ops`.

Règle d’usage :
- traiter les tâches dans l’ordre ;
- lancer le prompt Codex indiqué quand la tâche le demande ;
- ne pas mélanger plusieurs sujets dans une même passe Codex ;
- vérifier les tests après chaque passe ;
- ne jamais commiter/pousser sans validation explicite.

## V0 — socle local

- [X] Initialiser le projet Python avec `uv`.
- [X] Ajouter une CLI `pbo`.
- [X] Ajouter un registre `brokers.yaml`.
- [X] Ajouter une base SQLite locale.
- [X] Ajouter les modèles principaux : Broker, Exposure, Request, MailEvent.
- [X] Ajouter la génération de demandes RGPD.
- [X] Ajouter la génération de brouillons `.eml`.
- [X] Ajouter un tracker CSV.
- [X] Ajouter un agent simple pour les relances.
- [X] Ajouter un dashboard local minimal.
- [X] Ajouter des tests de base.

## Phase 1 — règles agent, Git et sécurité

- [X] Appliquer le prompt `docs/codex-prompts/01-agent-rules.md`.
- [X] Ajouter ou mettre à jour `AGENT.md`.
- [X] Ajouter les règles Git et PR strictes.
- [X] Ajouter l’obligation Conventional Commits 1.0.0.
- [X] Ajouter le template de PR.
- [X] Ajouter les checklists avant commit et push.
- [X] Vérifier que l’agent ne peut pas inventer de branche, PR, commit ou push.
- [X] Lancer `uv run pytest`.
- [X] Lancer `uv run ruff check .`.

## Phase 2 — stockage local privé par profil

- [X] Appliquer le prompt `docs/codex-prompts/02-local-private-storage.md`.
- [X] Séparer données versionnées et données privées locales.
- [X] Ajouter le stockage par profil `default`.
- [X] Ajouter le stockage par profil nommé avec `--profile <name>`.
- [X] Stocker les données privées dans `~/.local/share/privacy-broker-ops/profiles/<profile>/`.
- [X] Corriger `.gitignore`.
- [X] Retirer toute DB réelle ou donnée privée du repo si présente.
- [X] Mettre à jour README et AGENT.
- [X] Lancer `uv run pytest`.
- [X] Lancer `uv run ruff check .`.

## Phase 3 — suivi des mails

- [ ] Appliquer le prompt `docs/codex-prompts/03-mail-events.md`.
- [ ] Ajouter ou compléter la table `mail_events`.
- [ ] Stocker les `.eml` hors Git dans le profil local.
- [ ] Ajouter `sha256` pour tracer les preuves.
- [ ] Ajouter `pbo mail import`.
- [ ] Importer `.eml` et `.txt`.
- [ ] Ne stocker qu’un extrait court du corps dans la DB.
- [ ] Ajouter des tests d’import mail avec données fictives.
- [ ] Lancer `uv run pytest`.
- [ ] Lancer `uv run ruff check .`.

## Phase 4 — relances et agent de suivi

- [ ] Appliquer le prompt `docs/codex-prompts/04-reminder-agent.md`.
- [ ] Ajouter la règle J+15 : relance douce.
- [ ] Ajouter la règle J+30 : relance RGPD ferme.
- [ ] Ajouter la règle J+45 : `CNIL_A_ENVISAGER`.
- [ ] Ajouter `pbo agent check`.
- [ ] Ajouter `pbo reminder generate`.
- [ ] Ajouter un résumé terminal urgent / bientôt / ok.
- [ ] Ajouter des tests sur les délais de relance.
- [ ] Lancer `uv run pytest`.
- [ ] Lancer `uv run ruff check .`.

## Phase 5 — dashboard minimal renforcé

- [ ] Appliquer le prompt `docs/codex-prompts/05-dashboard.md`.
- [ ] Garder le dashboard sur `127.0.0.1` par défaut.
- [ ] Ajouter une page détail par exposition.
- [ ] Ajouter des filtres par statut.
- [ ] Ajouter une page “Relances à faire”.
- [ ] Ajouter un mode lecture seule.
- [ ] Ajouter un export CSV depuis le dashboard.
- [ ] Ne pas afficher de secret ou donnée sensible inutile.
- [ ] Lancer `uv run pytest`.
- [ ] Lancer `uv run ruff check .`.

## Phase 6 — documentation et workflow final

- [ ] Appliquer le prompt `docs/codex-prompts/06-docs-and-final-check.md`.
- [ ] Mettre à jour README.
- [ ] Mettre à jour TODO.
- [ ] Mettre à jour AGENT.
- [ ] Ajouter les exemples de commandes.
- [ ] Ajouter une section “Données privées et Git”.
- [ ] Ajouter une section “Workflow Codex”.
- [ ] Lancer `uv run pytest`.
- [ ] Lancer `uv run ruff check .`.

## Git / PR / workflow agent

- [X] Interdire création de branche sans demande explicite.
- [X] Interdire nom de branche inventé.
- [X] Interdire PR sans demande explicite.
- [X] Interdire push sans demande explicite.
- [X] Interdire merge/rebase/reset destructif sans validation.
- [X] Interdire force push.
- [X] Ajouter un template PR dans `AGENT.md`.
- [X] Ajouter une checklist avant commit/push.
- [X] Vérifier que `.gitignore` protège les DB, mails, preuves et fichiers personnels.

## Conventional Commits

- [X] Ajouter dans `AGENT.md` l’obligation de respecter Conventional Commits 1.0.0.
- [X] Définir les types autorisés : `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `ci`, `build`, `style`, `perf`, `revert`.
- [X] Définir les scopes recommandés : `agent`, `git`, `db`, `mail`, `dashboard`, `privacy`, `broker`, `exposure`, `request`, `reminder`, `cli`, `docs`, `tests`, `config`.
- [X] Ajouter des exemples valides et interdits.
- [X] Interdire les messages vagues : `fix`, `update`, `stuff`, `wip`.
- [X] Ajouter la checklist avant commit.

## Rappel de sécurité

Ne jamais versionner : DB réelle, `.eml` réel, `person.yaml` réel, preuve réelle, capture réelle, export réel, `.env`, token, cookie, mot de passe ou secret.
