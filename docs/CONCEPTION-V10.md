# France Marbre 84 — Architecture locale multi-agences (V10)

## Installation

Le fichier `index.html` reste autonome. Il ne demande aucun serveur, API, compte Supabase ou synchronisation permanente. IndexedDB `fmt-commercial`, magasin `state`, conserve la base métier sous la clé `main`, la configuration du poste sous `installation`, puis un instantané complet par agence sous `agency-AG01` à `agency-AG04` en mode Direction.

Au premier lancement, choisir **AG01**, **AG02**, **AG03**, **AG04**, ou **Direction**. Chaque poste reçoit un `installationId` stable. La configuration conserve le mode, le nom facultatif du poste, les noms modifiables des agences, la dernière génération de sauvegarde, les postes de référence et un historique léger des imports. Les noms n'altèrent jamais `agencyId`. Le mode Direction est une configuration d'interface, pas une authentification résistante à la modification du HTML local.

Une ancienne base sans `agencyId` reste intacte tant qu'un opérateur n'a pas choisi son agence. Ce choix rattache explicitement tous les enregistrements existants. Une agence ayant des données est verrouillée dans le formulaire normal. **Changer exceptionnellement d'agence** demande une saisie exacte et une confirmation ; il requalifie la base locale et impose une nouvelle sauvegarde. Sauvegarder la base avant cette opération.

Le modèle commercial conserve `schemaVersion: 7` ; `settings.agencySchemaVersion: 1` identifie l'extension. Chaque collection commerciale porte `agencyId`, notamment clients, catalogue, intérêts, dossiers, lignes, devis, ventes, factures, paiements, relances, interactions et événements. Les lignes figées de devis, ventes confirmées et factures archivées sont également marquées. Les identifiants techniques d'origine et les montants historiques ne changent pas sur le poste de l'agence.

## Sauvegarde chiffrée

Dans **Paramètres → Données & administration → Sauvegarde quotidienne**, saisir une phrase secrète d'au moins 12 caractères et choisir **Créer la sauvegarde du jour**. Le téléchargement produit `FM84_AG01_YYYY-MM-DD_HHMMSS.backup.json`. Déposer ensuite le fichier dans le dossier cloud de l'agence. Le CRM enregistre l'heure de génération du fichier, sans prétendre vérifier le dépôt cloud ni fonctionner quand le navigateur est fermé. Les anciennes sauvegardes cloud ne sont jamais supprimées.

Le fichier externe est un JSON avec `format: "fmt-agency-backup"`, `formatVersion: 1`, `agencyId`, `installationId`, `backupId`, `createdAt`, `kdf`, `iterations`, `cipher`, `salt`, `iv` et `ciphertext`. Ces champs techniques publics servent à l'identifier et au déchiffrement ; ils sont authentifiés comme données associées AES-GCM. Le reste est chiffré : noms d'agence, clients, coordonnées, montants, manifestes et toutes les collections. Web Crypto utilise PBKDF2-SHA-256 (600 000 itérations, sel aléatoire de 16 octets) pour dériver une clé AES-GCM 256 bits ; chaque export emploie un IV aléatoire de 12 octets. Une phrase erronée ou un fichier modifié provoque un rejet. L'absence de Web Crypto bloque l'export avec un message explicite. La phrase secrète ne se trouve pas dans IndexedDB, le HTML, le fichier ni le journal des imports.

Le contenu déchiffré comporte `{manifest, data}`. Le manifeste indique `crmSchemaVersion`, `agencyId`, `agencyName`, `installationId`, `backupId`, `createdAt`, `complete: true`, la liste exhaustive `collections` et le nombre d'éléments par collection. `data` est l'instantané complet et cohérent du CRM, avec les paramètres, le catalogue et toutes les collections métier. L'import compare le manifeste public au manifeste chiffré, valide les nombres, l'agence de chaque enregistrement, les identifiants, les relations, les documents figés et les totaux.

**Conserver la phrase secrète de chaque agence dans un coffre indépendant des sauvegardes**, puis la communiquer au gérant par un canal approprié. Sa perte rend les sauvegardes chiffrées illisibles. Une personne connaissant la phrase secrète et possédant le fichier peut lire les données. Une phrase plus longue et non réutilisée est préférable.

## Restauration d'agence

Dans **Restauration locale**, choisir un fichier `.backup.json`, saisir sa phrase secrète et confirmer le remplacement. Seule une sauvegarde de la même agence est acceptée. Une restauration depuis un autre poste de la même agence exige une confirmation supplémentaire ; elle ne fusionne pas les activités des deux postes. Les anciens JSON locaux non chiffrés restent acceptés après validation et choix explicite de rattachement s'ils sont dépourvus d'identifiant d'agence. Aucun JSON non chiffré n'est proposé pour un nouveau dépôt cloud.

## Consolidation Direction

Dans **Paramètres → Données & administration → Consolidation des agences**, choisir un ou plusieurs fichiers. Pour chaque sauvegarde : saisir la phrase secrète, lire le résumé (agence, date, poste, nombres), puis confirmer. La première sauvegarde approuvée désigne le poste de référence de l'agence. Les suivantes doivent venir de ce poste. Le bouton **Changer le poste AGxx** demande un nouvel identifiant de poste, une saisie exacte et une confirmation ; l'import suivant de ce poste remplace l'ancien instantané. Les sauvegardes plus anciennes exigent la saisie `RESTAURER ANCIENNE`. Un même `backupId` réimporté est ignoré.

L'import est une transaction IndexedDB qui remplace `agency-AGxx` et met à jour l'historique ensemble. Une validation ou une écriture échouée laisse le dernier instantané valide disponible. L'historique conserve seulement les métadonnées des cent dernières opérations, sans empiler d'anciennes copies complètes. Les suppressions réelles dans l'instantané récent se reflètent donc en Direction. Deux postes d'une même agence utilisant chacun leur propre base ne peuvent **pas** être fusionnés par cette procédure.

Le sélecteur dans la navigation choisit une agence ou toutes les agences. En vue globale, les identifiants de consultation sont préfixés par `agencyId` et les relations sont adaptées en mémoire ; les instantanés originaux ne changent pas. Les numéros commerciaux visibles peuvent ainsi se répéter. Les produits du catalogue commun sont dédupliqués selon leur identifiant et leur contenu ; une variante locale reste distincte. Les vues Direction consultent uniquement l'état reconstruit. Les actions métier sont désactivées et le garde d'écriture central refuse toute modification ; aucune relance automatique n'est générée. Le HTML local n'est toutefois pas un système de contrôle d'accès contre quelqu'un qui modifie son code.

Les KPI affichent la date de chaque instantané et ne prétendent pas être en temps réel. La comparaison par agence indique ventes confirmées, encaissements, reste à encaisser, dossiers ouverts et relances en retard. Les indicateurs consolidés appliquent la période choisie aux flux datés ; dossiers ouverts, reste à payer et retard sont calculés sur les derniers instantanés. Les clients, dossiers, devis, factures, filtres et recherche globale suivent le sélecteur d'agence.

Les exports CSV et JSON partiels identifient l'agence des données. Les CSV conservent les colonnes métier et ajoutent `agencyId` et `agencyName`, avec le séparateur `;`, le BOM UTF-8 et une protection contre les formules de tableur. Les imports partiels rejettent un identifiant d'agence étranger. Un CSV n'est pas une sauvegarde complète.
