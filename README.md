# BV-LIHA

**Linux Intelligent Hybride Autonome**, le système personnel de la marque **BlowVizion**, avec **LIHA** comme assistante intégrée.

BV-LIHA est une variante indépendante fondée sur [Omarchy](https://omarchy.org), conçue d’abord pour le poste de travail de Blowdok.

## BV-LIHA — version expérimentale 0.1.0

BV-LIHA prépare le poste de travail personnel de Blowdok en ajoutant l’assistante LIHA au bureau issu d’Omarchy : conversation française, dictée et lecture locales, suivi des actions et modes approbation/accès complet. Le code combine QML/Quickshell et Python 3.11+, avec Codex ou Grok pour le raisonnement, Vosk pour la dictée et eSpeak NG pour la première voix gratuite.

Le cadrage vise l’absence de coût supplémentaire, en conservant les abonnements IA existants et en recherchant des composants vocaux gratuits.

Le français intégral est une exigence de la variante : interface, installation, notifications, aide, voix et réponses LIHA. Le panneau LIHA et sa consigne sont français ; la traduction des écrans et textes hérités d’Omarchy reste à réaliser et à vérifier avant validation du système. Les identifiants techniques imposés par les logiciels conservent leur syntaxe.

Les premières actions concernent les fichiers du projet, les fenêtres Hyprland, le lancement d’applications et les commandes explicitement approuvées. Le contrôle graphique universel, Vivienne HD et une ISO personnalisée ne sont pas encore fournis. Les essais natifs sous Omarchy restent nécessaires avant installation sur le SSD cible.

Sur une session Omarchy compatible avec le système d’extensions de cette branche, activer depuis le clone :

```bash
bash ./bin/omarchy-setup-liha --source "$PWD" --voix
```

Lire le [guide LIHA](shell/plugins/liha/README.md) pour les connexions, exemples pratiques, tests et limites ; la [vision](docs/regles/vision-variante-personnelle.md) conserve les besoins et le [plan](plans/liha-premiere-version.md) décrit la première version.

## Origine du projet

BV-LIHA est une œuvre dérivée d’Omarchy, projet créé par David Heinemeier Hansson. Les notices amont et la licence MIT sont conservées ; les modifications BV-LIHA relèvent de Blowdok sous la marque BlowVizion. Le projet est indépendant et ne revendique aucun aval d’Omarchy ni de ses auteurs. L’[identité du produit](docs/regles/decisions/0004-identite-bv-liha.md) distingue le système, sa marque et son assistante.

## Manuel du projet amont Omarchy

Le manuel de référence amont est conservé dans [`manual/`](manual/) et publié sur [le site documentaire Omarchy](https://learn.omacom.io/2/the-omarchy-manual), avec ses captures. Il décrit le socle technique ; sa traduction et son adaptation à BV-LIHA restent à réaliser.

- [Bienvenue dans Omarchy (projet amont)](manual/01-welcome-to-omarchy.md)

**Les bases**

- [Premiers pas](manual/02-getting-started.md)
- [Passer de Mac ou Windows](manual/03-coming-from-mac-or-windows.md)
- [Navigation](manual/04-navigation.md)
- [La barre supérieure](manual/05-the-top-bar.md)
- [Thèmes](manual/06-themes.md)
- [Raccourcis clavier](manual/07-hotkeys.md)
- [Presse-papiers et historique unifiés](manual/08-unified-clipboard-history.md)
- [Rappels](manual/09-reminders.md)
- [Notifications](manual/10-notices.md)
- [Extraction de texte et dictée](manual/11-text-extraction-dictation.md)
- [Captures et enregistrement](manual/12-screenshots-recording.md)
- [Options, inactivité et économiseur](manual/13-toggles-idle-screensaver.md)
- [Commandes Omarchy](manual/14-omarchy-cli.md)

**Les applications**

- [Terminal](manual/15-terminal.md)
- [Neovim](manual/16-neovim.md)
- [Intelligence artificielle](manual/17-ai.md)
- [Outils de développement](manual/18-development-tools.md)
- [Outils du terminal](manual/19-shell-tools.md)
- [Fonctions du terminal](manual/20-shell-functions.md)
- [Interfaces dans le terminal](manual/21-tuis.md)
- [Interfaces graphiques](manual/22-guis.md)
- [Navigateurs](manual/23-browsers.md)
- [Applications et services commerciaux](manual/24-commercial-apps-services.md)
- [Applications web](manual/25-web-apps.md)
- [Jeux](manual/26-gaming.md)
- [Remplir des PDF](manual/27-filling-out-pdfs.md)
- [Machine virtuelle Windows](manual/28-windows-vm.md)
- [Autres paquets](manual/29-other-packages.md)

**Configuration**

- [Mises à jour](manual/30-updates.md)
- [Fichiers de configuration](manual/31-dotfiles.md)
- [Extensions du bureau](manual/32-shell-plugins.md)
- [Écrans](manual/33-monitors.md)
- [Clavier, souris et pavé tactile](manual/34-keyboard-mouse-trackpad.md)
- [Réseau](manual/35-networking.md)
- [Mise en veille](manual/36-system-sleep.md)
- [Authentification matérielle](manual/37-hardware-authentication.md)
- [Polices](manual/38-fonts.md)
- [Fonds d’écran](manual/39-backgrounds.md)
- [Invite de commandes](manual/40-prompt.md)
- [Identité visuelle](manual/41-branding.md)
- [Personnalisations courantes](manual/42-common-tweaks.md)
- [Créer son thème](manual/43-making-your-own-theme.md)

**Pour aller plus loin**

- [Compatibilité Mac](manual/44-mac-support.md)
- [Dépannage](manual/45-troubleshooting.md)
- [FAQ](manual/46-faq.md)
- [Instantanés système](manual/47-system-snapshots.md)
- [Sécurité](manual/48-security.md)
- [Omarchy sur différents appareils](manual/49-omarchy-on.md)
- [Installation en double démarrage](manual/50-dual-boot-install.md)
- [Installations automatisées](manual/51-unattended-installs.md)

## Licence

Le code du projet est distribué sous la [licence MIT](LICENSE), avec conservation des attributions amont.
