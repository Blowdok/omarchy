# RAD 0004 — Identité BV-LIHA

- Date : 2026-09-07.
- Statut : retenu sur choix explicite de Blowdok.

## Identité

| Rôle | Nom retenu |
| --- | --- |
| Système | BV-LIHA |
| Développement de LIHA dans le nom du système | Linux Intelligent Hybride Autonome |
| Marque | BlowVizion |
| Assistante intégrée | LIHA |
| Socle technique et projet amont | Omarchy, Arch Linux, Hyprland et Quickshell |

Le nom exprime l’ambition du système ; il ne constitue pas la preuve d’un contrôle autonome universel. Le statut expérimental et les limites fonctionnelles documentées restent inchangés.

## Application technique

Le renommage concerne l’identité présentée à l’utilisateur : README, présentation du système, libellés de session et de démarrage, informations de thème, panneau LIHA et consigne commune aux fournisseurs. LIHA garde son nom et son identifiant `blowvizion.liha` ; les versions de l’assistante et du socle ne sont pas confondues.

Une identité typographique originale BV-LIHA remplace les logos principaux du dépôt, de l’économiseur, de l’écran d’information, de SDDM et de Plymouth ; les exports sont reproductibles avec `scripts/generer-identite-bv-liha.py`. Le bouton de menu porte le monogramme textuel BV. Les thèmes facultatifs et illustrations de documentation amont conservent leur provenance et demandent une sélection explicite pour l’image finale.

Les commandes `omarchy-*`, variables `OMARCHY_*`, chemins de configuration, identifiants des extensions, noms de paquets, sources et URL amont sont des contrats techniques ou des références de provenance, conservés pour compatibilité. Le dépôt GitHub existant reste `Blowdok/omarchy` et la branche `liha-premiere-version` ; aucune nouvelle adresse distante n’est inventée. Les titres de fenêtre couplés aux règles Hyprland demandent une modification coordonnée avant de pouvoir être renommés.

La compétence `agents/skills/renommage-marque/SKILL.md` organise le renommage ciblé et la préservation des références externes. Son retour d’expérience « Traduire le lot après l’avoir renommé » prévoit une traduction distincte, mais ses scripts ne traduisent pas automatiquement les interfaces. Leur configuration d’exemple vise d’autres projets ; aucune substitution globale Omarchy → BV-LIHA ou LIHA → BV-LIHA n’est appliquée.

## Français et provenance

Le [RAD 0003](0003-francais-systeme-et-liha.md) reste applicable : l’ensemble du système doit être en français, et LIHA répond en français. Le changement de marque ne prouve ni la traduction des écrans amont ni celle des applications tierces.

Les notices et le texte MIT amont sont conservés. Les ajouts BV-LIHA reçoivent une attribution distincte, limitée à ces modifications ; Omarchy reste cité comme origine du projet, sans revendication d’aval. Les ressources historiques et les noms des logiciels tiers ne deviennent pas des créations BlowVizion par simple renommage.

## Validation et limites de livraison

Vérifier les libellés, les liens documentaires, les identifiants techniques préservés et le rendu du panneau LIHA. La session Windows permet les tests Python et le harnais Qt, mais pas le contrôle natif de SDDM, Plymouth, Limine et Hyprland. Le paquet `omarchy-settings`, les PKGBUILD et l’orchestration ISO vivent hors de ce dépôt : leurs métadonnées et la langue système seront à intégrer dans la future image BV-LIHA. Modifier le clone ne change ni les fichiers déjà installés ni le démarrage du PC.
