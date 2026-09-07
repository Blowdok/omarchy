# RAD 0002 — LIHA comme extension conversationnelle d’Omarchy

- Date : 2026-09-07.
- Statut : retenu pour la première version expérimentale, selon l’autorisation de Blowdok d’appliquer les recommandations et d’implémenter sans nouveau questionnaire.

## Contexte

Blowdok souhaite améliorer Omarchy pour son usage personnel, conserver ses qualités et ajouter une assistante qui agit dans les applications par texte et voix. Le dépôt personnel `Blowdok/omarchy` existe déjà et conserve Omarchy comme dépôt `upstream`. L’environnement de développement actuel est Windows ; aucune session Omarchy, WSL ou machine virtuelle Linux n’est disponible.

## Décision

- Ajouter une extension QML `blowvizion.liha` dans le processus Quickshell existant, avec un panneau et un bouton de barre. Conserver les raccourcis, le menu et la disposition Omarchy.
- Exécuter le moteur Python dans un processus enfant séparé, relié uniquement par stdin/stdout JSON. Aucun serveur HTTP ni port réseau local ajouté.
- Séparer proposition et exécution : les fournisseurs retournent un plan JSON ; la politique locale valide ses outils et les autorisations avant toute action. Codex est appelé dans un dossier temporaire, en lecture seule, avec ses outils natifs désactivés et sa configuration utilisateur ignorée, tout en gardant son authentification par abonnement.
- Proposer deux modes. En approbation, les actions exactes d’une proposition sont présentées ensemble ; en accès complet, les actions ordinaires du catalogue sont exécutées dans le dossier choisi. Les commandes libres restent soumises à confirmation, car une expression régulière ne permet pas de garantir l’absence d’action destructive.
- Utiliser Vosk pour la transcription française locale et eSpeak NG pour une première synthèse gratuite. Vivienne HD reste souhaitée mais non intégrée faute de voie gratuite validée ; aucune dépendance Azure ou API vocale payante.
- Installer les personnalisations comme extension utilisateur réversible, depuis le clone ou le paquet de variante. Ne pas modifier les partitions ni le démarrage pendant le développement.

## Conséquences et limites

- Les abonnements IA restent nécessaires pour les fournisseurs choisis ; aucun repli vers une API facturée n’est effectué. Grok doit encore être validé avec un compte réel.
- La première version offre des actions de fichiers, fenêtres et lancement d’applications, ainsi que des commandes proposées avec approbation. Elle ne constitue pas encore un contrôle graphique universel de toutes les interfaces.
- Les actions, sorties et réponses sont visibles ; une commande en arrière-plan n’est pas présentée comme un clic à l’écran. La mémoire conversationnelle reste en RAM dans cette version.
- Les tests Python sont possibles sous Windows. Le rendu réel Quickshell/Hyprland, le microphone Linux, le son Linux et l’installation nécessitent une validation sur Omarchy avant de qualifier la variante d’opérationnelle.

## Sources techniques

- [Architecture Quickshell du dépôt](../../omarchy-shell.md).
- [Codex CLI](https://learn.chatgpt.com/docs/cli/reference) et [authentification](https://learn.chatgpt.com/docs/auth).
- [Grok en mode non interactif](https://docs.x.ai/build/cli/headless-scripting) et [options](https://docs.x.ai/build/cli/reference).
- [Modèles Vosk](https://alphacephei.com/vosk/models) et [eSpeak NG](https://github.com/espeak-ng/espeak-ng).
