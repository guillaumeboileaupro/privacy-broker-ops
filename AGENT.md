# AGENT.md

## Objectif

Ce document fixe les règles de travail pour tout agent de code ou contributeur humain intervenant sur `privacy-broker-ops`.

Le projet sert a gerer localement des demandes RGPD de suppression, opposition ou dereferencement aupres de data brokers, annuaires, moteurs de recherche et sites exposant des informations personnelles.

## Priorites

Toujours respecter cet ordre :

1. Ne pas casser l'existant.
2. Ne jamais exposer de donnees personnelles sensibles.
3. Ne jamais inventer de donnees, d'exposition, d'identite, de statut, de preuve ou de resultat.
4. Ne jamais traiter un homonyme comme confirme.
5. Produire un changement minimal, lisible et verifiable.
6. Garder le dashboard sur `127.0.0.1` par defaut.
7. Utiliser Python + `uv`.
8. Tester les changements avec `pytest` et `ruff`.

## Regles de securite

- Ne jamais envoyer automatiquement un email.
- Ne jamais confirmer une exposition sans preuve.
- Ne jamais traiter un homonyme comme une correspondance confirmee.
- Ne jamais inventer une demande envoyee, une reponse recue, une suppression confirmee ou une action CNIL.
- Ne jamais stocker de mot de passe, token, secret ou cookie dans le depot.
- Ne jamais commiter de fichier contenant des donnees personnelles reelles.
- Utiliser `person.example.yaml` pour les exemples.
- Garder les fichiers reels de l'utilisateur hors Git.
- Tout doit rester local par defaut.
- Le dashboard ne doit pas exposer de donnees sur le reseau public.
- Le dashboard doit ecouter uniquement sur `127.0.0.1` par defaut.

Ne jamais versionner :

- base SQLite reelle ;
- fichiers `.eml` reels ;
- captures d'ecran reelles ;
- preuves reelles ;
- exports ;
- fichier `person.yaml` reel ;
- `.env` ;
- token, mot de passe, cookie ou secret.

Les donnees personnelles reelles doivent rester dans des fichiers locaux ignores par Git, par exemple :

- `~/.local/share/privacy-broker-ops/profiles/default/person.yaml`
- `~/.local/share/privacy-broker-ops/profiles/default/privacy_broker_ops.db`
- `~/.local/share/privacy-broker-ops/profiles/default/mail/`
- `~/.local/share/privacy-broker-ops/profiles/default/evidence/`
- `~/.local/share/privacy-broker-ops/profiles/default/exports/`

## Regles fonctionnelles

Une exposition doit toujours avoir au minimum :

- un site ou broker ;
- une URL ;
- un statut ;
- une date de decouverte ;
- un niveau de confiance ;
- une note indiquant pourquoi elle est confirmee, a verifier ou rejetee.

Statuts autorises :

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

## Regles pour l'agent de suivi

L'agent peut :

- analyser les statuts ;
- detecter les demandes sans reponse ;
- proposer une relance ;
- generer un brouillon de relance ;
- signaler une action CNIL possible.

L'agent ne doit pas :

- envoyer un email sans validation humaine ;
- supprimer une donnee sans validation humaine ;
- modifier un statut critique sans trace ;
- inventer une reponse recue ;
- conclure qu'une suppression est faite sans preuve.

## Delais de relance

Regles par defaut :

- apres 15 jours : relance douce ;
- apres 30 jours : relance RGPD ferme ;
- apres 45 jours : dossier a preparer pour CNIL ;
- apres confirmation ecrite : passage possible en `SUPPRESSION_CONFIRMEE`.

Ces delais doivent etre configurables.

## Regles de developpement

Le projet utilise :

- Python ;
- `uv` ;
- Typer pour la CLI ;
- SQLite pour la base locale ;
- Jinja2 pour les templates ;
- pytest pour les tests ;
- Ruff pour le lint.

Ne pas remplacer cette stack sans decision explicite.

Avant de considerer une tache terminee, lancer au minimum :

```bash
uv run pytest
uv run ruff check .
```

Si `uv` ne peut pas ecrire dans `~/.cache/uv`, utiliser :

```bash
bash scripts/run-checks.sh
```

Ce script force `UV_CACHE_DIR` vers un cache local au depot.

## Regles Git et Pull Request

### Principe general

L'agent ne doit jamais prendre d'initiative Git risquee.

Le depot doit rester propre, lisible et controlable par l'utilisateur.

### Interdictions absolues

- Ne jamais creer de branche sans demande explicite.
- Ne jamais inventer un nom de branche.
- Ne jamais creer de PR sans demande explicite.
- Ne jamais faire de commit sans demande explicite.
- Ne jamais faire de push sans demande explicite.
- Ne jamais faire de merge sans demande explicite.
- Ne jamais faire de rebase, `git reset`, `git clean`, `force push` ou autre action destructive sans validation explicite.
- Ne jamais changer de branche sans verifier l'etat Git.
- Ne jamais supprimer une branche sans demande explicite.

### Fichiers interdits au commit

Ne pas commiter :

- base SQLite reelle ;
- fichiers `.eml` reels ;
- captures d'ecran reelles ;
- preuves reelles ;
- exports ;
- fichier `person.yaml` reel ;
- `.env` ;
- secret, token, mot de passe ou cookie.

### Checklist avant commit

Avant tout commit :

- verifier `git status` ;
- verifier la liste exacte des fichiers modifies ;
- verifier le diff ;
- confirmer qu'aucune donnee personnelle reelle n'est incluse ;
- confirmer qu'aucun secret n'est inclus ;
- lancer `uv run pytest` ;
- lancer `uv run ruff check .` ;
- verifier que le commit est minimal et coherent ;
- verifier que le message respecte Conventional Commits 1.0.0.

### Checklist avant push

Avant tout push :

- confirmer qu'un commit a ete demande explicitement ;
- confirmer qu'un push a ete demande explicitement ;
- re-verifier `git status` ;
- relire le diff final ;
- confirmer que la branche cible est la bonne ;
- confirmer qu'aucun fichier local, prive ou sensible n'est present ;
- confirmer qu'aucune branche, PR ou merge implicite ne sera cree automatiquement.

### Template de Pull Request

Utiliser ce template quand une PR est explicitement demandee :

```md
## Summary

- Explain the user-visible or developer-visible change.

## Changes

- List the main code or docs updates.

## Safety checks

- [ ] No real personal data added
- [ ] No secrets added
- [ ] Dashboard remains localhost-only
- [ ] No automatic email sending introduced

## Validation

- [ ] `uv run pytest`
- [ ] `uv run ruff check .`

## Notes

- Risks, limitations, or follow-up work.
```

## Convention de commits

Tous les commits doivent respecter la specification **Conventional Commits 1.0.0** :
https://www.conventionalcommits.org/en/v1.0.0/

Format obligatoire :

```text
<type>[optional scope]: <description>
```

Gestion des changements incompatibles :

- utiliser `!` apres le type ou le scope, par exemple `feat(api)!: change response format` ;
- ou ajouter un footer `BREAKING CHANGE: ...`.

Types autorises :

- `feat`
- `fix`
- `docs`
- `test`
- `refactor`
- `chore`
- `ci`
- `build`
- `style`
- `perf`
- `revert`

Scopes recommandes :

- `agent`
- `git`
- `db`
- `mail`
- `dashboard`
- `privacy`
- `broker`
- `exposure`
- `request`
- `reminder`
- `cli`
- `docs`
- `tests`
- `config`

Exemples valides :

- `docs(agent): add Git and PR workflow rules`
- `feat(db): add local profile storage`
- `feat(mail): track imported mail events`
- `fix(dashboard): keep server bound to 127.0.0.1`
- `refactor(cli): simplify request creation flow`
- `feat(api)!: change request export schema`
- `feat(api): change request export schema`
  `BREAKING CHANGE: exported JSON schema now requires broker_id`

Exemples interdits :

- `fix`
- `update`
- `stuff`
- `wip`
- `feat add thing`
- `docs:`
- `random(agent): test`
- `feat(codex): auto commit all`

Les messages de commit doivent etre sobres, descriptifs et limites a un seul sujet coherent.
