# Prompt Codex — 03 — Import et suivi des mails

Tu travailles sur le projet `privacy-broker-ops`.

Objectif : stocker les mails comme des événements traçables sans versionner les emails réels ni stocker trop de contenu sensible.

Règles :
- Les fichiers `.eml` réels restent hors Git.
- Les fichiers `.eml` sont stockés dans le profil local utilisateur.
- La DB garde le chemin local, un hash SHA-256 et un extrait court.
- Ne jamais envoyer automatiquement un email.
- Ne jamais importer un mail réel dans les tests.

Chemin local attendu : `~/.local/share/privacy-broker-ops/profiles/<profile>/mail/` avec sous-dossiers inbox/, sent/, drafts/.

Table `mail_events` : id, exposure_id, broker_id, direction, kind, subject, from_address, to_address, sent_at, received_at, status, eml_path, body_excerpt, sha256, created_at.

Valeurs : direction OUTBOUND/INBOUND ; kind REQUEST/REMINDER/RESPONSE/OTHER.

À faire :
1. Créer ou compléter le modèle `MailEvent`.
2. Créer ou compléter la table `mail_events`.
3. Ajouter `pbo mail import --profile <profile> --file <path> --exposure-id <id>`.
4. Accepter `.eml` et `.txt`.
5. Copier le fichier dans le dossier local du profil, calculer SHA-256, extraire sujet/from/to si possible, stocker un extrait court.
6. Ajouter `pbo mail list --profile <profile>`.
7. Ajouter tests fictifs import txt, import eml minimal, hash, stockage temp.
8. Mettre à jour README, TODO, AGENT.
9. Lancer `uv run pytest` et `uv run ruff check .`.

Ne fais pas de commit. Ne crée pas de branche. Ne pousse rien.
