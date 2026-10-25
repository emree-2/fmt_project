# Recette version 7

## Conditions

Six suites automatisées sont réunies dans `python tools/smoke_test.py` : V7/navigation/règlements/migration V6 ; saisie/automatisation/migration V5 ; cycle commercial et paiements ; migrations V1–V4 ; administration/imports ; filtres/performance. Les tests utilisent Chromium système et une origine HTTP statique locale temporaire. Le réseau est ensuite coupé pour les parcours fonctionnels. Python, Playwright et ce serveur sont uniquement des outils de recette, absents des dépendances d’exécution du HTML.

## Vérifications V7

- Dossier non confirmé : aucun accès à une facturation inexistante. Après confirmation, bouton « Voir la facturation », ouverture du bon enregistrement et retour au dossier. Visites répétées sans nouvelle facture, vente ou transaction.
- Bloc indépendant de facturation retiré du dossier ; blocs Devis et Facturation retirés du client. Accès par les cartes et les dossiers conservé.
- Parcours commercial absent sans traçabilité, fermé par défaut lorsqu’elle est activée ; statut actuel toujours affiché.
- Échange rapide modifié depuis sa ligne : même ID, même création, date de modification présente, canal/description actualisés et une seule interaction.
- Formulaire d’échange ouvert avant clôture, puis soumis après passage en Perdu : transaction refusée, aucune nouvelle interaction. Création d’échange/relance refusée sur dossier perdu. Dossier confirmé : actions de création et modification d’échange absentes, historique conservé.
- Relance en retard : statut sélectionnable dans sa cellule, passage à Effectuée, date prévue conservée, date réelle ajoutée, badge vert et aucune interaction dupliquée. Autre relance passée à Annulée et badge gris. Les tâches terminées restent consultables sans action principale de réalisation.
- Type, Date prévue, Date réalisée et Statut triés dans les deux sens ; stockage inchangé. Filtres Type/Statut multisélection dans les en-têtes, combinaisons et effacement ; anciens filtres supérieurs absents ; remise à l’ordre prioritaire.
- Vente de **3 000 € TTC** : bouton unique de règlement, quatre choix, propositions de 1 500 € pour l’acompte et 3 000 € pour solde/total sans règlement précédent ; personnalisé vide et saisie libre.
- Premier règlement personnalisé de **600 €** : deux soumissions consécutives ne créent qu’un enregistrement. Le récapitulatif affiche 2 400 € restants. Acompte complémentaire proposé de **900 €** pour atteindre 50 %, solde/total proposé de 2 400 € avant cet acompte.
- Après 1 500 € encaissés : choix Acompte proposant zéro, nouvel enregistrement à zéro refusé ; montant négatif et dépassement de 0,01 € refusés. Solde proposé de 1 500 €, puis statut Payé à 3 000 € réellement encaissés.
- Correction du solde de 1 500 € en 1 000 € : transaction originale annulée/conservée, lien de correction présent et 500 € à nouveau dus. Choix Règlement total proposant seulement ces 500 €, puis retour à 3 000 € encaissés. Type choisi conservé sur les nouvelles transactions.
- Ancien état de paiement à vérifier : transaction refusée sans rapprochement, même avec une soumission contournant la validation du navigateur ; acceptée après acquittement explicite.
- Carte client ouvrant directement le bon projet ; bouton secondaire ouvrant sa facturation. Cartes de projets avec montant/statut/dates ; grille à une colonne à 600 px. Plus de huit projets : expansion sur place et associations conservées.
- Produits d’intérêt : choix de la référence dupliquée `531` par ID stable, carte ouvrant exactement sa fiche, ajout répété sans doublon, prix courant affiché, produit désactivé conservé et signalé consultable.
- Historique des échanges client absent sans traçabilité, replié par défaut avec traçabilité, contenu conservé après ouverture.
- Rechargement : règlements/corrections, échange édité et réalisation de relance persistants. Restauration par le vrai sélecteur JSON, schéma validé en V7.

## Migration et régressions

La migration **V6 réelle** charge le HTML du commit `f5f3c94`, crée une base IndexedDB de démonstration complète, puis ouvre V7 sur la même origine. La comparaison de l’état complet avant/après ne diffère que par `schemaVersion` : toutes les collections, paramètres, IDs, lignes, paiements, devis, factures, instantanés et historiques restent identiques.

Les suites précédentes, adaptées aux nouveaux contrôles, continuent à vérifier :

- Migration réelle V5, anciens doublons de réalisation conservés/regroupés, et migrations V1–V4 sans inventer de paiements ni de dates inconnues.
- Éditeur produits, sélection stable, quantités/prix/TVA et montants immédiats, édition sans perte, petits écrans, devis et ventes nécessitant des lignes valides.
- Relances automatiques : génération locale persistée, absence de doublons, exclusions des dossiers fermés/à vérifier, activité métier séparée des alertes, désactivation et contrôles à l’ouverture. Véritable minuteur testé par avance de 61 secondes de l’horloge, réseau coupé, formulaire conservé.
- Cycle devis versionné/instantané → confirmation unique → facture émise séparément → acompte/solde/corrections. Instantanés inchangés après modification du catalogue et réémission conservant le numéro/contenu historique.
- Impression : demande native, PDF de recette A4 simple et multipage avec en-têtes répétés, interface CRM exclue.
- JSON/CSV clients/catalogue, aperçu d’import, SIRET et zéros initiaux, stabilité des liens, logo de recette dans un HTML portable sans activité privée, démonstration et sauvegardes.
- Recherche, filtres cumulés, multisélection tableau/Kanban/paiements, tris et pagination. Mesure récente : 10 000 clients, 5 000 résultats exacts en environ 66 ms ; cette mesure dépend de la machine.

Les suites terminées ne signalent pas d’erreur JavaScript. `node --check`, compilation des scripts Python et `git diff --check` passent. Catalogue initial embarqué comparé au précédent commit : identique. Inspection des balises HTML : aucun chargement distant ajouté. Captures de recette du formulaire de règlement et des cartes inspectées ; aucune donnée de test embarquée dans le HTML livré.

## Limites

- Le Chromium cloud géré refuse l’origine `file://` (`ERR_BLOCKED_BY_ADMINISTRATOR`). L’ouverture directe et IndexedDB doivent encore être vérifiés dans le navigateur de l’utilisateur. Les scénarios hors ligne ont été exécutés sur l’origine locale de recette ; aucune politique n’a été contournée.
- Les alertes automatiques fonctionnent à l’ouverture et pendant l’utilisation. Aucun traitement lorsque le fichier est fermé, ni notification permanente, envoi d’e-mail ou synchronisation entre appareils.
- La fenêtre système d’impression/enregistrement PDF n’a pas été manipulée manuellement ; l’invocation et les sorties PDF de recette ont été contrôlées.
- Les anciennes données manquantes ou ambiguës restent signalées ; la mise à jour ne reconstruit pas leur contenu inconnu. Les anciennes transactions sans `paymentType` conservent leur catégorie existante.
