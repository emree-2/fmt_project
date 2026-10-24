# FMT — CRM autonome, version 4

**Un seul fichier est nécessaire : `index.html`.** Copier ce fichier sur l’ordinateur et l’ouvrir dans un navigateur moderne autorisant JavaScript et IndexedDB. Aucun serveur, installation, compilation, autre fichier ni connexion Internet n’est requis par l’application.

Le HTML contient les styles, le JavaScript, les icônes et les 3 283 produits initiaux. Les fichiers de documentation et les outils du dépôt servent uniquement au développement et ne sont pas nécessaires pour utiliser le CRM.

## Nouveautés de la quatrième version

- **Produits** : création et dernière modification tracées, sans inventer les dates des produits historiques. Une sauvegarde sans changement n’actualise pas la date. Référence numérique suivante proposée sur tout le catalogue, produits inactifs inclus, avec contrôle de conflit lors de l’enregistrement. Liens web simplifiés, avec ajout de `https://` pour une saisie commençant par `www.`.
- **Clients** : menu Gestion des clients, exports JSON/CSV de tous les clients ou des résultats filtrés, import JSON/CSV avec aperçu, validation et confirmation. Mise à jour par identifiant technique ou numéro client stable. Aucun rapprochement automatique par nom ou e-mail, aucune suppression des clients absents du fichier. Les conflits d’identifiants bloquent l’import ; les doublons de coordonnées sont signalés.
- **SIRET** : texte de 14 chiffres, facultatif pour un professionnel. Société et SIRET sont toujours visibles, mais grisés, désactivés et vidés pour un particulier. Nouveau champ repris dans les imports, exports et sauvegardes.
- **Tri** : clic sur les en-têtes (croissant, décroissant, puis défaut), tri naturel des références, numérique des montants et chronologique des dates, appliqué avant pagination. Indicateur et navigation clavier ; l’ordre des données enregistrées n’est jamais modifié pour un tri d’affichage.
- **Prix** : deux curseurs et champs numériques synchronisés, bornes issues des prix réels, croisement des bornes empêché. Les prix absents sont inclus sans filtre et exclus lorsqu’une borne est définie. « Désignation contient » devient « Nom du produit ».
- **Recherche universelle** : résultats locaux par catégorie (clients, produits, opportunités, devis, ventes), compteurs, affichage progressif, flèches/Entrée/Échap et accès direct aux fiches.
- **Navigation et analyses** : catalogue et paramètres ancrés en bas du menu sur ordinateur ; tableau Performance par commercial supprimé. Les autres KPI sont conservés.
- **Logo** : import du fichier officiel PNG/JPEG/WebP dans Paramètres, stockage local et export optionnel d’un nouveau `index.html` qui embarque l’image. L’image collée dans le chat n’a pas été transmise comme fichier téléchargeable aux outils ; le HTML initial conserve donc la marque textuelle. Aucune approximation du logo officiel n’a été dessinée.

Le schéma de contenu passe à 4. Les versions 1, 2 et 3 restent importables, avec identifiants, relations et historiques conservés. Le catalogue initial de 3 283 lignes reste inchangé dans le HTML. Les fonctionnalités de démonstration, de filtres avancés, de devis/factures, de TVA et de restauration sont préservées.

## Conservation des données

Les modifications sont conservées dans IndexedDB sur le navigateur et l’appareil utilisés, et ne réécrivent pas le fichier HTML. Faire régulièrement **Paramètres → Exporter JSON**. L’export catalogue seul contient les produits, pas l’activité commerciale. Les exports sont facultatifs pour fonctionner et nécessaires pour transférer vos données vers un autre navigateur ou ordinateur.

Conserver le même navigateur et le même emplacement du HTML. Les navigateurs peuvent isoler différemment le stockage des fichiers locaux ; exporter avant un déplacement ou un changement d’appareil. Une seule session de modification à la fois est recommandée. La nouvelle version conserve le nom IndexedDB de la première version pour retrouver et migrer sa base sur la même origine.

## Validation

Voir [les résultats de la version 4](docs/VALIDATION-V4.md) et [la recette historique](docs/VALIDATION.md). Le code ne dépend pas d’un serveur ; un serveur HTTP local temporaire a uniquement servi à tester le navigateur cloud, dont la politique bloque `file://`. L’ouverture directe reste à recetter sur le navigateur cible.

L’analyse des Excel et la conception initiale sont conservées dans [CONCEPTION.md](docs/CONCEPTION.md) comme documentation historique. Les filtres analytiques avancés et les autres limites de la première version non traitées par cette mise à jour restent inchangés.

## Format des imports clients

JSON recommandé : un export « clients » (`format: "fmt-clients"`, `version: 1`, tableau `clients`). Un tableau JSON de fiches ou une sauvegarde complète compatible est également accepté pour en extraire les clients.

CSV : séparateur `;` ou `,`, UTF-8, champs entre guillemets pour les retours à la ligne et séparateurs. Les en-têtes d’un export clients sont reconnus : `id`, `number`, `lastName`, `firstName`, `type`, `company`, `siret`, `phone`, `email`, `street`, `postalCode`, `city`, `legacyAddress`, `origin`, `notes`, `createdAt`, `updatedAt`. Des alias français courants sont acceptés. Utiliser le format ISO pour les dates importées ; conserver téléphones, codes postaux et SIRET en colonnes texte dans Excel pour ne pas perdre les zéros avant l’export.

Pour mettre à jour, fournir `id` ou `number`. Si les deux sont présents, ils doivent désigner la même fiche. Une colonne absente conserve la valeur existante ; une valeur explicitement vide la vide. La date de création existante reste immuable. Les nouvelles fiches importées sans dates d’origine gardent ces dates non renseignées. Les données de démonstration réimportées comme clients seuls sont traitées prudemment comme des données importées, sans suppression automatique.

L’export HTML avec logo contient le programme et le catalogue initial ; il ne remplace pas l’export JSON pour transférer l’activité ou le catalogue modifié. L’image importée est embarquée à l’identique, sans dépendance à un fichier externe.
