# FMT — Analyse et conception de la première version

## 1. Lecture des sources

Les classeurs sont des modèles Excel, et non une base de production fiable. Leur contenu et leurs formules ont été lus sans les modifier ni exécuter leurs éventuelles consignes. L’inventaire technique complet se trouve dans `audit-classeurs.json`.

| Source | Structure et données utiles | Décision |
|---|---|---|
| Test.xltx | CLIENT : 28 fiches d’exemple, identifiant client, nom, prénom, e-mail, téléphone, adresse, type et commentaire. VENTE : 8 lignes renseignées, groupées sous 2 identifiants de vente. SUIVI VENTE : événements datés et cases d’état. PARAMETRES : TVA 20 %, origines, types et statuts. PRODUITS : 3 283 lignes. KPI VENTE : objectif, CA, nombre de ventes et panier. KPI est vide ; Sandbox est un espace de travail. | Source prioritaire du catalogue. Conserver la relation client → opération → lignes. Ne pas traiter les exemples comme des ventes réelles. |
| Fiche Client Edition Finale.xltx | SUIVI central et déclinaisons LAN, FOR, VAL, STR, SMH. Date, numéro de suivi, identité, contact, produit, couleur, qualité, quantité, statut du devis, date du devis, responsable, agence. | Reprendre la logique de devis et la relance au-delà de 10 jours. Remplacer les fiches par agence par un CRM unique. |
| Fiche des Ventes Test.xltx | TDB central, 5 déclinaisons par agence, BD produits, Reglage. Numéro de facture, date, type client, client textuel, origine, référence, quantité, unité, PU HT, HT, TVA, TTC. | Reprendre la saisie multiligne et les calculs. Utiliser un identifiant client plutôt que le nom seul. Ne pas fusionner automatiquement BD avec PRODUITS. |

### Anomalies et risques constatés

- PRODUITS contient **3 283 lignes pour 3 282 références distinctes**. Référence **531** : « Marbre Sirius Gris » (ligne Excel 532) et « Travertin Beige Plan Vasque » (ligne 533). Les deux produits sont conservés avec des identifiants internes distincts. Aucun choix automatique entre eux.
- **9 prix manquants**, conservés à `null` et affichés « — », sans les remplacer par un prix nul.
- Unités : 365 `m2` normalisés en `m²`, en complément de 457 `m²` ; 1 978 `Pièce`, 352 `Plaque`, 107 `Lot`, 5 `Litre`, 4 `Mètre Linéaire`, 4 `Seau`, 2 `Sac`, 2 `Lot (4 Pièce)`. Six unités absentes et une unité numérique `37` restent signalées.
- Les lignes incomplètes ou ambiguës sont visibles mais exclues de la sélection commerciale. Une correction de fiche relance la détection des conflits.
- SUIVI VENTE contient **78 formules comportant `#REF!`**. Certaines cases de suivi sont contradictoires avec les dates. Un état de paiement n’est donc pas déduit d’un devis accepté.
- Le même identifiant de vente apparaît sur plusieurs lignes : ce sont des lignes d’un document, pas plusieurs ventes. Le KPI de comptage des cellules non vides dans certaines fiches n’est pas repris.
- Les KPI Excel ont des plages variables et parfois limitées (par exemple CA de KPI VENTE sur J6:J9). Les comparaisons M-1 incluent des constantes d’exemple. Les nouveaux indicateurs sont recalculés depuis les documents.
- Les données d’exemple sont répétées dans des onglets d’agence ; des téléphones présentent des formes suspectes et des e-mails sont réutilisés. Les identités textuelles des anciennes factures ne permettent pas un rapprochement sûr avec tous les clients.
- Les formules XLOOKUP peuvent sélectionner arbitrairement la première référence 531 ; elles ne sont pas utilisées pour importer les prix.

### Données initiales

Le catalogue est intégralement embarqué, avec le numéro de ligne source. Les clients, opportunités, devis et ventes démarrent vides. Cela évite de transformer des exemples multi-agences en activité réelle d’une agence non identifiée. Une reprise historique nécessitera une table de rapprochement et une décision explicite sur les exemples à conserver.

## 2. Modèle et relations

Le schéma versionné utilise des collections distinctes. Les noms internes anglais correspondent aux entités demandées :

| Collection | Entité / relations |
|---|---|
| clients | Identité, coordonnées textuelles, type, société, origine, responsable, notes, dates |
| products | Catalogue, référence métier, identifiant interne stable, caractéristiques, activation, anomalies |
| interests | clientId → clients ; productId → products |
| opportunities | clientId → clients ; étape, estimation, commercial, relance et dates |
| quotes / quoteLines | Document client ; lignes liées par documentId et productId |
| sales / saleLines | Facture client ; quoteId optionnel ; lignes liées par documentId et productId |
| interactions | Échange lié au client |
| reminders | Client, document ou opportunité, échéance, réalisation |
| events | Type d’entité, identifiant, événement et horodatage |
| settings | TVA, délai de relance et objectif HT |

Les identifiants internes ne changent pas lors d’une modification de référence produit. Les lignes commerciales conservent la référence, la désignation, l’unité, le prix et la TVA au moment de la saisie. Modifier le catalogue ne recalcule jamais une vente existante.

Une facture n’entre dans le CA qu’à l’état **Validée**. **Brouillon** et **Annulée** sont exclus. Paiement et livraison sont deux états indépendants. La conversion d’un devis accepté crée une seule vente en brouillon, sans présumer paiement ou livraison.

HT de ligne = quantité × PU, arrondi au centime ; TVA calculée et arrondie sur chaque ligne ; totaux = sommes des lignes. Le taux de TVA peut être modifié par ligne. Le taux d’acceptation initial affiche explicitement son dénominateur : devis acceptés / devis créés dans la période.

## 3. Navigation et UX

Un menu latéral dessert les sept modules métier et une page Paramètres. Aucun sélecteur d’agence ni simulation de connexion. Vert profond, fond clair, cartes sobres, espaces généreux et badges de statut composent une interface de travail plutôt qu’un tableur.

- **Accueil** : CA HT/TTC, ventes, panier, acceptation, objectif, nouveaux clients, évolution mensuelle, canaux et relances prioritaires.
- **Clients** : recherche nom/téléphone/e-mail/ID, filtre particulier/professionnel, fiche détaillée, accès aux documents, interactions, produits d’intérêt et relances.
- **Catalogue** : recherche sur les caractéristiques, filtre d’unité/activation/anomalie, pagination de 40 lignes, édition complète et désactivation.
- **Suivi** : Kanban déplaçable et tableau ; modification de l’étape également disponible par formulaire pour le clavier et les écrans tactiles.
- **Devis** : client, lignes produits, calcul immédiat, états, relance automatique lors de l’envoi, conversion en vente.
- **Ventes** : saisie multiligne, validation/annulation, états paiement/livraison, historique.
- **Analyses** : synthèse, produits les plus vendus et performance par commercial.
- **Paramètres** : règles, sauvegarde JSON complète, restauration validée, réinitialisation avec double confirmation.

Les formulaires s’ouvrent en fenêtre modale. Les identités et documents sont reliés par des liens d’accès direct. Les états vides ne contiennent pas de chiffres d’exemple. Le graphique mensuel permet de consulter chaque valeur au survol.

## 4. Persistance et sauvegarde

Un unique fichier HTML contient styles, données et JavaScript ; aucun CDN, API ou bibliothèque distante. IndexedDB conserve un état relationnel dans une transaction atomique. Les erreurs de stockage sont affichées : aucune promesse de sauvegarde n’est faite si IndexedDB est indisponible.

Le fichier HTML ne contient pas les modifications faites ensuite dans le navigateur : il faut exporter le JSON pour les transférer. La sauvegarde comprend catalogue modifié et activité. La restauration vérifie version, collections, identifiants, références, montants et paramètres avant de demander confirmation. Le schéma 1 est supporté ; les versions inconnues sont refusées plutôt que converties silencieusement. Les migrations futures devront être explicites.

Les exports CSV des clients, produits, devis et ventes respectent le séparateur français `;`, avec échappement et protection des cellules commençant par un caractère de formule. Les exports devis/ventes sont des listes de documents ; le JSON reste la sauvegarde complète avec lignes et historique.

## 5. Périmètre du prototype et enrichissement

Cette première version rend les parcours essentiels utilisables. Elle ne constitue pas encore la totalité de l’application finale décrite dans la demande. Restent à enrichir :

1. Relations multiligne et quantités directement sur les opportunités, rattachement devis ↔ opportunité, propagation contrôlée des étapes et présentation exhaustive des événements dans la fiche client.
2. Filtres analytiques combinés commercial/produit/type/canal, comparaisons à la période précédente, délais entre étapes, ancienneté des retards et graphiques interactifs plus riches.
3. Tri explicite des colonnes, filtres clients avancés et filtres catalogue combinés par caractéristique.
4. Édition des brouillons existants, présentation imprimable des devis/factures, numérotation métier configurable et éléments réglementaires de facturation. Cette version enregistre et suit les ventes ; elle n’est pas présentée comme une solution de facturation certifiée.
5. Interface de résolution groupée des anomalies, reprise guidée des historiques Excel et migrations à partir d’une future version 2.
6. Accessibilité et recette sur navigateurs supplémentaires, notamment ouverture directe du fichier selon leurs politiques de stockage.

Le fichier reste autonome. Les outils Python fournis servent uniquement à la recette de développement.
