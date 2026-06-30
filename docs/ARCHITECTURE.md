# Architecture

```text
CLI pbo
  ├── brokers.yaml
  ├── data/person.yaml local non commité
  ├── SQLite privacy_broker_ops.db local non commité
  ├── templates Jinja2
  ├── agent relances
  └── dashboard FastAPI local
```

## Flux principal

1. Recherche manuelle ou assistée d’une exposition.
2. Ajout dans la base avec `pbo exposure add`.
3. Qualification : `A_VERIFIER`, `HOMONYME` ou `CONFIRME`.
4. Génération de demande RGPD.
5. Envoi manuel par l’utilisateur.
6. Marquage envoyé dans une future commande.
7. Agent de suivi pour les relances.
8. Dashboard local pour voir l’état global.

## Pourquoi pas d’envoi automatique en V0 ?

Parce que les annuaires et people-search contiennent beaucoup d’homonymes. Le projet doit éviter d’envoyer des demandes fausses ou excessives. L’automatisation sert à préparer, classer et suivre ; la validation humaine reste obligatoire.
