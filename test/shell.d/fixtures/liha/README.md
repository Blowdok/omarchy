# Vérification Qt de LIHA

`verifier_interface.py` charge le véritable `Panel.qml` et les composants `Ui` / `Commons` du dépôt dans Qt. Il remplace uniquement les interfaces Quickshell de fenêtre, de processus et de fichiers par des doublures temporaires : aucune commande système, aucun fournisseur IA et aucun microphone ne sont activés. Ce contrôle facultatif ne remplace pas la [vérification dans Omarchy sous Wayland](../../../../agents/skills/visual-verification.md).

Dans un environnement Python isolé contenant `PySide6-Essentials`, depuis la racine du dépôt :

```bash
python test/shell.d/fixtures/liha/verifier_interface.py --sortie /tmp/liha-interface
```

Sous Windows, utilise le Python de ton environnement isolé et choisis un dossier de sortie temporaire avec `--sortie`. Le script charge Consolas si cette police système est présente ; les couleurs et dimensions restent celles des composants Omarchy.

Le contrôle vérifie l'approbation à la souris, l'envoi avec Ctrl + Entrée, l'arrêt d'une tâche, la conservation de la dictée en brouillon, la désactivation des composants absents et la réouverture de la conversation. Toute assertion échouée ou tout dépassement de dix secondes produit un code de sortie non nul.

Inspecte ensuite les cinq captures PNG : accueil, conversation, approbation, approbation à la taille minimale et erreur à la taille minimale. Vérifie la lisibilité, les retours à la ligne, les boutons d'arrêt et d'approbation et l'absence de chevauchement. `rapport.json` rappelle les limites de ce contrôle ; les captures représentent des données de test et ne prouvent pas l'exécution d'une tâche réelle.
