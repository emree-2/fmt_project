# Version 7 — navigation et suivi quotidien

L’application reste dans `index.html`, sans dépendance externe. IndexedDB garde son nom, sa version physique 1, son magasin et la clé `main`. Le schéma de contenu devient **7**. La migration V6 → V7 clone les données et change uniquement ce numéro : aucun ID, montant, lien, instantané ou historique existant n’est réécrit. Les migrations V1 à V5 passent par les étapes précédentes.

## Navigation et fiches clients

Le dossier commercial possède un bouton « Voir la facturation » dès qu’un enregistrement lié existe. Ce bouton et les cartes clients appellent directement la fiche identifiée ; aucun numéro, document ou règlement n’est créé par une consultation. La fiche de facturation garde le retour au dossier.

La fiche client présente son en-tête, ses informations/notes, les cartes de projets puis les cartes de produits d’intérêt. Les sections autonomes Devis et Facturation ont disparu uniquement de cet écran ; le dossier donne accès aux versions de devis et à sa facturation.

Les projets sont classés par activité connue, sinon création, avec huit cartes initiales et une expansion sur place. Une vente confirmée indique son montant TTC figé ; les autres projets affichent l’estimation HT. Chaque carte possède un bouton principal couvrant sa surface et un éventuel bouton secondaire de facturation, sans boutons imbriqués, accessibles au clavier.

Les produits d’intérêt sont recherchés localement puis choisis par ID stable, y compris pour une référence dupliquée. L’ajout vérifie le couple client/produit dans la transaction. Les anciens doublons éventuels restent en base mais ne multiplient pas les cartes. Prix et caractéristiques affichés sont ceux du catalogue courant ; un produit inactif déjà associé reste consultable. Aucun document financier n’est recalculé par ces cartes.

## Formulaire unique de règlement

Les quatre types d’interface sont `deposit`, `balance`, `total`, `custom`. La proposition d’acompte est `min(reste dû, max(0, moitié TTC arrondie - encaissé))`. Solde et règlement total proposent tous deux le reste effectivement dû. Un acompte déjà atteint propose zéro et ne peut pas être enregistré comme nouveau paiement sans montant réellement positif. Le montant personnalisé démarre vide.

La sélection recalcule immédiatement le montant et le récapitulatif. Le montant réellement perçu reste modifiable, même pour un type prédéfini. Les deux derniers types n’entraînent aucun recalcul de la vente ou de la facture.

Nouveau champ **optionnel** `payments.paymentType`, enregistré pour les nouveaux règlements et corrections. Les anciennes valeurs `kind` (`deposit`, `balance`, `other`) sont conservées pour les relations, calculs et sauvegardes existants. `total` et `custom` utilisent `kind:'other'`. Les anciens paiements n’ont pas de type nouveau inventé ; leur libellé reste basé sur leur catégorie connue. Les nouveaux règlements de démonstration portent le type approprié.

L’ancienne transaction corrigée reste annulée (`voided`) avec son montant, sa date et son motif, puis un nouvel enregistrement la référence. Pour calculer le plafond d’une correction, la transaction corrigée est exclue du montant déjà encaissé ; un montant corrigé à zéro reste une annulation conservée. Le formulaire indique cette distinction. Le contrôle de solde est refait dans la transaction, et le verrou de soumission existant empêche les doubles clics. Les états historiques à vérifier conservent l’obligation de rapprochement explicite.

## Journal des relances et échanges

Les colonnes Type, Date prévue, Date réalisée et Statut réutilisent le tri commun des tableaux. Les filtres Type/Statut à cases à cocher sont intégrés dans les en-têtes ; les anciens filtres supérieurs ont été retirés. Une sélection vide affiche tout. Les valeurs d’une colonne se combinent par « ou » et les deux colonnes par « et ». Les filtres se combinent au tri sans changer l’ordre stocké. L’ordre prioritaire reste disponible et remet le tri de colonne à zéro.

Les menus se positionnent dans la fenêtre pour rester accessibles malgré le défilement du tableau et de la modale ; ils se ferment au clic extérieur ou avec Échap. Les types/statuts actifs restent comptés dans l’en-tête.

Une relance en attente propose directement Prévue/À effectuer (ou En retard calculé), Effectuée et Annulée. La réalisation enregistre `completedAt`, renouvelle l’activité métier et conserve une seule entrée. L’annulation conserve sa date et ne simule pas un contact commercial. Une tâche terminée ne se réactive pas depuis ce contrôle ; son statut devient un badge et son détail reste consultable. Aucun nouvel état persistant de retard n’est créé.

La transaction de statut peut garder la modale ouverte et ne reconstruire que le journal : pas de perte de saisie ni fermeture/réouverture nécessaire. Le détail du compte rendu des relances terminées reste modifiable sur un dossier ouvert, en lecture seule sur un dossier clôturé ou à vérifier.

L’édition d’un échange modifie le même objet `interactions` : `id` et `createdAt` conservés, `occurredAt`, `channel`, `note` modifiables, `updatedAt` actualisé. Un événement technique décrit la modification et la date d’activité métier est renouvelée. Aucun nouvel objet ni lien n’est créé par une édition.

## Dossiers fermés et traçabilité

Création/édition d’échanges et programmation/édition de relances nécessitent un dossier ouvert. Le contrôle est effectué à l’ouverture du formulaire et dans sa transaction ; un formulaire ancien ne peut donc pas écrire après une clôture. Les dossiers confirmés et perdus restent en lecture seule pour les échanges ; les dossiers historiques à vérifier doivent d’abord être clarifiés. Les règlements restent accessibles après confirmation dans la facturation.

Tous les historiques restent en base. Le parcours des étapes est désormais conditionné à `settings.traceability`, fermé par défaut, comme le journal technique. L’historique des échanges de la fiche client suit la même règle. Le journal commercial du dossier, ses relances et son statut actuel restent visibles quel que soit ce paramètre.
