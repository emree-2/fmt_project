# Version 9 — état de filtrage partagé

## Périmètre et conservation

`index.html` reste l’unique fichier d’exécution, sans ressource distante. L’avatar d’en-tête et ses règles CSS sont retirés ; la recherche utilise l’espace libéré et la marque latérale est conservée.

Le schéma de contenu **7**, le nom/version physique/magasin IndexedDB, les relations et les sauvegardes ne changent pas. Les filtres sont des états de présentation en mémoire : aucune ligne métier, date historique, facture, paiement ou instantané n’est modifié.

## Composant commun

`registerFilterTable` construit les métadonnées d’un tableau : colonnes, source complète, descripteurs typés et fonction d’actualisation. Chaque descripteur contient une clé, sa colonne, un libellé, le type de contrôle, la lecture de la valeur et, si nécessaire, les choix dans l’ordre métier.

- `readCriterion` / `writeCriterion` forment l’unique chemin de lecture/écriture, utilisé par les menus et panneaux.
- Les critères clients/catalogue existants, étapes commerciales, états de paiement, états des devis et types/statuts du journal sont réutilisés par des adaptateurs. Aucune copie indépendante de leur sélection n’est créée.
- `tableFilterState` ne stocke que les critères de consultation supplémentaires. Les prix du catalogue lisent/écrivent directement `minPrice`/`maxPrice`, également utilisés par le slider.
- `applyTableFilters` applique les critères sur tous les résultats de recherche avant tri/pagination. Les valeurs d’une sélection multiple sont alternatives ; les champs différents se combinent par « et ».
- Les menus des en-têtes et les panneaux emploient les mêmes `filterControls`, compteurs et fonctions de réinitialisation.

Le tri conserve le cycle croissant/décroissant/défaut et ses comparateurs existants. Il possède son propre bouton ; le filtre n’appelle jamais le tri. L’icône de filtre devient violette lorsqu’un critère de la colonne est actif.

## Types de critères

Texte complet/partiel avec normalisation des accents ; listes de catégories/statuts à cases multiples ; périodes calendaires inclusives ; plages numériques inclusives. Les coordonnées client sont textuelles, tandis que le début des échanges d’un dossier est une date. Les valeurs datées déjà converties en timestamps pour le tri sont converties en dates calendaires pour le filtrage.

Les grandes listes de choix sont recherchables sur l’ensemble des valeurs. Au plus 100 choix sont rendus à la fois dans le composant commun, sans limiter les enregistrements recherchés ; les sélections restent actives même lorsque leurs valeurs ne sont pas affichées dans cette tranche. Les facettes historiques du catalogue gardent leur recherche locale existante.

La période client reste unique, avec choix création/modification, comme auparavant. Ouvrir/appliquer un filtre d’une colonne datée sélectionne le bon type dans ce même composant. Les dates absentes sont exclues lorsqu’une période est active. Les périodes des autres tableaux correspondent à leurs champs distincts.

Le statut produit conserve les catégories Actif/Inactif/À vérifier : un produit actif peut aussi être à vérifier. Le filtre Unité n’est pas réintroduit, y compris dans l’en-tête du catalogue. L’unité reste présente dans les données et les documents.

## Organisation des pages

Les recherches textuelles principales restent visibles. Les critères structurés sont dans « Filtres », avec Réinitialiser et Fermer à l’intérieur. Les récapitulatifs compacts et indicateurs de colonne restent visibles. Fermer ne change aucun critère ; réinitialiser efface les critères structurés de la liste courante, conserve la recherche textuelle et ne touche pas aux autres listes/modules.

Clients/catalogue gardent leurs contrôles existants dans le même panneau, complétés avec les nouveaux critères de colonnes. Les types clients et statuts catalogue proposent désormais plusieurs valeurs. Dossiers, devis, relances, facturations et journal utilisent le panneau commun généré par les métadonnées.

La recherche globale possède un seul panneau, avec sections par catégorie, et filtre chaque catégorie avant sa pagination indépendante. Les onglets de catégories restent des accès aux groupes de résultats. Les critères de recherche globale restent séparés de ceux des listes principales.

Les analyses disposent d’un seul panneau avec la période des indicateurs et les filtres du tableau détaillé des produits vendus. Filtrer ce tableau ne recalcule pas les indicateurs financiers selon ces lignes filtrées ; la période existante continue seule à régler les KPI. La réinitialisation des analyses sélectionne Toute la période et efface les critères du tableau détaillé.

L’historique des règlements permet également de distinguer les transactions actives des corrections/annulations conservées. Le filtre concerne uniquement les lignes affichées : le calcul encaissé/reste utilise toujours le registre complet.

Les tableaux documentaires et de saisie sont exclus. Les colonnes Actions n’ont pas de filtre. Les documents imprimables restent entièrement conservés.

## Menus et saisie

Les menus sont positionnés dans la fenêtre, hors du conteneur défilant. Dans une fiche native, ils appartiennent au `<dialog>` pour rester au-dessus de son fond et accessibles au clavier. Échap ferme le menu et rend le focus au bouton de colonne ; le clic extérieur le ferme aussi.

Une actualisation déclenchée par un filtre conserve les contrôles du panneau et leur focus/caret. Elle ne détruit pas un menu en cours de sélection, même si la fiche qui contient le tableau est reconstruite. Les critères de date utilisent l’événement de validation du contrôle natif pour éviter une reconstruction pendant l’édition du calendrier.

Les menus sont supprimés de l’export HTML portable et masqués à l’impression. Les bornes et sélections ne sont pas enregistrées dans les données métier ni synchronisées entre appareils.
