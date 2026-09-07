# RAD 0003 — Français pour le système et LIHA

- Date : 2026-09-07.
- Statut : exigence retenue sur instruction explicite de Blowdok ; réalisation partielle, traduction du socle à poursuivre.

## Décision

Toute l’expérience destinée à Blowdok doit être en français : installation, bureau, menus, réglages, notifications, aide, messages d’erreur, interaction vocale et réponses LIHA. La consigne commune aux fournisseurs impose également des confirmations, explications et comptes rendus français lorsque leurs sources sont dans une autre langue.

Les noms de produits, chemins, commandes, formats et clés imposés par les outils externes gardent leur orthographe nécessaire au fonctionnement. Une sortie technique originale peut être conservée pour diagnostic ; son explication destinée à l’utilisateur doit être française.

La préparation du système devra générer et sélectionner une locale française UTF-8 avant de l’utiliser. La langue ne doit pas modifier implicitement la disposition du clavier ou le fuseau horaire. Les usages ponctuels de `LC_ALL=C` nécessaires à l’analyse de sorties techniques sont conservés ; ils ne constituent pas la langue de l’interface.

## État constaté dans le dépôt

- Le panneau LIHA, ses messages propres et la voix locale sont prévus en français ; la consigne de réponse est renforcée dans `shell/plugins/liha/backend/fournisseurs.py`.
- `default/bash/envs` lit la locale système de `/etc/locale.conf` ; définir une variable de langue ne génère pas les données de cette locale et ne traduit pas des textes codés en dur.
- `default/omarchy/omarchy-menu.jsonc` contient encore des libellés anglais ; `shell/plugins/panels/clock/Panel.qml` utilise explicitement une locale anglaise pour son calendrier.
- `shell/plugins/panels/weather/Panel.qml` demande des descriptions météo en anglais ; les panneaux audio et batterie possèdent aussi des libellés anglais codés en dur.
- Les formulaires de `install/provisioning/setup-form.sh`, d’autres panneaux et commandes conservent des textes amont anglais.
- Les lanceurs de `applications/` et les applications tierces demandent une vérification propre : le script d’installation VS Code ne prépare pas de pack français et la liste de paquets LibreOffice ne déclare pas son paquet linguistique français.
- L’ISO orchestre l’installation hors de ce dépôt : sa francisation doit aussi être prise en compte lors de sa préparation.

## Validation attendue

Sur la session Omarchy réelle, parcourir l’installation, les menus, les réglages, les notifications, l’aide et les applications retenues ; vérifier dates et nombres, saisie des accents, dictée, lecture et réponses LIHA à partir de documents français ou anglais. Recenser les écrans restant en anglais, notamment dans les logiciels tiers, et les traiter explicitement avant de déclarer la variante totalement française. Aucune configuration régionale du Windows actuel n’a été changée.
