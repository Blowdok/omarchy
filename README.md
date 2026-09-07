# Omarchy

Omarchy is a beautiful, fun & agentic Linux distribution by DHH.

Read more at [omarchy.org](https://omarchy.org).

## Variante personnelle LIHA — version expérimentale 0.1.0

Cette variante prépare le poste de travail personnel de Blowdok en ajoutant une extension LIHA au bureau Omarchy : conversation française, dictée et lecture locales, suivi des actions et modes approbation/accès complet. Le code combine QML/Quickshell et Python 3.11+, avec Codex ou Grok pour le raisonnement, Vosk pour la dictée et eSpeak NG pour la première voix gratuite.

Le cadrage vise l’absence de coût supplémentaire, en conservant les abonnements IA existants et en recherchant des composants vocaux gratuits.

Le français intégral est une exigence de la variante : interface, installation, notifications, aide, voix et réponses LIHA. Le panneau LIHA et sa consigne sont français ; la traduction des écrans et textes hérités d’Omarchy reste à réaliser et à vérifier avant validation du système. Les identifiants techniques imposés par les logiciels conservent leur syntaxe.

Les premières actions concernent les fichiers du projet, les fenêtres Hyprland, le lancement d’applications et les commandes explicitement approuvées. Le contrôle graphique universel, Vivienne HD et une ISO personnalisée ne sont pas encore fournis. Les essais natifs sous Omarchy restent nécessaires avant installation sur le SSD cible.

Sur une session Omarchy compatible avec le système d’extensions de cette branche, activer depuis le clone :

```bash
bash ./bin/omarchy-setup-liha --source "$PWD" --voix
```

Lire le [guide LIHA](shell/plugins/liha/README.md) pour les connexions, exemples pratiques, tests et limites ; la [vision](docs/regles/vision-variante-personnelle.md) conserve les besoins et le [plan](plans/liha-premiere-version.md) décrit la première version.

## The Omarchy Manual

The manual lives in [`manual/`](manual/), which is its authoritative source. It's
mirrored to [learn.omacom.io](https://learn.omacom.io/2/the-omarchy-manual), where
its screenshots are also hosted.

- [Welcome to Omarchy!](manual/01-welcome-to-omarchy.md)

**The Basics**

- [Getting Started](manual/02-getting-started.md)
- [Coming From Mac or Windows](manual/03-coming-from-mac-or-windows.md)
- [Navigation](manual/04-navigation.md)
- [The top bar](manual/05-the-top-bar.md)
- [Themes](manual/06-themes.md)
- [Hotkeys](manual/07-hotkeys.md)
- [Unified Clipboard & History](manual/08-unified-clipboard-history.md)
- [Reminders](manual/09-reminders.md)
- [Notices](manual/10-notices.md)
- [Text Extraction & Dictation](manual/11-text-extraction-dictation.md)
- [Screenshots & Recording](manual/12-screenshots-recording.md)
- [Toggles, idle & screensaver](manual/13-toggles-idle-screensaver.md)
- [Omarchy CLI](manual/14-omarchy-cli.md)

**The Applications**

- [Terminal](manual/15-terminal.md)
- [Neovim](manual/16-neovim.md)
- [AI](manual/17-ai.md)
- [Development Tools](manual/18-development-tools.md)
- [Shell Tools](manual/19-shell-tools.md)
- [Shell Functions](manual/20-shell-functions.md)
- [TUIs](manual/21-tuis.md)
- [GUIs](manual/22-guis.md)
- [Browsers](manual/23-browsers.md)
- [Commercial apps/services](manual/24-commercial-apps-services.md)
- [Web Apps](manual/25-web-apps.md)
- [Gaming](manual/26-gaming.md)
- [Filling out PDFs](manual/27-filling-out-pdfs.md)
- [Windows VM](manual/28-windows-vm.md)
- [Other Packages](manual/29-other-packages.md)

**Configuration**

- [Updates](manual/30-updates.md)
- [Dotfiles](manual/31-dotfiles.md)
- [Shell plugins](manual/32-shell-plugins.md)
- [Monitors](manual/33-monitors.md)
- [Keyboard, Mouse, Trackpad](manual/34-keyboard-mouse-trackpad.md)
- [Networking](manual/35-networking.md)
- [System sleep](manual/36-system-sleep.md)
- [Hardware authentication](manual/37-hardware-authentication.md)
- [Fonts](manual/38-fonts.md)
- [Backgrounds](manual/39-backgrounds.md)
- [Prompt](manual/40-prompt.md)
- [Branding](manual/41-branding.md)
- [Common tweaks](manual/42-common-tweaks.md)
- [Making your own theme](manual/43-making-your-own-theme.md)

**The Rest**

- [Mac support](manual/44-mac-support.md)
- [Troubleshooting](manual/45-troubleshooting.md)
- [FAQ](manual/46-faq.md)
- [System snapshots](manual/47-system-snapshots.md)
- [Security](manual/48-security.md)
- [Omarchy on...](manual/49-omarchy-on.md)
- [Dual Boot Install](manual/50-dual-boot-install.md)
- [Unattended Installs](manual/51-unattended-installs.md)

## License

Omarchy is released under the [MIT License](https://opensource.org/licenses/MIT).
