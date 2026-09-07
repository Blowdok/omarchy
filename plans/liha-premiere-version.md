# LIHA — première version expérimentale

## Objectif

Ajouter une assistante personnelle à Omarchy sans remplacer son bureau : conversation française, saisie texte et dictée, réponse vocale, tâches observables et autorisations compréhensibles. Le cadrage détaillé reste dans [la vision](../docs/regles/vision-variante-personnelle.md) et les choix techniques dans le [RAD 0002](../docs/regles/decisions/0002-liha-extension-conversationnelle.md).

## Réalisation

- Panneau Quickshell et bouton de barre ; disponibilité des fournisseurs et de la voix explicitement affichée.
- Processus Python avec protocole JSON, arrêt concurrent, une tâche à la fois et boucle limitée à huit étapes.
- Adaptateur Codex vérifiable avec abonnement ; adaptateur Grok documenté, sans achat ni clé API automatique.
- Actions de fichiers limitées au dossier de travail choisi, sauvegarde avant remplacement, lancement d’applications et accès aux fenêtres Hyprland.
- Proposition et approbation des commandes libres avant exécution.
- Préparation vocale séparée : dépendances gratuites, modèle français local, microphone et synthèse interruptibles.
- Activation depuis un clone, sans copie destructive des configurations Omarchy.

## Critères de vérification

- Les outils inconnus, arguments inattendus, traversées de chemins et approbations forgées sont rejetés.
- Le mode complet exécute les actions ordinaires, tandis qu’une commande libre attend toujours une autorisation locale.
- Un arrêt pendant le raisonnement ou l’attente d’approbation ne lance aucune action supplémentaire.
- Les identifiants fournisseurs ne sont pas recopiés dans le dépôt et aucune clé API héritée ne déclenche de consommation.
- Les erreurs de client, de modèle vocal ou de session graphique manquante sont compréhensibles.
- Un échange réel Codex fournit un résultat conforme ; les essais Linux vérifient ensuite fenêtres, microphone, lecture vocale et comportement souris/clavier.

## Suite après les premières observations

- Piloter davantage d’actions Blender, Unreal Editor et audiovisuelles avec des intégrations dédiées.
- Ajouter observation visuelle et interaction graphique après validation du mécanisme de reprise en main.
- Améliorer la voix et le dialogue continu ; préserver le choix gratuit.
- Préparer l’ISO et le double démarrage sur le SSD Crucial après validation de la variante et préservation du contenu de D:.
