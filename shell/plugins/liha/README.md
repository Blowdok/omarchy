# LIHA 0.1.0

Extension personnelle expérimentale du bureau Omarchy. Le panneau et son bouton de barre conservent les fonctions du bureau existant. Le clic droit du bouton ouvre les applications.

## Première utilisation

L’activation et les prérequis sont présentés dans le [README du dépôt](../../../README.md#variante-personnelle-liha--version-expérimentale-010). Le script `omarchy-setup-liha` exige une session Omarchy avec ses commandes système et son registre d’extensions Quickshell ; il n’installe pas un système Linux sur Windows.

- Exécuter `codex login` ou `grok login` dans un terminal et connecter l’abonnement existant. Aucune clé API n’est nécessaire ; aucun repli facturé n’est implémenté. Codex nécessite les options récentes `--ignore-user-config`, `--ephemeral` et `--output-schema` ; le client 0.153.0 a servi à l’essai réel.
- Ouvrir LIHA depuis la barre ou l’entrée LIHA dans les applications.
- Choisir un dossier de travail existant et précis, par exemple `~/Work/mon-projet` ; la racine système et le dossier personnel entier sont refusés.
- Choisir le fournisseur et le mode, puis écrire une demande. Le diagnostic indique si les composants sont installés ; l’authentification et les quotas se vérifient lors de la connexion et de l’appel réel.
- Le microphone transcrit une phrase dans le brouillon ; relire puis envoyer. La première dictée peut charger le modèle. La lecture des réponses est facultative et interruptible.

Grok reste à essayer avec un compte connecté : LIHA refuse les configurations Grok comportant hooks, extensions, commandes de connexion ou politiques imposées incompatibles avec ses autorisations. Ce refus est indiqué dans le diagnostic ; aucune configuration personnelle n’est supprimée automatiquement.

## Autorisations et observation

En mode approbation, LIHA montre une proposition complète et attend l’accord avant d’exécuter ces actions exactes. En accès complet, les actions ordinaires de lancement, fenêtres et fichiers s’exécutent directement dans le périmètre choisi ; les modifications de fichiers existants ont une sauvegarde.

Une commande libre demande toujours un accord : elle peut agir avec les droits de ton compte au-delà du dossier sélectionné. Il ne s’agit pas d’un accès administrateur permanent. Arrêter annule le raisonnement ou la commande en cours et empêche les étapes suivantes ; les applications déjà ouvertes et les fichiers déjà écrits restent disponibles.

Le journal présente les actions réelles et leur résultat. Le contrôle souris/clavier arbitraire et l’observation automatique par capture d’écran ne sont pas encore proposés. Les commandes s’exécutent en arrière-plan avec leur résultat dans le panneau ; les applications lancées s’affichent sur le bureau. La conversation reste en mémoire vive, sans enregistrement permanent par le moteur LIHA.

Les chemins cachés, liens symboliques, liens physiques multiples, secrets usuels et certains fichiers de configuration d’exécution sont exclus des outils de fichiers ; ce filtre réduit l’exposition accidentelle mais ne remplace pas le choix prudent du dossier. Ne fournir aucun secret dans la conversation. Le texte de la tâche et les résultats nécessaires partent vers le fournisseur choisi ; l’audio est traité localement.

## Voix gratuite

La préparation optionnelle installe un environnement Python utilisateur, Vosk, sounddevice/PortAudio, un modèle français vérifié par SHA-256 et eSpeak NG. Le microphone n’est ouvert que sur demande ; aucun service vocal distant n’est contacté.

La voix livrée est synthétique et basique : **ce n’est pas Vivienne HD**. La contrainte de gratuité est préservée. La dictée est limitée à 30 secondes et se termine après détection d’une phrase ou par arrêt ; Arrêter jette le texte en cours. La synthèse limite les réponses lues à 2 000 caractères.

## Essais pratiques sur Omarchy

- « Ouvre Blender et mon dossier dans VS Code » : vérifier les fenêtres et leur présence dans la liste Hyprland.
- « Crée bonjour.txt avec le texte Bonjour Boss » dans un dossier d’essai : vérifier le fichier, puis demander sa modification et retrouver la sauvegarde.
- « Liste les fichiers et résume le contenu de bonjour.txt » : vérifier la lecture réelle.
- « Exécute printf bonjour » : vérifier l’approbation de la commande, y compris en accès complet ; refuser une proposition et constater l’absence d’exécution.
- Dicter une phrase française, contrôler le brouillon et écouter la réponse ; arrêter une lecture puis en relancer une.
- Arrêter pendant une réponse IA et pendant une attente d’accord ; vérifier qu’aucune action suivante ne démarre.

Depuis le dépôt, les tests indépendants du bureau se lancent avec `python3 -m unittest discover -s shell/plugins/liha/backend/tests -p 'test_*.py'` ou `bash test/shell.d/liha-test.sh`.

Les [résultats et limites des vérifications](../../../docs/regles/verification-liha.md) distinguent l’essai réel Codex, les tests automatisés et le [harnais Qt](../../../test/shell.d/fixtures/liha/README.md), dont le transport Quickshell est simulé.

## Désactivation et mise à jour

`omarchy plugin disable blowvizion.liha` retire l’extension active sans remplacer tes configurations. Réactiver avec `omarchy plugin enable blowvizion.liha --section right`.

En activation depuis le clone, l’extension utilisateur est un lien vers ce clone : conserver son emplacement et sa branche. Une mise à jour du clone peut recharger l’interface ; arrêter les tâches avant de modifier ou mettre à jour son code. Le script conserve une sauvegarde s’il remplace un lanceur existant et refuse d’écraser une autre extension au même emplacement.
