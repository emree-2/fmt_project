# Recette de la version 2

## Livrable

`index.html` contient HTML, CSS, JavaScript, icône SVG et catalogue initial. Aucun autre fichier du dépôt n’est utilisé à l’exécution. Aucun chargement CDN, API, service worker ou bibliothèque externe. Les imports et exports JSON sont des actions facultatives de l’utilisateur.

## Tests exécutés

Scénarios vérifiés dans un contexte Chromium vierge, automatisés dans `tools/smoke_test.py` (outil facultatif de développement) :

1. **Autonomie** : seuls le document HTML et l’icône embarquée sont chargés. Après chargement, réseau désactivé pour les opérations métier ci-dessous.
2. **Accueil** : Analyses & KPI par défaut ; sept entrées de navigation ; aucune route `dashboard` dans le JavaScript.
3. **Client particulier/professionnel** : société désactivée et vidée pour un particulier, réactivée immédiatement pour un professionnel. Aucun champ Commercial client.
4. **Adresse** : rue, code postal `01000` et ville sauvegardés ; filtres par ville et code postal opérationnels ; recherche par numéro client.
5. **Modification** : action Modifier visible, annulation sans enregistrement, conservation du numéro et de l’identifiant technique, liens vers devis et ventes préservés.
6. **Catalogue** : 3 283 produits ; bouton Modifier sur chaque ligne ; prix et désignation modifiés ; conflit 531 bloqué à la saisie ; prix et noms historiques conservés.
7. **Commerce** : devis de deux lignes (2 × 12 € et 3 × 14 €) = 66 € HT + 13,20 € TVA = 79,20 € TTC. Envoi, relance, acceptation, conversion unique, brouillon exclu du CA puis facture validée incluse une seule fois.
8. **Démo** : 40 clients, huit étapes du pipeline, quatre statuts de devis et ventes sur six mois. Deux générations successives remplacent le jeu supprimable au lieu de l’accumuler. Numéros clients tous distincts.
9. **Suppression protégée** : retour aux données réelles après suppression de la démo. Ajout d’une interaction réelle à un client fictif, puis suppression : interaction et historique lié conservés. Validation des relations après suppression.
10. **Catalogue JSON** : export complet contrôlé, import par identifiant stable testé, prix actualisé, 3 283 produits conservés ; import introduisant une référence ambiguë refusé. Documents historiques inchangés.
11. **Sauvegardes** : export complet JSON contrôlé, restauration via le sélecteur de fichier ; restauration d’une sauvegarde au schéma 1 et migration automatique d’une ancienne base IndexedDB au démarrage. Adresse d’origine conservée sans ville/code postal inventés, commercial retiré du modèle client, identifiants techniques et relations préservés.
12. **Persistance** : rechargement, catalogue modifié et données clients retrouvés dans IndexedDB ; nouveau client après restauration sans collision de numéro.
13. **Régression visuelle** : rendu des sept écrans sans erreur JavaScript ; captures ordinateur et tablette examinées, design initial conservé.

Syntaxe du script contrôlée avec Node. Aucune donnée utilisateur n’a été modifiée par les tests : les données et le stockage de recette appartiennent à un contexte navigateur temporaire.

## Limites constatées

- L’ouverture directe `file://` a été essayée et a renvoyé **ERR_BLOCKED_BY_ADMINISTRATOR** dans le Chromium géré du cloud. Cette politique n’a pas été contournée. La recette fonctionnelle s’est donc déroulée via une origine HTTP locale temporaire. L’application n’utilise aucune API serveur. Le fonctionnement et la persistance à partir d’un fichier local restent à vérifier sur le navigateur cible.
- Les fonctions d’export ont été testées en contrôlant leurs contenus générés. L’enregistrement physique des fichiers téléchargés dépend du navigateur ; la restauration par sélecteur de fichier a été effectivement exercée.
- La recette ne couvre pas tous les navigateurs ni la concurrence entre onglets. Utiliser une seule session de modification et exporter régulièrement.
- La suppression de la démo conserve volontairement les éléments fictifs modifiés ou liés aux données réelles. Le message de résultat indique le nombre d’éléments protégés ; ces éléments ne sont jamais supprimés silencieusement.
