# FMT — CRM autonome, version 2

**Un seul fichier est nécessaire : `index.html`.** Copier ce fichier sur l’ordinateur et l’ouvrir dans un navigateur moderne autorisant JavaScript et IndexedDB. Aucun serveur, installation, compilation, autre fichier ni connexion Internet n’est requis par l’application.

Le HTML contient les styles, le JavaScript, les icônes et les 3 283 produits initiaux. Les fichiers de documentation et les outils du dépôt servent uniquement au développement et ne sont pas nécessaires pour utiliser le CRM.

## Nouveautés

- **Analyses & KPI** est l’accueil unique. L’ancienne page Tableau de bord est supprimée.
- **Paramètres → Données de démonstration** génère 40 clients fictifs, avec produits d’intérêt, pipeline, devis, ventes sur six mois, relances et interactions. Génération et suppression demandent confirmation. La démo est remplaçable ; les données réelles et les éléments fictifs modifiés ou liés à des données réelles sont protégés.
- **Clients** : actions Modifier visibles, société conditionnelle, suppression du commercial client, rue/code postal/ville séparés, recherche et filtres d’adresse. Numéros stables `CLI-000001`, distincts des identifiants techniques préservés.
- **Catalogue** : action Modifier explicite, édition de toutes les caractéristiques, prix, référence et activation. Export JSON dédié et import par identifiant stable, sans suppression des produits absents du fichier.
- **Migration version 1 → 2** automatique à l’ouverture et lors de la restauration d’une ancienne sauvegarde. L’adresse d’origine reste dans « Ancienne adresse conservée » si elle ne peut pas être décomposée sûrement. Les associations commerciales et les identifiants techniques ne changent pas.

## Conservation des données

Les modifications sont conservées dans IndexedDB sur le navigateur et l’appareil utilisés, et ne réécrivent pas le fichier HTML. Faire régulièrement **Paramètres → Exporter JSON**. L’export catalogue seul contient les produits, pas l’activité commerciale. Les exports sont facultatifs pour fonctionner et nécessaires pour transférer vos données vers un autre navigateur ou ordinateur.

Conserver le même navigateur et le même emplacement du HTML. Les navigateurs peuvent isoler différemment le stockage des fichiers locaux ; exporter avant un déplacement ou un changement d’appareil. Une seule session de modification à la fois est recommandée. La nouvelle version conserve le nom IndexedDB de la première version pour retrouver et migrer sa base sur la même origine.

## Validation

Voir [les résultats et limites de recette](docs/VALIDATION.md). Le code ne dépend pas d’un serveur ; un serveur HTTP local temporaire a uniquement servi à tester le navigateur cloud, dont la politique bloque `file://`. L’ouverture directe reste à recetter sur le navigateur cible.

L’analyse des Excel et la conception initiale sont conservées dans [CONCEPTION.md](docs/CONCEPTION.md) comme documentation historique. Les filtres analytiques avancés et les autres limites de la première version non traitées par cette mise à jour restent inchangés.
