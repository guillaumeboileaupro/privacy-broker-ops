# Prompt Codex — 04 — Suivi et relances

Tu travailles sur le projet `privacy-broker-ops`.

Objectif : renforcer l’agent de suivi pour détecter les relances à faire et générer des brouillons sans envoyer automatiquement.

Règles : l’agent peut analyser/proposer/générer un brouillon, mais ne doit jamais envoyer automatiquement, conclure une suppression sans preuve, ni traiter un homonyme comme confirmé.

Statuts : A_VERIFIER, HOMONYME, CONFIRME, DEMANDE_PREPAREE, ENVOYE, REPONSE_RECUE, SUPPRESSION_CONFIRMEE, REFUS, JUSTIFICATIF_DEMANDE, RELANCE_A_FAIRE, CNIL_A_ENVISAGER, CLOS.

Règles de relance : J+15 relance douce ; J+30 relance RGPD ferme ; J+45 CNIL_A_ENVISAGER ; aucune relance si CLOS, SUPPRESSION_CONFIRMEE, HOMONYME, REFUS ; aucune relance sans date d’envoi.

À faire :
1. Ajouter/corriger `pbo agent check --profile <profile>` avec sortie urgent/bientôt/ok.
2. Ajouter/corriger `pbo reminder generate --profile <profile> --exposure-id <id>`.
3. Ajouter templates reminder_soft_fr.txt.j2, reminder_formal_fr.txt.j2, cnil_prepare_fr.txt.j2.
4. Ajouter tests : avant J+15, J+15, J+30, J+45, CLOS, SUPPRESSION_CONFIRMEE, HOMONYME.
5. Mettre à jour README, TODO, AGENT.
6. Lancer `uv run pytest` et `uv run ruff check .`.

Ne fais pas de commit. Ne crée pas de branche. Ne pousse rien.
