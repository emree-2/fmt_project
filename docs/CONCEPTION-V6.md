# Version 6 — décisions de fonctionnement

`index.html` reste l’unique fichier d’exécution. Aucun service distant ni dépendance ajouté. IndexedDB conserve son nom, sa version physique 1, son magasin et sa clé `main`. Le schéma de contenu devient **6** ; migration des sauvegardes V1 à V5 sans réinitialisation ni changement des identifiants existants.

## Saisie commune

Dossiers et brouillons de devis utilisent le même éditeur : une ligne vide, recherche locale dans la cellule, 25 suggestions maximum, sélection par identifiant produit stable, champs quantité/prix/TVA et calcul arrondi au centime pour chaque ligne. Référence, désignation, caractéristiques, unité et prix proviennent du produit choisi. Les références dupliquées restent distinguables par leur identifiant. Le changement de sélection initialise la quantité à 1 ; modifier le prix dans le dossier ne modifie pas le catalogue.

Les champs numériques se recalculent sans reconstruire le formulaire. Un dossier peut rester vide. Une ligne vide inutilisée est ignorée ; une recherche saisie sans sélection doit être résolue ou supprimée avant enregistrement. Les unités et prix déjà enregistrés restent conservés lors de l’édition. Les documents émis et ventes confirmées gardent leurs instantanés précédents.

## Activité et automatisation

Nouveau champ `opportunities.lastBusinessActivityAt`. Mise à jour lors d’une modification effective du projet, d’étape ou de lignes, de la préparation/émission/qualification d’un devis, d’un nouvel échange enregistré ou de la réalisation d’une relance. Un simple enregistrement de projet inchangé ne renouvelle pas le délai. Une activité saisie a posteriori renouvelle le suivi à sa date d’enregistrement ; la date réelle de l’échange reste distincte dans le journal.

La programmation, l’annulation et la génération d’une alerte, les changements de paramètres et les événements purement techniques ne renouvellent pas cette date. La restauration d’une sauvegarde conserve la date métier sauvegardée.

`settings.autoReminders = {enabled, days}` : désactivé par défaut, délai initial de 10 jours, entier de 1 à 3650 jours. `settings.reminderDays` reste indépendant et sert notamment à la relance suivant l’envoi d’un devis.

Contrôles à l’ouverture avant affichage, à l’accès au suivi, après enregistrement, chaque minute lorsque la page est visible, au retour sur la page et à la reprise de la fenêtre. Toutes les écritures passent par la même file et sont persistées dans IndexedDB. Un contrôle périodique n’efface jamais un formulaire en cours. Il n’existe aucun traitement lorsque le fichier est fermé ; les retards sont détectés à la prochaine ouverture.

Seuls les dossiers ouverts dont une activité est datée sont éligibles. Ventes confirmées, perdus et historiques à vérifier sont exclus. L’échéance est la date d’activité augmentée du délai en jours calendaires du navigateur. Une alerte automatique porte `origin:'automatic'`, `reason:'inactivity'`, `inactivityKey` (date métier de départ), `triggeredAt`, date prévue et motif. Une alerte automatique d’inactivité en attente bloque toute nouvelle alerte sur ce dossier. Une alerte terminée ou annulée empêche aussi la recréation pour la même période d’inactivité. La réalisation renouvelle la date métier et permet un nouveau cycle après le délai. Un nouveau contact client ne supprime pas une alerte déjà créée ; il appartient au commercial de l’effectuer ou de l’annuler.

## Journal commercial et relances

Les relances conservent `done`, `cancelled`, `date`, les rattachements et IDs existants. Champs complémentaires : `origin` (manual/automatic), `reason`, `notes`, `report`, `completedAt`, et dates d’annulation/modification si applicables. Le statut est calculé pour ne pas stocker un état « En retard » devenu périmé. La date initialement prévue et la date effective restent distinctes.

Une réalisation modifie cette relance et ajoute un événement technique, sans créer d’interaction commerciale supplémentaire. Le compte rendu peut être enregistré sur la même relance. Une relance prévue peut être modifiée ou annulée ; une terminée reste consultable.

Les échanges ajoutent `origin:'quick'`, `occurredAt` et `channel`, distincts de `createdAt`. Les anciens échanges sans dossier ne sont pas rattachés arbitrairement et restent accessibles depuis le client. Aucun échange n’est supprimé.

Le journal commun présente les relances à traiter d’abord, puis les éléments passés, avec type/statut/tri. Les anciennes interactions de clôture ne sont regroupées avec une relance que si le dossier, le client, le libellé exact et la date à moins de deux secondes identifient une seule relance effectuée. Un lien `interactions.reminderId` masque la seconde ligne, conserve le texte dans la ligne historique et garde l’enregistrement original en base et dans le JSON. Toute ambiguïté reste visible. Les anciennes relances sans date de réalisation restent explicitement « Non renseignée (historique) ».

La vision globale regroupe les tâches en attente automatiques/manuelles, y compris les relances manuelles de dossiers historiques à vérifier. Les clôtures annulent les tâches restantes en conservant leur historique.

## Migration, démonstration et traçabilité

Pour V5, la dernière activité initiale est la date connue la plus récente parmi création/modification du dossier, échanges et réalisations de relances. Sa provenance est signalée `activitySource:'migration'` ; si aucune date n’est connue, elle reste vide et aucune alerte n’est inventée. Les migrations antérieures et leurs précautions restent applicables. La base V6 n’est pas réinterprétée à chaque ouverture.

Les données de démonstration reçoivent les nouveaux champs. Les alertes automatiques et événements générés sur un dossier fictif gardent son marquage, afin de rester supprimables avec ce jeu si aucun lien réel ou modification ne les protège. Les nouveaux liens entre interactions et relances sont pris en compte dans la protection des données.

Les journaux techniques ne sont rendus que lorsque la traçabilité est activée, dans un `<details>` fermé à chaque ouverture de fiche. Les dates métier, règlements, échanges et relances restent visibles. Les changements d’étape futurs sont également consignés dans un parcours commercial accessible indépendamment de la traçabilité. La migration ne reconstruit pas des transitions anciennes inconnues.

## Filtres

Un composant commun à cases à cocher sert aux étapes commerciales et aux états de paiement. Sélection vide = tous. Conservation entre tableau et Kanban, masquage des colonnes exclues, combinaison avec recherche, tri, compteurs et pagination ; l’export de facturation suit les résultats filtrés.

Le filtre Unité est retiré du catalogue et de son état de recherche, sans modification des unités produit, lignes, documents, paramètres, imports ou exports.
