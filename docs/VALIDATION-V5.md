# Recette V5 — résultats et limites

## Exécution

Les quatre suites du lanceur `tools/smoke_test.py` ont terminé avec succès dans Chromium :

1. `iteration5_test.py` — parcours commercial et financier complet.
2. `migration5_test.py` — migration réelle d’une base V4 et lecture de sauvegardes V1 à V4.
3. `iteration4_test.py` — tests d’administration adaptés aux nouvelles règles V5.
4. `filters_test.py` — filtres, tri, catalogue, recherche et performance, adaptés au composant de période unique.

Ce sont des outils facultatifs de développement. Les opérations métier ont été exercées avec le réseau désactivé après chargement initial ; aucun outil Python n’est appelé par l’application.

## Parcours commercial vérifié

- Un client possède deux dossiers indépendants.
- Dossier à deux lignes : 10 × 100 € HT et 20 × 50 € HT, TVA 20 % = 2 000 € HT, 400 € TVA, 2 400 € TTC.
- Devis créé depuis ces lignes sans ressaisie, brouillon, émission, conditions et validité.
- Modification du catalogue sans changement de l’instantané émis.
- Nouvelle version conservant l’ancienne ; remplacement de la version de référence et acceptation explicite de la nouvelle.
- Une acceptation de devis ne crée pas encore de facture ni de paiement.
- Relance rattachée au dossier, avec état et date, puis annulation lors de la confirmation.
- Confirmation explicite créant une seule vente confirmée et un seul dossier de facturation. Répéter l’action ne crée pas de doublon.
- Brouillon de facturation sans numéro de facture final ; émission séparée attribuant le numéro FAC.

## Paiements et documents

- Acompte proposé à 1 200 € sur 2 400 € TTC ; date réelle antérieure acceptée.
- Double soumission simultanée du formulaire d’acompte ne crée qu’un paiement.
- Solde initial de 1 200 € ; tentative de 1 300 € refusée sans écriture.
- Solde enregistré, puis correction de l’acompte à 1 000 € : ancien enregistrement conservé et marqué annulé/corrigé, reste dû de 200 €, état partiel.
- Réception des derniers 200 € : montant effectivement reçu de 2 400 €, reste 0 €, état Payé intégralement.
- Cas limite testé séparément : 2 399,99 € encaissés sur 2 400 € restent un règlement partiel, avec 0,01 € dû ; aucun affichage « 100 % » ou « Payé intégralement ».
- Annulation d’une émission avec motif, conservation du snapshot et réservation de l’ancien numéro, nouvelle émission distincte sans doubler la vente.
- KPI contrôlés : une vente confirmée et une facture active malgré deux lignes et plusieurs règlements ; versions remplacées exclues du taux d’acceptation des propositions courantes.
- Appel à `window.print()` vérifié avec un espion de test ; styles d’impression contrôlés par émulation. Deux PDF ont été produits par le moteur headless pour examiner le rendu : un document A4 d’une page et un document synthétique de 90 lignes sur cinq pages. Les en-têtes de tableau sont répétés et les menus du CRM sont absents.
- L’interface ne génère pas silencieusement un PDF : le bouton ouvre le mécanisme natif du navigateur, où l’utilisateur choisit l’impression ou l’enregistrement PDF.

## Recherche, interface et référentiels

- Entrée sans sélection dans les suggestions ouvre la page complète de résultats.
- Sections Tous/Clients/Produits/Opportunités/Devis/Factures, compteurs, tris et pagination ; flèche + Entrée continue d’ouvrir directement la fiche sélectionnée.
- Un seul composant de période client ; changement création/modification conservant les dates ; filtre Rue absent.
- Badges particuliers/professionnels distincts et textuels.
- Traçabilité masquée par défaut, réactivable immédiatement et persistante ; les dates commerciales restent visibles.
- Unités en liste, normalisation sûre des équivalences, ajout d’une unité autorisée, documents existants préservés.
- Filtres clients multi-villes et préfixes postaux, recherche produit sans accents et multi-mots, filtres techniques et prix, tri numérique/naturel avant pagination.
- Recherche de 10 000 clients : 5 000 résultats exacts avec critères combinés et rendu paginé en environ 58–68 ms dans les derniers passages de la recette. Mesure indicative selon la machine.
- Filtres et exports CSV conservés dans les onglets Devis et Facturation, sans recréer une page autonome de devis.
- Captures ordinateur et tablette examinées. Catalogue et paramètres restent dans la zone inférieure du menu sur ordinateur.

## Préservation des données

- Base V4 réellement initialisée dans le navigateur, puis ouverture de V5 sur la même origine et le même magasin IndexedDB.
- Identifiants clients, opportunités, devis, factures et lignes historiques inchangés.
- Ancien Accepté conservé dans `legacyStage` et signalé à vérifier, sans fabriquer de confirmation.
- Ancien état Payée sans preuve détaillée : aucun paiement ni date inventé, état de rapprochement explicite.
- Devis/facture/relance initialement non rattachés reliés à un dossier historique ; rechargement sans recréation de ces dossiers ni changement de leurs identifiants.
- Confirmation explicite d’un dossier historique réutilisant sa facture existante ; rapprochement d’un paiement réel sans supposer l’encaissement total.
- Sauvegardes V1, V2, V3 et V4 lues et migrées sans perte d’identifiants ou création de paiement fictif.
- Sauvegarde V5 exportée, restaurée via le sélecteur de fichier et retrouvée après rechargement.
- Données fictives V5 : 40 clients et 50 projets, devis, confirmations, factures et paiements cohérents ; suppression ramenant aux données réelles, sans perdre les règlements de recette réels.
- Imports clients JSON/CSV avec aperçu, identifiants stables, SIRET et zéros initiaux ; conflits bloqués et associations existantes maintenues.
- Export HTML avec image synthétique de recette ouvert dans un contexte vierge sans autre fichier : programme/catalogue/image présents, données privées, contenu d’impression et titres de documents absents. Le fixture n’est pas présenté comme le logo officiel.
- Contrôles de sauvegarde : références relationnelles, doublons, confirmations uniques, montants, corrections de paiements, dates réelles et instantanés cohérents. Une date de règlement impossible et une confirmation dupliquée sont refusées.
- Catalogue source embarqué identique au commit précédent : 3 283 lignes. Les normalisations s’appliquent à la base locale sans tronquer le catalogue.

## Limites

- `file://` reste bloqué dans le Chromium géré du cloud (`ERR_BLOCKED_BY_ADMINISTRATOR`). Le fichier n’utilise aucun serveur ni ressource distante, mais l’ouverture locale et la politique de stockage doivent être vérifiées dans le navigateur cible.
- La fenêtre d’impression du système n’a pas été manipulée ; le déclenchement natif et le rendu PDF A4 du moteur ont été vérifiés. Le navigateur cible doit autoriser l’impression/enregistrement PDF.
- Les coordonnées légales de l’émetteur doivent être renseignées et les mentions applicables vérifiées. L’outil n’est pas présenté comme une certification de facturation électronique. L’annulation d’une émission ne crée ni remboursement ni avoir fiscal automatique.
- Les données historiques ambiguës demandent un rapprochement humain ; les informations absentes ne sont pas déduites arbitrairement.
- Le logo officiel reste à fournir comme fichier binaire accessible ou à importer dans Paramètres. La marque textuelle est utilisée tant qu’aucune image n’est configurée ; aucune approximation n’a été dessinée.
- Application locale à une agence : pas de base partagée, d’e-mail automatique, de rappel serveur ou de synchronisation multi-appareils. Une seule session de modification est recommandée.
