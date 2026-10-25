# Validation V10

Commande : `python tools/smoke_test.py` (Chromium et Playwright installés), qui exécute `iteration10_test.py`. La suite lance un serveur statique temporaire pour les tests ; l'application elle-même ne lui fait aucun appel métier et fonctionne sans réseau après chargement.

Scénarios vérifiés :

- Quatre postes d'agence indépendants ; identifiants permanents, `agencyId` dans les clients et paramètres, rechargement.
- Export chiffré complet depuis chaque agence pendant que le contexte navigateur est hors ligne ; enveloppe ne contenant ni clients ni nom d'agence en clair ; déchiffrement et nombres de collections corrects.
- Phrase secrète incorrecte et texte chiffré altéré rejetés.
- Restauration chiffrée d'une base d'agence contenant 40 clients, 50 dossiers, 35 devis, 7 facturations et 8 paiements ; mêmes quantités et identifiants après restauration.
- Import des quatre agences en Direction ; numéros clients identiques acceptés avec identifiants distincts ; catalogue commun non quadruplé.
- Réimport du même fichier sans doublons ni changement d'instantané ; sélecteur d'agence ; conservation des copies après rechargement.
- Sauvegarde plus récente d'AG02 remplaçant uniquement AG02 ; sauvegarde plus ancienne refusée sans la confirmation spéciale ; autres trois instantanés identiques.
- Rejet d'une sauvegarde incomplète et d'un poste de référence inattendu ; la copie valide reste intacte.
- Ouverture des fiches client, dossier et facturation ; actions de modification désactivées et écriture métier refusée.
- KPI consolidés vérifiés contre les ventes et restes à payer calculés ; recherche globale bornée par agence et export CSV avec colonnes `agencyId`/`agencyName`.
- Chaîne HTML malveillante dans un client importé affichée comme texte, sans création d'élément `<img>` ni exécution ; aucun événement JavaScript non géré.
- Migration d'une base V9 avec données : absence de rattachement avant choix explicite, puis rattachement à AG02 et conservation après rechargement.

Contrôles complémentaires : `node --check` du JavaScript intégré, `python -m py_compile tools/iteration10_test.py`, `git diff --check`.

La recette historique V9 compare délibérément l'état IndexedDB octet pour octet à une V8, ce qui n'est plus une attente valide après l'ajout de `agencyId` et de la configuration du poste. La V10 vérifie désormais cette migration explicitement.
