# Recette du prototype

Recette exécutée dans Chromium via Playwright, avec un serveur HTTP local temporaire et un contexte navigateur vierge. Aucune dépendance distante n’a été appelée par l’application. Le serveur de recette a été arrêté ensuite.

Résultats :

- Catalogue embarqué : 3 283 lignes ; référence 531 bloquée à la saisie commerciale.
- Création client et préservation du zéro initial du téléphone.
- Devis à deux lignes : référence 1, quantité 2, PU 12 € ; référence 2, quantité 3, PU 14 €. Résultat : 66 € HT, 13,20 € TVA, 79,20 € TTC.
- Envoi du devis et création d’une relance ; acceptation ; conversion en un seul brouillon de vente ; seconde conversion refusée.
- Brouillon exclu du CA ; facture validée incluse et comptée une seule fois malgré ses deux lignes.
- Modification du prix catalogue à 99 € sans changement des 66 € HT historiques.
- Rechargement de la page : client, téléphone et vente retrouvés dans IndexedDB.
- Validation d’une sauvegarde complète et refus d’une référence de document inexistante.
- Création d’une opportunité et rendu des huit pages sans erreur JavaScript.
- Captures examinées pour la présentation sur ordinateur ; capture tablette produite.
- Vérification de syntaxe JavaScript avec Node.

L’ouverture directe `file://` n’a pas pu être validée ici : la politique du navigateur géré de cet environnement la bloque. Les vérifications fonctionnelles ont donc été effectuées sur l’origine HTTP locale. La compatibilité et la persistance en ouverture directe sont à vérifier dans le navigateur cible. Le fichier livré n’utilise aucune API serveur.

Les tests ne constituent pas une validation exhaustive : déplacement Kanban tactile, téléchargements CSV/JSON dans tous les navigateurs, restauration via sélecteur de fichier et concurrence entre onglets restent à recetter. Une seule session de modification est recommandée.
