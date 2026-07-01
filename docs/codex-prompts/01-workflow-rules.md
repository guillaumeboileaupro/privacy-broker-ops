# Prompt Codex — 01 — Workflow, Git, PR et Conventional Commits

Tu travailles sur le projet `privacy-broker-ops`.

Objectif : ajouter ou mettre à jour `AGENT.md` avec des règles strictes de sécurité, de Git, de PR et de commits.

Contraintes absolues :
- Ne pas casser l’existant.
- Ne pas inventer de données.
- Ne pas envoyer d’email automatiquement.
- Ne pas traiter un homonyme comme confirmé.
- Ne pas commiter de données personnelles réelles.
- Garder le dashboard sur localhost.
- Utiliser Python + uv.
- Vérifier avec pytest et ruff.
- Ne pas créer de branche, PR, commit ou push sans demande explicite.

À faire :
1. Créer ou mettre à jour `AGENT.md` à la racine du projet.
2. Ajouter les sections : Objectif, Priorités, Règles de sécurité, Règles Git et Pull Request, Convention de commits.
3. Dans Git/PR, interdire : branche sans demande, nom inventé, PR sans demande, push sans demande, merge sans demande, rebase/reset/force push/clean destructif sans validation, commit de DB/mails/preuves/exports/person.yaml/.env/secrets.
4. Ajouter une checklist avant commit et avant push.
5. Ajouter un template de PR.
6. Imposer Conventional Commits 1.0.0 : https://www.conventionalcommits.org/en/v1.0.0/
7. Format obligatoire : `<type>[optional scope]: <description>`.
8. Types autorisés : feat, fix, docs, test, refactor, chore, ci, build, style, perf, revert.
9. Scopes recommandés : agent, git, db, mail, dashboard, privacy, broker, exposure, request, reminder, cli, docs, tests, config.
10. Ajouter des exemples valides et interdits.
11. Ajouter la gestion des BREAKING CHANGE avec `!` ou footer.
12. Mettre à jour `TODO.md`.
13. Lancer `uv run pytest` et `uv run ruff check .`.

Ne fais pas de commit. Ne crée pas de branche. Ne pousse rien.
