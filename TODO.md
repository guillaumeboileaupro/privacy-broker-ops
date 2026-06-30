# TODO

## V0 — socle local

- [x] Initialiser le projet Python avec `uv`.
- [x] Ajouter une CLI `pbo`.
- [x] Ajouter un registre `brokers.yaml`.
- [x] Ajouter une base SQLite locale.
- [x] Ajouter les modèles principaux : Broker, Exposure, Request, MailEvent.
- [x] Ajouter la génération de demandes RGPD.
- [x] Ajouter la génération de brouillons `.eml`.
- [x] Ajouter un tracker CSV.
- [x] Ajouter un agent simple pour les relances.
- [x] Ajouter un dashboard local minimal.
- [x] Ajouter des tests de base.

## V0.1 — durcissement

- [ ] Ajouter une commande `pbo exposure update-status`.
- [ ] Ajouter une commande `pbo mail import` pour importer une réponse `.eml` ou `.txt`.
- [ ] Ajouter une table `mail_events` réellement alimentée par l’import.
- [ ] Ajouter un champ `proof_path` pour les captures/preuves locales.
- [ ] Ajouter un export JSON complet.
- [ ] Ajouter des tests sur les délais de relance.
- [ ] Ajouter un mode lecture seule du dashboard.

## V0.2 — agent de suivi

- [ ] Détecter les réponses positives : suppression confirmée, dossier clos.
- [ ] Détecter les refus.
- [ ] Détecter les demandes de justificatif.
- [ ] Générer une relance douce à J+15.
- [ ] Générer une relance ferme RGPD à J+30.
- [ ] Marquer `CNIL_A_ENVISAGER` à J+45 sans réponse.
- [ ] Ajouter un résumé terminal lisible : urgent / bientôt / ok.

## V0.3 — dashboard

- [ ] Ajouter une page détail par exposition.
- [ ] Ajouter des boutons pour générer une demande ou une relance.
- [ ] Ajouter des filtres par statut.
- [ ] Ajouter un compteur par broker.
- [ ] Ajouter un export CSV depuis le dashboard.

## V1 — intégration mail contrôlée

- [ ] Ajouter Gmail OAuth en lecture seule.
- [ ] Associer les réponses reçues aux demandes envoyées.
- [ ] Créer des brouillons Gmail de relance.
- [ ] Ne jamais envoyer automatiquement sans validation humaine.

## V2 — recherche semi-automatique

- [ ] Ajouter un module de recherche manuelle assistée.
- [ ] Ajouter une liste de requêtes à lancer dans Google/Bing.
- [ ] Ajouter des connecteurs par site uniquement quand c’est légal et stable.
- [ ] Ajouter une étape de validation humaine avant toute classification `CONFIRME`.
