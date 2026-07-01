# Prompt Codex — 06 — Documentation et vérification finale

Tu travailles sur le projet `privacy-broker-ops`.

Objectif : mettre à jour la documentation et vérifier que le projet est cohérent après les changements.

À faire :
1. Mettre à jour README avec objectif, installation uv, commandes, profils, données privées, sécurité Git, dashboard, import mail, agent relance, limites V0.
2. Mettre à jour TODO : cocher uniquement ce qui est réellement terminé.
3. Mettre à jour AGENT si les règles ne couvrent pas stockage local, mail events, relances, Git/PR, Conventional Commits, données privées hors Git.
4. Vérifier `.gitignore` : instance/, *.db, *.sqlite, *.sqlite3, data/person.yaml, out/, exports/, evidence/, screenshots/, mail/, *.eml, .env, .env.*.
5. Vérifier que le repo ne contient pas DB réelle, .eml réel, person.yaml réel, preuve réelle, capture réelle, export réel, .env, token, cookie, mot de passe ou secret.
6. Lancer `uv run pytest` et `uv run ruff check .`.
7. Produire un résumé : fichiers modifiés, tests lancés, limites restantes, TODO ouverts.

Ne fais pas de commit. Ne crée pas de branche. Ne pousse rien.
