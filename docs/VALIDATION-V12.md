# Validation V12

Commande : `python tools/smoke_test.py` (Chromium et Playwright requis). Le serveur HTTP de la recette ne sert que le fichier statique ; le CRM et sa sauvegarde fonctionnent hors ligne.

Scénarios vérifiés par `iteration12_test.py` : première configuration avec nom, coordonnées, conditions et logo PNG prévisualisé ; absence des champs de poste ; identité et logo dans la navigation et les Paramètres ; identifiant d'agence stable au renommage ; nom commercial synchronisé puis personnalisable ; instantané d'un devis émis conservé ; création client avec téléphone textuel et placeholder ; filtres des en-têtes Clients, Catalogue, Dossiers et Facturation, curseur de prix, effacement limité à la vue et Kanban ; absence des grands panneaux ; sauvegarde chiffrée nouvelle sans identifiant de poste, lisibilité d'une ancienne sauvegarde chiffrée avec `installationId`, restauration ; exports clients, catalogue et commercial sans poste ; persistance au rechargement ; migration d'une base `AG01` avec 40 clients et ancienne fiche de poste.

Contrôles complémentaires : `node --check` du script intégré, compilation Python de la recette, `git diff --check`, comparaison du catalogue intégré avec la version précédente. La recette V11 reste archivée ; elle documente le comportement antérieur des panneaux et des champs de poste.

Le formulaire initial a également été ouvert à 1 280, 800 et 390 px de large dans Chromium ; aucun débordement horizontal n'a été constaté.
