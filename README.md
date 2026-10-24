# France Marbre 84 — CRM autonome, version 6

**Seul `index.html` est nécessaire.** Copier ce fichier et l’ouvrir dans un navigateur moderne autorisant JavaScript, IndexedDB et l’impression. Aucun serveur, compilation, installation, API ou bibliothèque distante n’est requis par l’application. Les fichiers de documentation et les outils de recette sont facultatifs.

Le catalogue initial de 3 283 lignes reste intégré au HTML. Les modifications du catalogue et de l’activité sont stockées dans IndexedDB. Faire régulièrement **Paramètres → Exporter JSON** ; déplacer le HTML ne transfère pas automatiquement les données du navigateur.

## Nouveautés de la version 6

- Tableau de produits partagé entre dossiers et devis : recherche par référence/nom dans chaque ligne, sélection stable, quantités/prix/TVA modifiables, totaux immédiats, suppression et défilement sur petit écran.
- **Paramètres → Relances automatiques** : activation et délai d’inactivité indépendants du délai après envoi de devis. Contrôles locaux à l’ouverture, pendant l’utilisation et après les opérations ; aucune exécution lorsque le CRM est fermé.
- **Relances & échanges** : journal commun filtrable, actions prévues/en retard en premier, dates prévue/réalisée distinctes, compte rendu lié à la relance, échanges rapides datés avec canal facultatif. Une réalisation ne crée plus une seconde ligne commerciale.
- Historiques techniques masqués sans traçabilité ; avec traçabilité, ils restent repliés par défaut.
- Filtres multisélection des étapes commerciales et états de paiement ; les étapes restent sélectionnées lors du changement tableau/Kanban.
- Filtre Unité retiré du catalogue ; toutes les données et fonctions liées aux unités sont conservées.

Les relances automatiques sont **désactivées initialement**. Leur désactivation ne supprime pas les alertes déjà enregistrées. Un dossier sans date d’activité connue ou historique à vérifier ne déclenche aucune relance d’inactivité.

## Nouveau parcours

1. Créer ou ouvrir un client.
2. Créer un **dossier commercial** pour son projet. Un client peut avoir plusieurs dossiers.
3. Ajouter les produits, quantités, prix proposés et TVA dans ce dossier. Il est possible de commencer sans produit.
4. Choisir **Générer un devis**, vérifier la proposition, ses conditions et sa validité, puis l’enregistrer en brouillon.
5. Compléter l’émetteur et les coordonnées client si nécessaire, puis **Émettre et marquer envoyé**. Cette action ne transmet aucun e-mail : imprimer/enregistrer le PDF et le communiquer au client soi-même.
6. En cas de négociation, créer une nouvelle version ; l’ancienne reste figée et consultable.
7. **Confirmer la vente** en choisissant la proposition retenue. Les lignes sont figées et un seul dossier de facturation est préparé, sans créer immédiatement une facture émise ni un paiement.
8. Dans **Facturation & paiements**, vérifier la prévisualisation puis émettre la facture. Le numéro définitif est attribué à cette étape.
9. Enregistrer l’acompte et le solde avec les montants et dates réellement reçus. Une correction conserve l’ancien enregistrement et ajuste les totaux.

Les devis, relances, interactions, facturations et paiements sont accessibles depuis les fiches client et dossier. Les devis et factures possèdent une vue A4 : **Imprimer / enregistrer en PDF** ouvre le mécanisme natif du navigateur ; l’utilisateur doit sélectionner l’enregistrement PDF dans sa fenêtre d’impression.

## Paramètres à renseigner

- Émetteur : raison sociale, adresse, SIRET, numéro de TVA et coordonnées selon le cas ; conditions et mentions applicables. Aucune information légale inconnue n’est inventée.
- TVA par défaut, seuil de relance, objectif de facturation HT.
- **Afficher les informations de traçabilité**, désactivé par défaut. Les dates commerciales restent toujours visibles.
- Référentiel des unités de vente, normalisé à partir du catalogue. Les unités utilisées par des produits ne sont pas supprimables ; les documents historiques gardent leur unité d’origine.
- Logo officiel : l’import local PNG/JPEG/WebP et l’export d’un HTML qui l’embarque sont conservés. Le logo collé dans le chat n’a pas été accessible comme fichier téléchargeable ; aucun redessin n’a été substitué à l’original.

## Recherche et ergonomie

La recherche d’en-tête conserve ses suggestions. **Entrée sans sélection** ouvre la page complète des résultats ; **flèche puis Entrée** ouvre directement l’enregistrement sélectionné. La page propose catégories, tris et pagination.

Les filtres clients utilisent un seul composant de période (création ou dernière modification), sans filtre Rue. Les badges particuliers/professionnels sont distincts. Les dates techniques sont masquées par défaut, mais restent conservées et exportées. Les tris, le catalogue modifiable, les liens produits, le SIRET, les imports/exports clients et les filtres avancés sont conservés.

## Modèle, migrations et KPI

Schéma de contenu **6**, sans changement du nom IndexedDB ni réinitialisation. Les sauvegardes V1 à V5 restent lisibles. Voir [les décisions V6](docs/CONCEPTION-V6.md) et [le modèle commercial V5](docs/CONCEPTION-V5.md).

Les chiffres distinguent les devis, les ventes confirmées, les factures émises et les règlements effectifs. Les corrections annulées ne sont pas encaissées deux fois. Le taux d’acceptation utilise les devis courants, hors versions remplacées ; le nombre de versions émises est affiché séparément.

Les anciens états « Payée » sans montant/date ne créent aucun règlement fictif : ils restent **à vérifier** jusqu’au rapprochement explicite. Les anciennes opportunités dont la confirmation n’était pas établie sont signalées, et les documents orphelins sont rattachés à des dossiers historiques sans fusion automatique entre projets.

## Sauvegardes, exports et démonstration

- JSON complet : base, catalogue modifié, instantanés des documents, historique et paiements.
- JSON/CSV clients : tous les clients ou résultats filtrés, aperçu avant import, mise à jour par identifiants stables, aucune suppression des fiches absentes.
- JSON/CSV catalogue et CSV des résultats devis/facturation.
- Données de démonstration : 40 clients, 50 projets, versions de devis, ventes confirmées, factures et paiements fictifs. Génération remplaçable ; suppression protégeant les données réelles ou liées à des éléments fictifs.

Pour le CSV clients, utiliser les en-têtes d’un export (`id`, `number`, `lastName`, `firstName`, `type`, `company`, `siret`, `phone`, `email`, `street`, `postalCode`, `city`, `legacyAddress`, `origin`, `notes`, `createdAt`, `updatedAt`) ; séparateur `;` ou `,`, texte UTF-8, dates ISO. Conserver les identifiants, téléphones, codes postaux et SIRET en texte dans Excel. Une colonne absente conserve sa valeur ; une valeur explicitement vide la vide. Les créations historiques connues restent immuables.

L’export HTML avec logo ne contient pas l’activité ni le catalogue modifié : utiliser le JSON pour les transférer. Une seule session de modification est recommandée, sans synchronisation entre appareils.

## Validation et limites

Voir [la recette V6](docs/VALIDATION-V6.md). `python tools/smoke_test.py` exécute les scénarios de développement avec Playwright et un serveur statique local de recette ; aucun de ces outils n’est nécessaire à l’utilisation du CRM.

La politique du Chromium cloud bloque `file://` ; l’ouverture directe et le stockage associé restent à vérifier dans le navigateur cible. Les contrôles fonctionnels ont utilisé une origine locale temporaire et des interactions réseau coupé. Le document imprimable ne constitue pas à lui seul une certification de conformité légale ou de facturation électronique. Les mentions applicables doivent être vérifiées avant diffusion.
