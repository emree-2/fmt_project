# Recette version 6

## Conditions et résultat

Les cinq suites de `python tools/smoke_test.py` ont passé sous Chromium système, piloté par Playwright, avec une origine statique locale temporaire. Les scénarios fonctionnels coupent ensuite le réseau. Ce serveur et Python/Playwright ne sont que des outils de développement ; ils ne sont pas requis par le HTML livré.

Le complément V6 vérifiant le véritable minuteur a ensuite passé dans `python tools/iteration6_test.py` : horloge du navigateur avancée de 61 secondes, création et persistance de l’alerte, maintien du formulaire et du texte saisi, réseau coupé. Pas d’attente réelle d’une minute dans ce test.

## Scénarios V6 réellement vérifiés

- Création d’un dossier vide ; refus de devis sans lignes.
- Éditeur multiligne partagé avec la préparation de devis, modale large.
- Référence dupliquée `531` sélectionnée par l’identifiant produit précis ; unité/prix automatiques ; saisie au clavier.
- Quantité 2,5 × prix 100 € avec TVA 10 % : affichage immédiat de 250 € HT et 275 € TTC ; recalcul après suppression.
- Modification du prix commercial sans changement du prix catalogue ; conservation des lignes existantes, annulation puis réouverture, nouvelle sauvegarde sans perte.
- Recherche en cours conservée lors d’un ajout de ligne et enregistrement refusé si aucun produit exact n’est sélectionné. Ligne vide supprimable sans confirmation de contenu ; ligne sélectionnée avec confirmation.
- Recherche sur les 3 283 lignes intégrées : environ **13 à 23 ms** observées pendant les recettes, maximum 25 suggestions. Défilement horizontal vérifié sur un écran de 700 px ; rendu ordinateur et petit écran capturés pour inspection.
- Dossier ouvert inactif : génération automatique persistée ; contrôles répétés sans doublon ; date métier inchangée par l’alerte et les événements techniques.
- Réalisation : date réelle enregistrée, une seule entrée commerciale, aucune interaction de clôture ajoutée ; renouvellement de la date métier et génération possible après une nouvelle période d’inactivité.
- Annulation automatique : pas de recréation pour la même période ; désactivation : aucune nouvelle génération ; activation et délai via le vrai formulaire Paramètres ; délai après devis conservé séparément.
- Ventes confirmées, dossiers perdus et historiques à vérifier exclus du générateur. Nouvelle activité commerciale reportant le déclenchement.
- Création, modification, réalisation et compte rendu d’une relance manuelle ; date prévue conservée distinctement de la date réalisée.
- Échange rapide avec date/heure préremplies, canal Téléphone, compte rendu et badge Enregistré.
- Journal commun : filtres, types distincts, retard rouge, réalisation verte, annulation grise ; tâches terminées absentes de la liste globale des actions en attente.
- Contrôle pendant un formulaire : saisie conservée ; minuteur réellement exécuté avec l’horloge contrôlée.
- Journaux techniques absents sans traçabilité, fermés par défaut avec traçabilité sur dossiers/clients/produits ; informations commerciales visibles. Les écrans devis/facturation utilisent le même composant.
- Plusieurs étapes cochées, résultats exacts en tableau, sélection conservée en Kanban avec seulement deux colonnes, combinaison avec recherche, tout sélectionner et effacer.
- Paiements Non payé + Acompte/partiel cochés simultanément, compteur exact, tri conservé. Le test de cycle existant vérifie aussi l’export CSV filtré.
- Filtre Unité absent et colonne Unité conservée ; tests administratifs existants vérifiant formulaires, imports/exports et référentiel d’unités.
- Démonstration V6 avec nouveaux champs et relances automatiques, suppression d’un jeu non modifié sans orphelins, protection des liens.

## Migrations et régressions

- **V5 réelle** : chargement du HTML du commit `add11f9`, constitution d’une base IndexedDB avec documents et historique, puis ouverture du HTML V6 sur la même origine. Collections et identifiants comparés avant/après ; lignes commerciales, paiements et facturations inchangés ; instantanés des devis identiques.
- Ancienne réalisation de relance accompagnée d’une interaction dupliquée : les deux IDs restent en base ; un lien permet une seule ligne visible, avec le texte historique conservé.
- Détection d’inactivité à l’ouverture depuis une base persistée, puis nouvelle ouverture conservant le même identifiant d’alerte.
- Restauration par le vrai sélecteur JSON, validation V6 et conservation de la date d’activité sauvegardée ; persistance après rechargement.
- **V1 à V4** : suite historique conservée, migration réelle V4, IDs/liens, absence de paiements fictifs, rapprochement explicite et réutilisation de facture historique.
- **Cycle commercial** : dossiers multiples, devis versionnés et figés malgré modification du catalogue, confirmation unique, facture émise séparément, acompte/solde sur 2 400 €, dépassement refusé, correction tracée, annulation/réémission et sauvegarde.
- **Impression** : invocation du mécanisme natif, génération de PDF de recette A4 (simple et multipage), en-têtes répétés et interface CRM exclue. La fenêtre de choix d’imprimante/PDF n’a pas été manipulée manuellement.
- **Administration** : JSON/CSV clients avec aperçu, SIRET/zéros initiaux, liens et références stables, catalogue, tri global, HTML portable avec image de recette et sans activité privée.
- **Recherche/filtres** : accents, plusieurs mots, villes, dates, prix, liens produits validés, imports et persistance ; 10 000 clients, **5 000 résultats exacts en 53 ms** observés dans la dernière recette générale.
- Aucune erreur JavaScript dans les suites terminées. `node --check`, compilation des scripts de test et `git diff --check` passent. Catalogue initial intégré comparé au précédent commit : identique. Inspection des balises : aucune dépendance distante ajoutée.

## Limites

- Le Chromium géré du cloud refuse `file://` avec `ERR_BLOCKED_BY_ADMINISTRATOR`. L’ouverture directe et IndexedDB sur cette origine doivent être vérifiés dans le navigateur de l’utilisateur. Aucun contournement de cette politique n’a été tenté.
- Aucune relance n’est exécutée lorsque le fichier est fermé. Les contrôles reprennent à l’ouverture et pendant l’utilisation ; pas de notification persistante, envoi d’e-mail ni synchronisation entre appareils.
- Les anciennes dates absentes restent absentes ; la migration ne prétend pas reconstruire une activité ou une réalisation inconnue. L’automatisation est désactivée par défaut.
- Une sauvegarde JSON régulière reste nécessaire pour conserver/transférer les données du navigateur. Le fonctionnement simultané dans plusieurs onglets ou appareils n’a pas été ajouté.
