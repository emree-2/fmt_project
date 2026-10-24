# Recette — troisième itération France Marbre 84

## Résultats

Deux suites Playwright exécutées dans un contexte Chromium temporaire : `tools/smoke_test.py` pour les parcours existants et `tools/filters_test.py` pour les nouveautés. Aucun de ces outils n’est requis pour utiliser le fichier HTML livré.

- Clients : recherche sans accents, combinaison professionnel + Avignon + code postal commençant par 84, sélection de plusieurs villes, recherche dans l’adresse, périodes de création et modification, tris des deux dates et du nom. Compteur, réinitialisation et suppression individuelle des critères exercés.
- Modification : enregistrement sans changement préservant la date ; véritable modification actualisant la date ; ajout d’une ville immédiatement disponible dans le filtre dynamique.
- Catalogue : recherche `TRAVERTIN BEIGE` par mots et `mosaique` sans accent, filtres combinés couleur/épaisseur/format/prix 20–40 €, tri décroissant, message lorsque le prix minimum dépasse le maximum, retour aux 3 283 produits après réinitialisation.
- URL produit : valeur initiale vide, refus des protocoles autres que HTTP/HTTPS, sauvegarde et rechargement, fiche produit, lien nouvel onglet avec `noopener noreferrer`. L’ouverture a été testée vers une page interceptée par le banc de test, sans requête réelle vers un serveur externe.
- Imports : sauvegardes complètes, migration v1 et v2 vers v3, champ de modification absent conservé vide, export catalogue enrichi, import d’un ancien catalogue sans URL ne supprimant pas l’URL existante, URL interdite refusée à l’import.
- Non-régression : catalogue source identique au dernier commit (3 283 lignes), clients et numéros stables, devis multiligne et calculs 66 € HT / 79,20 € TTC, conversion unique, validation de facture, prix et désignations historiques, démo générable/remplaçable, suppression protégeant les données réelles et les relations.
- Performance mesurée : 10 000 clients synthétiques, 5 000 résultats exacts pour des critères combinés, filtrage et rendu paginé en environ 76–85 ms sur la machine de recette. Ce temps est indicatif et dépend de l’appareil.
- Sept écrans rendus sans erreur JavaScript, captures ordinateur et tablette examinées. Panneaux repliables, largeur du tableau conservée avec défilement horizontal lorsque nécessaire.
- Contrôle de syntaxe JavaScript et de l’absence de ressources externes requises. Opérations métier des suites effectuées avec le réseau désactivé après le chargement initial.

## Points explicitement non validés ou différés

- **Logo officiel différé par l’utilisateur** : le téléchargement PagesJaunes retourne HTTP 403 depuis le proxy cloud, y compris lors de la tentative avec accès étendu. L’utilisateur a indiqué qu’il transmettrait le fichier ultérieurement. La marque textuelle et la palette sont présentes ; aucune image approximative n’est substituée au logo officiel.
- **Ouverture directe file://** : toujours bloquée par la politique du Chromium géré (`ERR_BLOCKED_BY_ADMINISTRATOR`). Les recettes fonctionnelles ont utilisé un serveur statique local temporaire ; le code applicatif ne contient aucune API serveur et ne requiert que `index.html`. Vérifier le stockage local dans le navigateur cible et exporter avant de déplacer le fichier.
- Les téléchargements physiques de fichiers restent soumis au navigateur ; les contenus JSON/CSV ont été contrôlés et les restaurations par sélecteur de fichier effectivement exercées.
- Recette tactile et multi-navigateurs non exhaustive. Pas de synchronisation entre ordinateurs ni de gestion des éditions simultanées dans plusieurs onglets.

## Modèle

Le nom IndexedDB et son magasin `state` sont conservés. Le schéma de contenu passe à 3 : `products.url` et `products.category` sont ajoutés sans toucher aux identifiants ou aux lignes historiques. Les catégories stockées restent prioritaires sur les suggestions ; les URL existantes sont préservées lors d’imports catalogue anciens n’incluant pas ce champ. Aucun horodatage inconnu n’est inventé lors de la migration.
