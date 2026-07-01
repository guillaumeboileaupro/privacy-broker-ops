# Prompt Codex — 05 — Dashboard local minimal

Tu travailles sur le projet `privacy-broker-ops`.

Objectif : renforcer le dashboard local en gardant une interface simple, locale et sûre.

Règles : écouter sur 127.0.0.1 par défaut ; ne pas exposer sur le réseau public ; ne pas afficher de secret ; ne pas afficher de contenu complet d’email ; ne jamais envoyer automatiquement ; ajouter un mode lecture seule.

À faire :
1. Ajouter/corriger `pbo dashboard --profile <profile>`.
2. Options : `--host 127.0.0.1`, `--port 8080`, `--readonly`.
3. Ajouter vues : accueil avec compteurs, liste expositions, détail exposition, relances à faire, filtre statut, compteur par broker.
4. Actions sûres : générer demande, générer relance, exporter CSV. Ces actions créent des fichiers locaux, jamais d’envoi automatique.
5. Tests : dashboard sur 127.0.0.1, HTML compteurs, readonly sans action écriture, aucun secret affiché.
6. Mettre à jour README, TODO, AGENT.
7. Lancer `uv run pytest` et `uv run ruff check .`.

Ne fais pas de commit. Ne crée pas de branche. Ne pousse rien.
