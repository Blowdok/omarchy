# Vérification de LIHA 0.1.0

Date : 2026-09-07. Résultat : première version expérimentale implémentée et vérifiée partiellement sur le poste Windows ; validation native Omarchy encore nécessaire. Aucune installation de système, modification des disques ou modification du démarrage n’a été réalisée.

## Vérifications réalisées

| Vérification | Résultat et portée |
| --- | --- |
| Tests Python du moteur, des fournisseurs et de la voix | 66 tests exécutés : 63 réussis, 3 ignorés sous Windows. Couverture des chemins, propositions, approbations, sauvegardes, annulation, protocoles fournisseurs, extraction du modèle et états vocaux. |
| Compilation Python | `compileall` réussit pour le moteur et le harnais Qt. |
| Scripts Bash | Analyse syntaxique individuelle des deux commandes LIHA, du lanceur Python et des deux tests shell réussie. |
| Métadonnées des commandes Omarchy | `omarchy commands --check` réussit sur 452 commandes, dont les ajouts LIHA. |
| Installation dans un environnement simulé | Six scénarios réussis : activation intégrée, réinstallation intégrée, préservation d’une cible différente, refus de sources concurrentes, découverte différée du registre, absence du registre avec attente bornée. Deux scénarios de liens symboliques sont présents mais ignorés faute de droits Windows. Aucun paquet réellement installé par ces tests. |
| Abonnement Codex réel | Client 0.153.0 connecté à ChatGPT ; le moteur reçoit une demande, obtient une proposition, crée réellement `bonjour-liha.txt` dans un dossier temporaire puis termine. Le test vérifie le contenu `Bonjour Boss` après retrait des espaces et retours périphériques ; aucun outil graphique n’est utilisé. |
| Interface Qt | Chargement du vrai panneau et des composants `Ui` / `Commons` avec PySide6 ; échanges avec Quickshell simulés. Souris, Ctrl + Entrée, approbation, arrêt, brouillon de dictée, indisponibilités et réouverture vérifiés. Cinq rendus inspectés, jusqu’à 580 × 680. |
| Modèle vocal | Archive française officielle téléchargée, empreinte contrôlée et extraction testée. Aucune voix Windows copiée. Voir la [revue des licences](verification-licences-liha.md). |
| Mémoire du projet | Sources capturées et compilées par agent-memo ; index local contrôlé avec son outil `generer-index.py --verifier`, code de sortie 0. Aucune publication de la mémoire. |

La suite amont `test/cli` a commencé sous Git Bash et validé les premiers contrôles de routage et de métadonnées, puis s’est arrêtée au lancement de `python3`, qui correspond ici à l’alias WindowsApps sans interpréteur utilisable. Elle n’est pas déclarée réussie ; les suites globales et l’acceptation graphique restent à exécuter dans l’environnement Linux prévu.

## Corrections issues de la vérification

- Le modèle ne peut exécuter ses outils natifs à la place des actions approuvées : options de confinement Codex contrôlées, outils Grok désactivés, configurations Grok à effets de bord refusées et variables d’API héritées filtrées.
- L’activation attend la découverte effective du registre et refuse deux sources concurrentes pour le même identifiant d’extension.
- La fermeture d’un processus parent ne termine pas forcément ses descendants ; l’arrêt et les délais restent actifs tant que les lecteurs de sortie attendent. Sous Linux, l’interruption vise le groupe de processus même si son parent a déjà quitté.
- Les remplacements de fichiers conservent une sauvegarde privée et les permissions originales ; une modification concurrente détectée annule le remplacement.
- Les dispositions Qt à taille minimale et la fermeture des fenêtres du harnais ont été corrigées ; aucun faux mouvement de souris n’est affiché pour une action exécutée en arrière-plan.

## Vérifications encore nécessaires

- Activer le panneau dans la vraie session Omarchy/Quickshell/Hyprland de cette branche ; contrôler son cycle de vie, le registre, les fenêtres, les commandes et les interactions souris/clavier.
- Exécuter les trois tests Python ignorés : deux cas de descendants fournisseurs spécifiques à POSIX et un cas de liens symboliques ; vérifier également les deux scénarios d’installation d’un clone lié.
- Tester microphone, transcription française, sortie audio, lecture et interruption sur Linux. Les tests simulés ne démontrent ni la compatibilité des périphériques ni la qualité vocale.
- Connecter réellement Grok et exécuter son scénario d’abonnement ; aucun succès d’authentification Grok n’est revendiqué.
- Exécuter les [scénarios pratiques](../../shell/plugins/liha/README.md#essais-pratiques-sur-omarchy) avant de déclarer le poste opérationnel.

## Reproduction

Depuis la racine du dépôt, avec Python 3.11 ou plus récent :

```bash
python3 -m unittest discover -s shell/plugins/liha/backend/tests -p 'test_*.py'
bash test/shell.d/liha-installation-test.sh
```

L’essai ci-dessous contacte explicitement le fournisseur connecté et consomme son quota d’abonnement ; il n’est pas inclus dans les tests automatiques :

```bash
python3 shell/plugins/liha/backend/tests/verifier_abonnement.py --fournisseur codex
```

Le [harnais Qt](../../test/shell.d/fixtures/liha/README.md) utilise un environnement Python temporaire avec PySide6. Il produit des captures et un rapport, sans ouvrir d’application utilisateur, contacter un fournisseur ni activer le microphone.
