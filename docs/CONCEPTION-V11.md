# Conception V11 — CRM local mono-agence

## Installation et migration

Chaque copie du HTML utilise une base IndexedDB locale `fmt-commercial`. Lors de la première ouverture sans agence configurée, un formulaire intégré recueille le nom, la ville facultative et le nom du poste facultatif. La configuration écrit atomiquement l’état métier et la fiche d’installation. Le nom normalisé en majuscules sans accents forme un slug ; trois octets aléatoires donnent un suffixe hexadécimal de six caractères. L’identifiant est généré une fois, puis demeure en lecture seule dans les Paramètres.

Une installation V10 déjà associée à `AG01`, `AG02`, `AG03` ou `AG04` garde cet identifiant, le même `installationId`, et ses enregistrements. Les données non encore associées à une agence attendent le formulaire initial. Les anciens instantanés Direction ne sont pas chargés ni effacés automatiquement. Le code de consolidation, les vues multi-agences et l’observation de l’interface propre à Direction sont supprimés.

`agencyId` reste inscrit dans les collections métier, les lignes et les documents figés. Un import de module exige l’identité de l’agence courante. Le JSON de module `fmt-commercial-module` version 1 contient agence, nom, poste, date, schéma, compteurs et collections liées. L’export commercial emporte les dossiers et leurs dépendances ; l’export de facturation part des ventes et emporte dossiers, clients, produits, devis, lignes, règlements et historiques correspondants. L’import compare les identifiants stables : un enregistrement identique est ignoré ; un identifiant présent avec un contenu différent reste local et est signalé comme conflit. Le graphe résultant est validé avant toute écriture atomique. Aucun numéro de document n’est réattribué.

Les JSON de module ne sont pas chiffrés : la sauvegarde complète chiffrée reste la méthode de reprise du poste. Son format V10 `fmt-agency-backup` version 1, son chiffrement PBKDF2/AES-GCM et le contrôle d’agence sont conservés. Aucun service réseau n’est utilisé par le CRM.

Dans Suivi commercial et Facturation, le bouton commun **Filtres** est replacé dans la barre de recherche. Le panneau utilise le même état de critères que les menus de colonnes, y compris en Kanban. Les exports CSV commerciaux portent sur les résultats filtrés et triés de l’onglet courant ; les règlements disposent aussi d’un CSV détaillé distinct.

Limite volontaire : un import de module ne remplace jamais un document existant divergent. Pour restaurer l’état complet d’une agence, utiliser la sauvegarde chiffrée après vérification du fichier et de la phrase secrète.
