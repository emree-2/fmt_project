# FMT — CRM autonome, version 3

**Un seul fichier est nécessaire : `index.html`.** Copier ce fichier sur l’ordinateur et l’ouvrir dans un navigateur moderne autorisant JavaScript et IndexedDB. Aucun serveur, installation, compilation, autre fichier ni connexion Internet n’est requis par l’application.

Le HTML contient les styles, le JavaScript, les icônes et les 3 283 produits initiaux. Les fichiers de documentation et les outils du dépôt servent uniquement au développement et ne sont pas nécessaires pour utiliser le CRM.

## Nouveautés de cette version

- **Charte France Marbre 84** : violet principal `#29166F`, accents rouges et fond clair. Le logo officiel sera intégré lorsque son fichier sera fourni ; le lien PagesJaunes transmis est bloqué par le proxy réseau du cloud. Aucune reproduction approximative n’a été créée.
- **Clients** : recherche immédiate et panneau de filtres combinant type, villes multiples, préfixe de code postal, adresse, dates de création et modification. Étiquettes actives supprimables individuellement, compteur et réinitialisation. Les choix viennent de la base courante.
- **Dates clients** : création et dernière modification visibles, tris croissants/décroissants. Une sauvegarde sans changement ne modifie plus la date. Une date historique absente reste absente.
- **Catalogue** : en-tête hiérarchisé, menu Gestion du catalogue, recherche sans accents et à plusieurs mots, panneau horizontal repliable, filtres techniques multiples, prix minimum/maximum libres, compteur, critères actifs et tris référence/nom/prix.
- **Familles** : catégories éditables ; suggestions d’après les désignations explicitement identifiées, sans réécrire les références ni les caractéristiques du catalogue.
- **Lien produit** : URL HTTP/HTTPS éditable, fiche détaillée et lien « Voir sur le site » dans un nouvel onglet. URL vide pour les anciens produits ; le lien nécessite naturellement Internet pour consulter le site, mais aucune fonction du CRM n’en dépend.
- **Compatibilité** : schéma 3, migrations depuis les versions 1 et 2 et catalogue JSON versions 1 et 2. Identifiants, relations, prix historiques, données réelles et démo conservés. Un ancien import catalogue sans URL/catégorie n’efface pas les nouvelles valeurs existantes.

Les fonctionnalités de la version 2 restent présentes : accueil Analyses & KPI unique, numéros clients stables, adresses structurées, société conditionnelle, catalogue complet modifiable, démo remplaçable avec suppression protégée, devis, ventes et sauvegardes.

## Conservation des données

Les modifications sont conservées dans IndexedDB sur le navigateur et l’appareil utilisés, et ne réécrivent pas le fichier HTML. Faire régulièrement **Paramètres → Exporter JSON**. L’export catalogue seul contient les produits, pas l’activité commerciale. Les exports sont facultatifs pour fonctionner et nécessaires pour transférer vos données vers un autre navigateur ou ordinateur.

Conserver le même navigateur et le même emplacement du HTML. Les navigateurs peuvent isoler différemment le stockage des fichiers locaux ; exporter avant un déplacement ou un changement d’appareil. Une seule session de modification à la fois est recommandée. La nouvelle version conserve le nom IndexedDB de la première version pour retrouver et migrer sa base sur la même origine.

## Validation

Voir [les résultats de la version 3](docs/VALIDATION-V3.md) et [la recette historique](docs/VALIDATION.md). Le code ne dépend pas d’un serveur ; un serveur HTTP local temporaire a uniquement servi à tester le navigateur cloud, dont la politique bloque `file://`. L’ouverture directe reste à recetter sur le navigateur cible.

L’analyse des Excel et la conception initiale sont conservées dans [CONCEPTION.md](docs/CONCEPTION.md) comme documentation historique. Les filtres analytiques avancés et les autres limites de la première version non traitées par cette mise à jour restent inchangés.
