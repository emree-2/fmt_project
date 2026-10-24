# Recette de la quatrième version

## Tests exécutés

Trois suites Playwright (`smoke_test.py`, `filters_test.py`, `iteration4_test.py`) dans des contextes Chromium isolés, sans données utilisateur. Ces outils sont facultatifs et ne sont jamais requis à l’exécution du HTML.

- **Dates des produits** : création UI horodatée, modification réelle actualisant seulement `updatedAt`, sauvegarde sans changement conservant la date, ancien catalogue affiché « Import historique / création non renseignée ». Import d’un produit existant préservant sa création même si une autre date est fournie.
- **Clients JSON/CSV** : aperçu ajout/mise à jour avant écriture, confirmation, annulation sans mutation, absence de suppression des fiches hors fichier, conflits et doublons d’identifiants bloqués, collision entre numéro proposé et identifiant résolu détectée. Téléphones, codes postaux et SIRET sont du texte. CSV avec séparateur, champs multilignes et guillemets vérifié. Identifiants, date de création, devis, ventes et opportunités restent associés après import.
- **SIRET** : validation 14 chiffres, zéros initiaux, saisie avec espaces normalisée, affichage professionnel et export JSON/CSV. Société et SIRET visibles, désactivés et vidés lors du passage à Particulier.
- **Tris** : références naturelles, prix et montants numériques (66 avant 1 000), dates chronologiques, en-têtes des clients/produits/devis/ventes/pipeline/classement KPI et lignes des documents. Tri global avant pagination, indicateur actif, maintien du tri en changeant de page, conservation physique de l’ordre enregistré. En-têtes utilisables au clavier, focus conservé après tri ; colonne Actions non triable. L’ordre des statuts est documenté dans le titre de l’en-tête.
- **Slider prix** : deux bornes synchronisées avec les champs numériques, clavier, bornes réelles, croisement empêché, critère conservé après ajout d’un autre filtre. Les prix inconnus sont exclus uniquement lorsqu’un filtre de prix est actif.
- **Référence proposée** : calcul maximum numérique + 1 incluant les produits inactifs, références alphanumériques ignorées, champ modifiable, doublons rejetés. L’identifiant technique reste distinct et stable.
- **Liens produits** : libellé simplifié, préfixe `https://` ajouté à `www.`, protocoles non HTTP/HTTPS refusés. Prix et désignations historiques toujours conservés.
- **Recherche universelle** : cinq catégories, recherche partielle sans accents, compteurs, affichage progressif, flèches/Entrée/Échap, fermeture à l’extérieur, ouverture directe du client, du produit, de l’opportunité ou du document demandé.
- **Navigation et KPI** : cinq modules opérationnels en haut, deux modules de gestion en bas du menu sur ordinateur ; tableau Performance par commercial absent. Les autres calculs et tableaux sont préservés.
- **Régression** : devis multiligne 66 € HT / 79,20 € TTC, relance et conversion unique, factures en brouillon exclues du CA, catalogue complet, démo remplaçable/supprimable avec protection des données réelles, filtres clients/catalogue, restauration et persistance après rechargement.
- **Migration** : schémas 1, 2 et 3 vers 4, champs SIRET et dates produits ajoutés sans réinitialisation et sans dates historiques inventées.
- **Autonomie et image locale** : opérations exercées avec le réseau coupé après chargement. Import d’une image synthétique de recette, export du HTML l’embarquant puis ouverture de ce HTML dans un contexte vierge sans autre fichier : image correctement chargée, catalogue présent, absence d’activité utilisateur embarquée involontairement. Le fixture n’est pas présenté comme le logo officiel et n’est pas incorporé au livrable.
- **Présentation** : captures ordinateur et tablette examinées, syntaxe JavaScript et `git diff --check` contrôlés. Aucun fichier CSS/JS/image externe requis. Catalogue source embarqué identique au commit précédent.

## Limites et état du logo

Le logo officiel est visible dans le message, mais le fichier binaire n’a pas été rendu accessible aux outils comme pièce jointe téléchargeable. Le lien PagesJaunes transmis lors de l’itération précédente était bloqué par le proxy HTTP 403 ; aucune tentative de contournement ni redessin n’a été effectuée. Le HTML livré conserve donc la dénomination textuelle et propose Paramètres → Logo France Marbre 84 pour importer l’original localement et exporter un HTML autonome qui l’embarque. Une archive ZIP contenant l’original permettrait également son intégration exacte par l’agent.

La politique du Chromium géré continue de bloquer `file://` (`ERR_BLOCKED_BY_ADMINISTRATOR`). La recette utilise une origine HTTP statique locale temporaire, sans aucune API serveur. La vérification de l’ouverture directe et du stockage associé reste à effectuer dans le navigateur cible. Le code de l’application ne nécessite ni serveur, ni installation, ni réseau. Les liens « Voir sur le site » nécessitent naturellement le réseau pour ouvrir le site distant.

Les téléchargements physiques sont soumis au navigateur ; les contenus JSON/CSV/HTML ont été contrôlés et les imports par sélecteur de fichier effectivement exercés. Une seule session de modification est recommandée ; pas de synchronisation entre appareils ni de recette exhaustive sur tous les navigateurs tactiles.
