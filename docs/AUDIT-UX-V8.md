# Audit UX/UI — version 8

## Cadre

Audit des six modules avec le jeu de démonstration et des fiches client, dossier, facturation. Cette passe conserve la logique métier, le schéma de contenu 7, IndexedDB, les imports/exports, les instantanés et les identifiants. L’interface est appelée V8 ; aucune migration V7 → V8 n’est nécessaire.

## Constats et décisions appliquées

| Zone | Problème observé | Réponse ergonomique |
|---|---|---|
| Navigation | Symboles disparates, libellés mal alignés, recherche peu intégrée | SVG embarqués partageant le même trait, grille icône/libellé, actif violet, recherche plus large avec résultats espacés et sélection clavier visible |
| Statuts | Devis envoyé orange dans un écran et violet dans un autre ; tous les dossiers du tableau portaient le même badge | Fonctions de badges communes pour étapes, devis et paiements ; tokens pastel et libellés conservés dans tableaux, Kanban, fiches, cartes et recherches |
| Tableaux | Petits caractères, montants alignés comme du texte, boutons répétitifs dominants | Corps 13 px, informations secondaires 12 px, colonnes numériques alignées à droite, dates sans coupure, survol léger, actions compactes avec icônes utiles et texte |
| Pagination | Taille fixe et commandes peu explicites | Résultats/page visibles, titres Précédent/Suivant, choix 20/40/50/100 lignes sur les listes principales, remise à la première page sans perdre filtre/tri |
| Recherches | Critères fréquents enfouis dans un panneau complet | Type/Ville clients et Famille/Couleur produits accessibles près de la recherche, sans duplication des contrôles ; autres critères repliés, chips et réinitialisation conservés |
| Fiche client | Coordonnées en paragraphes et actions séparées | En-tête regroupé, coordonnées/adresse/entreprise/notes en libellés-valeurs, cartes structurées et compactes, navigation directe conservée |
| Dossier | Séquence verticale peu hiérarchisée, informations du projet prenant la même importance que les actions | Synthèse montant/action/activité, barre d’actions, raccourcis de section, informations complémentaires repliées, produits/devis/journal séparés sans sous-écrans supplémentaires |
| Kanban | Étapes visuellement proches, retard peu visible | Liseré de colonne et badge correspondant à l’étape, compteurs réels, signalement textuel des relances en retard, contenu réduit au projet/client/montant/action |
| Journal | Dates et filtres d’en-têtes peu lisibles | Alignements, icônes de filtre distinctes du tri, statuts et types harmonisés, liseré discret pour les retards, commandes compactes, menus clavier/clic/focus |
| Facturation | Acompte attendu aussi dominant que les montants réellement encaissés | Trois valeurs principales : total, encaissé, reste ; acompte attendu secondaire, statut distinct, progression conservée, montant reçu et choix du règlement renforcés |
| KPI | Hiérarchie variable, graphiques difficiles à lire au clavier | Cartes de même famille et unités conservées, graduations, légendes, valeur au survol/focus ; aucune addition ou redéfinition d’indicateur |
| Paramètres | Longue page réunissant tous les réglages | Cinq catégories accessibles au clavier ; déplacement des formulaires existants avec leurs gestionnaires et validations ; réinitialisation isolée visuellement |
| Fenêtres/formulaires | Lecture étroite et actions d’enregistrement éloignées | Fiches larges, en-tête de fermeture fixe, pied de formulaire accessible pendant le défilement ; éditeur produits conservant le défilement horizontal sans limite verticale imbriquée |
| Retours | Toast extérieur masqué derrière une fenêtre native | Message également présenté dans la fenêtre, traitement distinct des erreurs ; contenu purgé de l’export HTML portable pour préserver sa confidentialité |
| Petit écran | Densité des colonnes et menus | Menus horizontaux, grilles à une colonne, résumé financier empilé, tableaux défilants, recherche et fenêtres adaptées ; pas de débordement global dans les tailles vérifiées |

## Système visuel

Palette : violet `#29166F`, rouge de marque `#DE2418`, surfaces claires, texte principal `#252238`, gris secondaire contrasté. Les badges gardent toujours leur texte.

- Nouveau : bleu ; besoin identifié : indigo ; devis à préparer : orange ; devis envoyé : violet ; négociation : ambre ; confirmé : vert ; perdu : gris ; historique à vérifier : avertissement mauve.
- Relance prévue : ambre ; retard : rouge discret ; effectuée : vert ; annulée : gris ; échange : bleu ; origine automatique : violet.
- Paiement non payé : rouge discret ; partiel : ambre ; payé : vert ; historique à vérifier : mauve avec bordure.

Boutons, champs, cartes, titres, espacements, tableaux et fenêtres sont définis dans une couche CSS écran commune. Les règles d’impression restent séparées et les SVG sont intégrés au fichier. Pas de police, bibliothèque ou ressource distante ajoutée. Les transitions restent courtes et désactivées avec `prefers-reduced-motion`.

## Choix de périmètre

- La taille de page et la catégorie de paramètres sont des états de présentation en mémoire, sans modification des sauvegardes métier.
- La recherche universelle conserve ses groupes paginés de 30 résultats ; les nouvelles tailles concernent les listes principales.
- Les informations de projet repliées se déploient aussi depuis le raccourci Projet. Les produits, devis et interactions restent dans la même fiche.
- Les tableaux larges et le Kanban défilent horizontalement sur téléphone ; les colonnes métier ne sont pas supprimées.
- Les formulaires existants des paramètres sont déplacés dans le DOM, et non recréés : leurs validations, confirmations et transactions restent en place.
- Les calendriers de saisie restent natifs : leur apparence dépend du navigateur. Les valeurs affichées par le CRM restent au format français.
