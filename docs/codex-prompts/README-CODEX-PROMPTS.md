# Codex prompts

Ce dossier contient des prompts prêts à donner à Codex, dans l’ordre.

## Ordre recommandé

1. `01-agent-rules.md`
2. `02-local-private-storage.md`
3. `03-mail-events.md`
4. `04-reminder-agent.md`
5. `05-dashboard.md`
6. `06-docs-and-final-check.md`

## Règles d’utilisation

- Faire une seule phase à la fois.
- Lire le diff après chaque phase.
- Lancer les tests après chaque phase.
- Ne pas autoriser Codex à créer une branche, une PR, un commit ou un push sans demande explicite.
- Ne jamais accepter un changement qui ajoute des données personnelles réelles au dépôt.

## Commandes de vérification

```bash
uv run pytest
uv run ruff check .
git status
git diff --stat
```

## Convention de commits

Quand un commit sera explicitement demandé, utiliser Conventional Commits :

```bash
git commit -m "docs(agent): add Git and PR workflow rules"
git commit -m "feat(db): add local profile storage"
git commit -m "feat(mail): track imported mail events"
```
