# Architecture de BV-LIHA

## Vue d'ensemble

BV-LIHA (Linux Intelligent Hybride Autonome), sous la marque BlowVizion, conserve Arch Linux, Hyprland et le bureau Quickshell d’Omarchy. LIHA est son assistante intégrée : sa version 0.1.0 ajoute une extension utilisateur ou embarquée, sans nouvelle session graphique ni serveur réseau local.

## Principes

- Le bureau existant continue à fonctionner lorsque LIHA est arrêtée.
- Le modèle propose ; le moteur local valide, demande l’accord requis et exécute.
- Les actions ordinaires du mode complet restent bornées au catalogue et au dossier choisi ; les commandes libres sont explicitement approuvées.
- Aucune API payante de secours ; voix locale gratuite, sans prétendre intégrer Vivienne HD.
- Le français est la langue de l’expérience utilisateur entière et des réponses LIHA ; les textes hérités d’Omarchy restent à traduire. La configuration linguistique doit préserver les identifiants techniques, le clavier et le fuseau choisis.

## Modules

| Emplacement | Responsabilité |
| --- | --- |
| `shell/plugins/liha/Panel.qml` | Conversation, dictée, lecture, modes et approbations |
| `shell/plugins/liha/Widget.qml` | Accès cliquable à LIHA et aux applications |
| `shell/plugins/liha/backend/moteur.py` | Protocole JSONL, boucle de tâches, historique en RAM et annulation |
| `shell/plugins/liha/backend/politique.py` | Validation des propositions, chemins et autorisations |
| `shell/plugins/liha/backend/actions.py` | Actions réelles sur fichiers, fenêtres, applications et commandes approuvées |
| `shell/plugins/liha/backend/fournisseurs.py` | Connexions aux clients Codex et Grok par abonnement |
| `shell/plugins/liha/backend/voix.py` | Transcription Vosk et synthèse eSpeak NG locales |
| `bin/omarchy-setup-liha` | Activation réversible et préparation vocale optionnelle |

Le panneau échange avec son processus enfant par stdin/stdout JSON, sans port ouvert. Les composants vocaux sont installés dans un environnement Python utilisateur séparé ; le modèle français est téléchargé uniquement par la préparation explicite.

## Décisions

Toute décision structurante est consignée dans `docs\regles\decisions\` au format RAD.

- [RAD 0002 — Extension conversationnelle LIHA](decisions/0002-liha-extension-conversationnelle.md).
- [RAD 0003 — Français pour le système et LIHA](decisions/0003-francais-systeme-et-liha.md).
- [RAD 0004 — Identité BV-LIHA](decisions/0004-identite-bv-liha.md).
