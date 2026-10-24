# Décisions de conception — V5

## Dossier central et deux modules opérationnels

La navigation comporte Analyses & KPI, Clients, Suivi commercial & ventes et Facturation & paiements. Catalogue et Paramètres restent en bas. La route historique des devis redirige vers l’onglet intégré ; aucune page autonome Devis & relances n’est conservée.

Le dossier représente un projet précis, avec plusieurs lignes et ses propres échanges. Il peut être créé incomplet. Les lignes deviennent obligatoires pour un devis et une confirmation. Les coordonnées de l’émetteur et du client sont vérifiées avant l’émission d’un document, plutôt que de bloquer la préparation d’un projet encore incomplet.

## Relations

| Collection | Fonction |
|---|---|
| clients / products / interests | Identifiants existants conservés, informations clients et catalogue, intérêts produits |
| opportunities / opportunityLines | Projet, client, premier contact, étape, description, notes et lignes proposées |
| quotes / quoteLines | Version de proposition liée au dossier, numérotation propre, échéance, conditions et lignes |
| confirmedSales | Une confirmation par opportunité, lien vers la proposition retenue et la facturation, instantané des lignes vendues |
| sales / saleLines | Ancienne collection conservée comme dossiers de facturation et leurs lignes figées ; numéro DOS distinct du numéro final FAC |
| payments | Montant, date réelle, mode, référence, date informatique et éventuelle correction d’un paiement antérieur |
| reminders / interactions / events | Relances rattachées au dossier, échanges et historique horodaté |
| settings | Émetteur, TVA, objectif, unités, traçabilité et logo local |

La copie des lignes à l’émission ou à la confirmation est volontaire : elle constitue un instantané métier, et non une seconde saisie. Les changements ultérieurs du catalogue, du client ou de l’émetteur ne réécrivent pas les documents émis.

La confirmation est explicite et contrôlée dans la transaction : une seule vente confirmée et une seule facturation associée. Si un ancien dossier de facturation est déjà lié au projet, la confirmation le réutilise au lieu de créer un doublon. Les soumissions de formulaire sont également protégées contre les doubles clics pendant l’écriture.

## Statuts et relances

Sept étapes : Nouveau contact, Besoin identifié, Devis à préparer, Devis envoyé, Négociation / relance, Vente confirmée, Perdu / abandonné. Une colonne supplémentaire « À vérifier (historique) » n’apparaît que lorsqu’il existe des données ambiguës.

Le devis stocke le code historique `À préparer` pour compatibilité, affiché « Brouillon ». L’acceptation de la proposition ne signifie ni vente confirmée, ni paiement, ni livraison. La confirmation reste une action distincte.

L’émission du devis programme une relance locale. Les relances ont un statut prévu, effectué, en retard ou annulé ; le retard est calculé à la date courante. La clôture confirmée/perdue annule les rappels actifs sans effacer leur historique. Aucun e-mail ou rappel serveur n’est envoyé.

## Émission et corrections

Les devis possèdent un numéro propre et plusieurs versions par dossier. Une version émise conserve ses coordonnées, lignes, conditions et montants. La nouvelle version remplace la précédente pour le calcul du taux d’acceptation, sans l’effacer.

Le dossier de facturation est créé au moment de la confirmation. La facture est émise plus tard après vérification et reçoit alors un numéro final indépendant. Une annulation conserve le document et le motif ; une nouvelle édition réserve un nouveau numéro et garde l’ancienne copie. Cette annulation n’efface pas les règlements et ne simule ni remboursement ni avoir fiscal.

L’impression utilise la fenêtre du navigateur et une feuille A4 dédiée. Les menus et les boutons ne sont pas imprimés ; les en-têtes de tableau sont répétés sur plusieurs pages. L’enregistrement PDF nécessite l’action de l’utilisateur.

## Paiements et calculs

Chaque règlement est un événement réel. Acompte attendu = moitié du TTC arrondie au centime ; solde = TTC moins somme des paiements actifs. Un paiement partiel exceptionnel reste affiché comme tel et n’est jamais déclaré payé intégralement avant encaissement complet. Le montant saisi ne peut pas dépasser le reste dû.

Une correction annule logiquement l’ancien événement, avec date et motif, puis enregistre le montant corrigé. L’ancien reste consultable. Les dates réelle et informatique sont séparées ; une saisie tardive peut être antidatée à la date réelle, sans falsifier la date de saisie.

Les KPI séparent : potentiel HT des projets ouverts, ventes confirmées, facturation émise HT/TTC, encaissements réels et solde global. Une facture multiligne ou plusieurs paiements ne créent pas plusieurs ventes. Les annulations de facture sont exclues du facturé ; les encaissements déjà réels ne disparaissent pas avec l’annulation d’un document.

## Migration sans attribution arbitraire

Le magasin IndexedDB reste identique ; le schéma de contenu passe à 5. Les identifiants existants des clients, produits, opportunités, devis, factures et lignes restent stables.

Les anciens statuts explicitement comparables sont adaptés. Un ancien « Accepté », « Vente » ou « Clôturé » d’opportunité ne prouve pas les étapes du nouveau modèle : il est conservé dans `legacyStage` et signalé à vérifier. Une ancienne facture validée reste une facture ; aucune date de confirmation commerciale n’est déduite de sa date de facture.

Les documents non reliés à un projet reçoivent un dossier historique distinct. Sa date de premier contact et sa date de création d’origine restent inconnues ; `migratedAt` indique uniquement l’opération technique. Les coordonnées de plusieurs projets d’un même client ne suffisent pas à les fusionner.

L’ancien état « Payée » est conservé dans `legacyPaymentStatus`, avec un indicateur de rapprochement requis. Il ne devient pas un paiement fictif à une date inventée. Les sommes non vérifiées sont exclues des montants encaissés et du solde présenté comme certain. Le rapprochement demande un montant et une date réels, avec reconnaissance explicite de l’ancien état.

Les documents sans instantané complet d’origine sont signalés comme reconstitutions historiques. Ils restent accessibles, mais leur présentation n’est pas prétendue identique à l’original.

## Préservation générale

La traçabilité est masquée par défaut sans effacer les métadonnées. Les dates commerciales restent visibles. Les unités sont normalisées avec prudence ; les unités numériques anormales sont signalées, et les unités légitimes ne sont pas supprimées. Les documents historiques gardent leurs anciennes chaînes d’unité.

La démo utilise le modèle complet V5 et reste explicitement fictive, y compris sur les documents. La suppression tient compte des nouvelles relations afin de préserver les données réelles liées aux dossiers fictifs.
