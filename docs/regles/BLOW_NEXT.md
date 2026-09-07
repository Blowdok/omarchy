# Continuité du projet LIHA

Mise à jour : 2026-09-07. Lire ce fichier au début de chaque session.

## État actuel

LIHA 0.1.0 est une extension expérimentale implémentée sur Omarchy quattro, version amont 4.0.0.alpha. Dépôt personnel : https://github.com/Blowdok/omarchy ; branche de travail : `liha-premiere-version`. L’origine amont reste https://github.com/omacom/omarchy.

Blowdok a demandé d’appliquer les recommandations et d’implémenter directement sans nouvelle question. L’objectif reste son poste de travail personnel, puis une distribution éventuelle. Aucune installation Linux ni modification des disques ou du démarrage Windows n’a été effectuée.

Exigence rappelée explicitement par Blowdok : le système doit être totalement en français, et LIHA doit répondre en français. Cela couvre interfaces, installation, menus, notifications, aide, voix, confirmations et comptes rendus. La consigne commune Codex/Grok a été renforcée ; la traduction complète d’Omarchy n’est pas encore réalisée. Voir le [RAD 0003](decisions/0003-francais-systeme-et-liha.md).

## Résultat et vérifications

- Extension Quickshell : conversation, bouton dans la barre, accès aux applications, modes approbation/accès complet, activité réelle et arrêt.
- Moteur Python : fournisseurs Codex/Grok par abonnement, validation indépendante du modèle, fichiers du dossier choisi, sauvegardes, fenêtres et applications. Les commandes libres demandent toujours un accord.
- Voix locale : transcription Vosk française et synthèse eSpeak NG basique ; Vivienne HD n’est pas intégrée, aucun service vocal payant ajouté.
- Un essai réel Codex via ChatGPT a créé un fichier dans un dossier temporaire. Les tests Qt utilisent les composants visuels réels avec un transport Quickshell simulé ; ils ne valident pas Wayland.
- Les résultats exacts et les limites sont dans [le rapport de vérification](verification-liha.md). L’extension n’est pas déclarée opérationnelle sous Linux avant ces essais.
- L’observation de l’écran et le contrôle graphique général, les intégrations métier Blender/Unreal et l’ISO restent à développer.

## Installation cible connue

D: est la partition 2 du SSD Crucial CT500BX500SSD1, disque physique Windows 0, environ 466 Gio ; il contient `Sauvegarde-LIHA`, à préserver. Windows et son démarrage EFI sont sur le SSD Samsung 860 QVO 1TB, disque Windows 1, environ 932 Gio. Réidentifier les disques sous Linux par modèle et capacité, jamais par une correspondance supposée avec les numéros Windows.

Matériel observé : Intel Core i3-10100, 16 Gio de mémoire, Radeon RX 570, démarrage UEFI. Les états BitLocker et Secure Boot restent inconnus : les lectures ont été refusées faute de privilèges. Aucun environnement Linux ou VM prêt n’est disponible dans cette session Windows.

## Reprise du travail

- Réaliser la francisation complète et l’inclure dans la validation : langue système française générée, menus et panneaux hérités traduits, applications configurées en français. Préserver les commandes techniques, le clavier choisi et le fuseau horaire.
- Lire le [guide LIHA](../../shell/plugins/liha/README.md), puis terminer les essais natifs dans une session Omarchy compatible avec cette branche.
- Vérifier ouverture et activation des applications, dictée, lecture, permissions et arrêt de groupes de processus sous Linux.
- Tester Grok avec un abonnement réellement connecté ; aucun essai Grok authentifié n’a été réalisé.
- Corriger les observations avant de préparer l’ISO et le double démarrage ; l’effacement ou le partitionnement nécessite la confirmation explicite prévue par les règles utilisateur.
- Conserver les nombreux fichiers de compétences importés par Blowdok et la modification préexistante de `.gitignore` ; ils ne font pas partie de la livraison LIHA.

## Décisions et mémoire

- [Vision du poste personnel](vision-variante-personnelle.md).
- [Plan de première version](../../plans/liha-premiere-version.md).
- [Architecture](architecture.md) et [RAD 0002](decisions/0002-liha-extension-conversationnelle.md).
- [Vérification des licences](verification-licences-liha.md).
- Ingestion effectuée par agent-memo dans la mémoire locale : projet `wiki/blowdok/projets/omarchy/projet.md`, décision `poste-personnel-et-gratuite.md` et session `wiki/liha/sessions/2026-09-07/22-46-omarchy-premiere-version.md`. Sources capturées, index vérifié ; aucune publication de la mémoire.
