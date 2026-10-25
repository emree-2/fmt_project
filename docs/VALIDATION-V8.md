# Validation de la version 8

## Environnement et exécution

`python tools/smoke_test.py` regroupe sept suites : interface V8, parcours V7, saisie/automatisation V6, cycle commercial V5, migrations V1–V4, administration et filtres/performance. Les scénarios utilisent Chromium système avec Playwright, une origine statique locale de recette, puis le réseau coupé pour les parcours fonctionnels. Ces outils ne sont pas requis par le HTML livré.

## Vérifications propres à la refonte

- Chargement du HTML V7 du commit `15d3ae1`, création d’une vraie base IndexedDB, puis ouverture de V8 sur la même origine : état complet strictement identique, schéma **7** conservé. Après navigation, pagination, filtres et rechargement, les paramètres, collections, IDs, lignes, paiements et instantanés sont encore identiques.
- Comparaison du code des dix-huit fonctions centrales de transactions, calculs, validation, migration, relances, devis, facturation, règlements et sauvegarde : identique à V7. Les modifications concernent les rendus et l’état de présentation.
- Six modules — KPI, clients, commercial, facturation, catalogue, paramètres — et trois grandes fiches testés à **1920×1080, 1366×900, 768×1024 et 390×844**. Pas de débordement horizontal de la page ; fenêtres contenues dans la fenêtre du navigateur ; tableaux/Kanban défilants quand nécessaire. Captures bureau et téléphone inspectées.
- Badges d’étapes présents dans le tableau, Kanban, dossier, carte client et résultats de recherche ; paiements utilisant les mêmes tokens en liste et fiche. Vérification du contraste texte/fond des huit étapes et des quatre états de paiement : ratio d’au moins 4,5:1 pour ces composants.
- Corps de tableau d’au moins 13 px, montants alignés à droite. Filtres rapides clients/produits présents une seule fois. Tri conservé après changement de page ; tailles de 20, 40 et 100 lignes exercées, retour à la première page lors du changement de taille.
- Raccourcis du dossier vers Projet et Relances ; ouverture des informations repliées ; synthèse financière à trois valeurs et acompte attendu secondaire.
- Cinq catégories de paramètres : une seule visible à la fois, navigation avec flèches au clavier, formulaires entreprise/unités/relances/sauvegardes réellement présents dans leur catégorie. Réinitialisation isolée sans changement de sa confirmation.
- Recherche universelle : Entrée ouvre les résultats complets ; flèche puis Entrée ouvre la bonne fiche ; badges dans les résultats.
- Notification visible dans la fenêtre native. Export HTML avec un message de recette privé et un client actif : ni ce message ni l’identifiant client ne sont embarqués dans le fichier portable.
- Graphiques : douze valeurs comparées exactement aux agrégats V7 pour facturation, encaissements et ventes confirmées. Valeur accessible au focus clavier, libellé mois/année/montant et graduation présents.
- Menus de filtres fermés lors du passage du focus à un autre contrôle ; les tests traversent les filtres rapides et avancés sans menu résiduel masquant la cible.

## Régressions métier couvertes

Les tests existants gardent leurs assertions de données et utilisent les nouvelles catégories des paramètres :

- Rechercher/modifier un client et un produit, SIRET, imports JSON/CSV avec aperçu, références et liens stables.
- Créer un dossier vide puis multiligne, saisir quantités/prix/TVA, recalcul immédiat, édition sans perte.
- Préparer/émettre un devis, créer une nouvelle version, conserver les instantanés après modification du catalogue.
- Programmer/modifier/effectuer/annuler une relance ; modifier un échange ; refuser les écritures commerciales après clôture.
- Détecter une inactivité sans doublons, conserver la date métier, désactiver la règle, détecter au démarrage et exécuter le minuteur avec l’horloge avancée de 61 secondes sans perdre le formulaire.
- Confirmer une seule vente, ouvrir la bonne facturation, émettre la facture, saisir acompte/solde/personnalisé, refuser dépassement/double soumission, conserver les corrections et réémissions.
- Sauvegarder/restaurer le JSON, conserver les anciennes sauvegardes V1–V7, générer/supprimer la démonstration avec protections.
- Impression native demandée et PDF de recette A4 simple/multipage contrôlés, en-têtes répétés et interface CRM exclue. Mise en page imprimée conservée séparément des styles écran.
- Recherche, tris, filtres cumulés et multisélection, pagination, réseau coupé. Mesure récente sur **10 000 clients** : **5 000 résultats exacts en environ 79 ms**, dépendant de la machine.

`node --check`, compilation Python et `git diff --check` sont exécutés. Catalogue initial embarqué comparé à V7 : identique. Aucune balise ne charge une ressource externe. Aucune donnée de démonstration ou de recette n’est insérée dans le HTML de production.

## Limites vérifiées

- Le navigateur géré du cloud bloque `file://` avec `ERR_BLOCKED_BY_ADMINISTRATOR`. L’ouverture directe et le stockage IndexedDB sur cette origine restent à vérifier dans le navigateur de l’utilisateur. Les tests hors ligne ont utilisé l’origine locale de recette ; aucune politique n’a été contournée.
- L’accessibilité est vérifiée sur les composants cités et les parcours clavier ; il ne s’agit pas d’un audit exhaustif avec lecteurs d’écran ou de tous les navigateurs mobiles réels.
- La fenêtre système d’impression/enregistrement PDF n’a pas été manipulée manuellement ; invocation et sorties PDF de recette ont été contrôlées.
- Les relances restent locales et s’exécutent à l’ouverture et pendant l’utilisation. Pas de traitement fichier fermé, de notification permanente, d’envoi d’e-mail ou de synchronisation entre appareils.
