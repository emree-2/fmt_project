# Recette version 9

## Conditions

Huit suites sont regroupées dans `python tools/smoke_test.py` : V9/filtres partagés, interface V8, parcours V7, automatisation V6, cycle commercial, migrations V1–V4, administration et filtres/performance.

Exécution sous Chromium système avec Playwright, origine HTTP locale de recette puis réseau coupé pour les parcours fonctionnels. Aucun de ces outils n’est requis par le HTML de production.

## Scénarios V9 réellement exercés

- Base IndexedDB créée avec le HTML V8 du commit `ff71bf6`, puis ouverture de V9 sur la même origine. État complet comparé avant/après les filtres et après rechargement : identique, schéma 7 conservé, aucun changement des paramètres, IDs, relations, montants ou instantanés.
- Avatar absent, marque latérale conservée, aucune substitution décorative.
- Colonne Type clients : sélection Professionnel depuis l’en-tête, valeur déjà cochée dans le panneau ; ajout Particulier dans le panneau, deux cases cochées dans l’en-tête. Combinaison Type/Ville/Code postal vérifiée contre le résultat attendu.
- Coordonnées client : recherche d’une partie d’e-mail, résultat exact, valeur synchronisée dans le panneau ; le contrôle est textuel, pas une période.
- Date de création : période janvier, 20 clients exacts sur 40 ; type de date et bornes synchronisés avec le composant principal.
- Réinitialisation dans le panneau : critères de la liste effacés, recherche textuelle préservée ; les critères d’un autre module restent inchangés. Fermer le panneau conserve les sélections.
- Prix catalogue : bornes 20–40 saisies dans l’en-tête, mêmes valeurs dans le panneau et slider ; changement à 25 depuis le panneau, valeur reprise dans l’en-tête. Comparaison du nombre sur tout le catalogue.
- Référence située à la fin du catalogue trouvée depuis son filtre de colonne : preuve que la sélection précède la pagination. Tri, page suivante, taille de page et critères conservés ensemble.
- Étapes Nouveau contact + Besoin identifié : deux valeurs sélectionnées, panneau synchronisé, deux colonnes en Kanban, conservation au retour en tableau.
- Saisie progressive au clavier d’un minimum de 100 : focus et valeur conservés pendant les actualisations ; résultat comparé à la sélection complète des dossiers.
- Devis, relances, facturations, journal, historique des règlements, recherche globale et détail KPI : présence des filtres pertinents ; aucune commande dans Actions, les lignes de saisie ou les lignes documentaires.
- Paiements Non payé + Partiel cochés dans l’en-tête, mêmes cases dans le panneau. Le calcul financier n’utilise pas le sous-ensemble affiché.
- Journal : filtre de type depuis la fiche, menu à l’intérieur du dialogue natif, choix repris dans son panneau. Les régressions vérifient également la réalisation/annulation et l’édition des échanges.
- Analyses : un seul panneau, période déplacée à l’intérieur. Recherche globale : un seul panneau et filtrage avant pagination par catégorie.
- Menus vérifiés à 768×1024 et 390×844, placés dans la fenêtre et hors du conteneur de tableau. Captures inspectées ; tableaux larges défilants sur petit écran.
- Tri et filtrage indépendants : ouvrir une icône de filtre ne change pas le tri ; les régressions exercent les tris dans les deux sens et le retour au défaut.

## Régressions conservées

Les tests précédents sont adaptés aux nouveaux emplacements des contrôles, sans retirer leurs assertions de données :

- Création/modification clients et catalogue, imports JSON/CSV avec aperçu, SIRET, liens, références et zéros initiaux.
- Dossier vide puis multiligne, quantités/prix/TVA, totaux immédiats, édition sans perte ; devis versionnés et figés.
- Relances manuelles/automatiques, inactivité sans doublons, date métier distincte des alertes, désactivation, contrôle réel du minuteur par avance de 61 secondes sans perte de formulaire.
- Échanges modifiables, verrouillage après clôture, confirmation unique, navigation directe vers la bonne facturation.
- Acompte/solde/personnalisé, double soumission, dépassement refusé, corrections et transactions d’origine conservées, annulation/réémission de facture.
- Sauvegardes/restauration, démonstration et protections, migrations réelles V4/V5/V6/V7/V8 vers le contenu actuel sans paiements ou dates inventés.
- Impression native et PDF A4 de recette simple/multipage ; en-têtes répétés, filtres et interface CRM exclus. HTML portable sans activité privée.
- Six modules et grandes fiches aux résolutions 1920, 1366, 768 et 390 px ; clavier, badges, graphiques aux valeurs inchangées.
- Performance : 10 000 clients, 5 000 résultats exacts en environ 175 ms lors de la recette générale. La mesure dépend de la machine ; le catalogue conserve ses 3 283 lignes et sa recherche locale.

Les suites terminées ne signalent pas d’erreur JavaScript. Vérifications statiques : syntaxe JavaScript, compilation des scripts Python, `git diff --check`, catalogue embarqué identique et absence de chargement distant.

## Limites

Le navigateur cloud géré refuse `file://` avec `ERR_BLOCKED_BY_ADMINISTRATOR`. L’ouverture directe et IndexedDB sur cette origine restent à vérifier dans le navigateur de l’utilisateur ; les tests hors ligne ont utilisé une origine locale de recette, sans contournement de politique.

Les filtres sont des états d’affichage en mémoire : conservés pendant la navigation prévue, ils ne sont pas sauvegardés dans le JSON ni restaurés après redémarrage. Les dates clientes conservent leur sélection unique création/modification. Les calendriers restent natifs et leur apparence dépend du navigateur.

La fenêtre système d’impression/enregistrement PDF n’a pas été manipulée manuellement. Les alertes d’inactivité restent locales et ne s’exécutent pas lorsque le fichier est fermé. Aucune synchronisation ou notification permanente n’est ajoutée.
