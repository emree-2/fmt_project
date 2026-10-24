# FMT — Espace commercial

Première version d’un CRM local pour une agence, avec le catalogue complet de `Test.xltx`.

## Utilisation

Ouvrir `index.html` dans un navigateur moderne autorisant JavaScript et IndexedDB. Aucune installation ni connexion réseau nécessaire. Les données commerciales démarrent vides ; les 3 283 lignes du catalogue sont intégrées. Commencer par **Clients → Nouveau client**, puis créer un devis ou une vente.

Les modifications sont conservées dans le navigateur, pas dans le fichier HTML. Faire régulièrement **Paramètres → Exporter JSON**. Conserver le même navigateur et le même emplacement du fichier ; exporter avant de déplacer le fichier ou de changer d’appareil. Les politiques de stockage des fichiers locaux dépendent du navigateur. Ne pas utiliser plusieurs onglets pour modifier simultanément la même base.

Pour une recette locale si les fichiers `file://` sont bloqués :

```sh
cd /workspace/fmt_project
python -m http.server 8765 --bind 127.0.0.1
```

Le serveur ne fait que servir le fichier ; l’application n’en dépend pas pour sa logique. Le stockage d’une origine HTTP est distinct de celui du fichier local : utiliser le JSON pour transférer les données.

## Conception

Voir [l’analyse des trois classeurs, le modèle, l’UX et les limites du prototype](docs/CONCEPTION.md) et [l’audit technique](docs/audit-classeurs.json).

## Recette de développement

Avec Playwright Python et Chromium installés, lancer le serveur local ci-dessus puis :

```sh
python tools/smoke_test.py
```

Le test utilise un contexte navigateur temporaire, sans toucher aux données d’un utilisateur.
