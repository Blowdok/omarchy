# Variante personnelle d’Omarchy : réflexion initiale

Date : 2026-09-07. Phase : première version LIHA 0.1.0 implémentée, validation native Linux à effectuer. Dépôt personnel : Blowdok/omarchy, branche liha-premiere-version. Le [plan](../../plans/liha-premiere-version.md), l’[architecture](architecture.md) et le [rapport de vérification](verification-liha.md) décrivent le résultat concret.

## Intentions exprimées par Blowdok

- Construire son poste de travail personnel idéal à partir d’Omarchy ; envisager une distribution à d’autres utilisateurs ultérieurement.
- Suivre le cycle brainstorm, plan, développement, vérification, tests et validation ou corrections.
- Intégrer une IA capable d’agir dans tout l’environnement ; le périmètre concret et les capacités devront être établis par des essais, sans promettre une capacité universelle.
- Permettre l’utilisation naturelle de la souris, avec les habitudes Windows ou macOS, tout en conservant le clavier ; préférence exprimée pour une coexistence immédiate plutôt qu’un changement de mode obligatoire.
- Privilégier Codex et Grok via abonnement, puis OpenRouter pour l’accès par API.
- Contrainte suivante de Blowdok : éviter tout ce qui est payant. Recommandation retenue pour cette version : utiliser les abonnements déjà détenus sans ajouter de service vocal ni d’API facturée. Aucun achat de crédits ou repli payant n’est implémenté ; les paramètres de facturation du compte fournisseur restent extérieurs à LIHA. OpenRouter sort du périmètre initial.
- Texte et voix dès la première version, avec un échange conversationnel permettant de déléguer des tâches complètes.
- Préférence vocale confirmée : Vivienne, parmi les nouvelles voix HD de son Windows 11 Pro ; disponibilité dans la variante Linux non validée. Le choix de la voix ne vaut pas approbation d’un service Azure, de frais supplémentaires ou d’un transfert distant du texte.
- La contrainte de gratuité prime sur la préférence Vivienne : Vosk français et eSpeak NG constituent la première implémentation locale. La qualité de la voix basique ne correspond pas à Vivienne HD ; l’essai microphone et haut-parleur sous Linux reste nécessaire.
- Préserver ce qui fonctionne bien dans Omarchy et l’améliorer ; éviter les régressions.
- Voir les actions réelles se dérouler à l’écran comme si Blowdok travaillait lui-même.
- Proposer deux modes : accès complet et demande d’approbation, en limitant les interruptions ; conserver la confirmation avant les opérations destructives.
- Couverture applicative souhaitée : outils variés, notamment Visual Studio Code, terminaux, Blender, Unreal Engine et applications audio/vidéo ; logiciels audiovisuels précis et tâches représentatives à identifier. Le besoin est généraliste et extensible.
- Installation cible choisie : disque actuellement D: de la machine Windows de Blowdok, avec choix Windows ou variante Omarchy au démarrage. Cette intention ne vaut pas confirmation d’un effacement immédiat ; le cycle de conception, développement, tests et validation reste en cours.

## Installation cible : constat du 2026-09-07

- Lecture seule de Windows : D: correspond à la partition 2 du disque physique 0, modèle CT500BX500SSD1, environ 466 Gio, GPT ; volume NTFS nommé BlowVizion avec environ 465 Gio libres.
- Windows C: réside sur un autre disque physique, numéro 1, Samsung SSD 860 QVO 1TB, environ 932 Gio ; sa partition système EFI se trouve également sur ce disque. Démarrage UEFI constaté.
- D: n’est pas entièrement vide : le dossier `Sauvegarde-LIHA` est présent, en plus des dossiers système. Vérifier et préserver son contenu avant toute opération destructive.
- Les identifiants de disque Windows ne doivent pas être assimilés aux noms Linux ; réidentifier le disque par modèle et capacité dans l’installateur.
- Les lectures BitLocker et Secure Boot ont échoué pour manque de privilèges ; leur état est inconnu, aucune conclusion d’absence de chiffrement ne doit être tirée des erreurs secondaires.
- Proposition pour le plan : installation Linux et partition EFI propres sur le disque cible, puis menu proposant les deux systèmes, à vérifier sur l’installateur retenu. Documentation de référence : https://omarchy.org/manual/dual-boot-install/.
- Aucun formatage, repartitionnement, changement du démarrage ou installation effectué.

## Vérifications documentaires

- Le dépôt possède déjà des lanceurs Codex et Grok dans `bin/omarchy-agent` et leur préparation dans `install/user/mise.sh` ; cela ne constitue pas à lui seul un contrôle graphique complet du système.
- Codex permet une connexion ChatGPT pour l’accès par abonnement : https://learn.chatgpt.com/docs/auth.
- Codex App Server fournit une interface d’intégration pour une application personnelle, avec authentification, conversations, validations et événements : https://learn.chatgpt.com/docs/app-server.
- xAI annonce Grok Build accessible aux abonnés SuperGrok et X Premium Plus : https://x.ai/news/grok-build-cli ; une connexion par abonnement dans OpenCode est également documentée : https://x.ai/news/grok-opencode.
- OpenRouter expose une API authentifiée par clé : https://openrouter.ai/docs/quickstart.
- Un essai complet avec le compte ChatGPT connecté à Codex a depuis créé un fichier via le moteur LIHA. L’accès Grok du compte et les quotas restent à vérifier ; les tests simulés ne démontrent pas une authentification réelle.
- Voix Microsoft : le Narrateur propose des voix naturelles sous Windows (https://support.microsoft.com/en-us/accessibility/windows/narrator/appendix-a-supported-languages-and-voices) ; aucune méthode officielle de réutilisation directe de ces paquets sous Linux n’a été établie dans cette recherche. Azure Speech propose séparément des voix HD, dont Vivienne et Rémy, via un service distant (https://learn.microsoft.com/en-us/azure/ai-services/speech-service/high-definition-voices), utilisable depuis Linux (https://learn.microsoft.com/en-us/azure/ai-services/speech-service/get-started-text-to-speech). Ce service n’est pas une réutilisation automatique de la licence Windows et ne constitue pas un choix approuvé par Blowdok.

## Pistes du cadrage initial

Ces pistes conservent l’ambition à terme ; elles ne constituent pas une liste de fonctions toutes livrées. Blowdok a ensuite demandé d’appliquer les recommandations et d’implémenter sans nouvelle question ; les choix de la première version sont fixés dans le RAD 0002.

- Un panneau LIHA intégré au bureau pour donner une tâche, suivre son exécution et l’interrompre.
- Des accès cliquables aux applications, fenêtres, espaces de travail et réglages, tout en gardant les raccourcis Omarchy.
- Des outils système et applicatifs communs aux fournisseurs, complétés par le contrôle graphique quand nécessaire ; architecture encore à déterminer.
- Une autonomie pour les tâches autorisées, un historique des actions sans secrets et une confirmation avant les opérations destructives ou irréversibles, conformément aux instructions de Blowdok.
- Premier scénario de démonstration proposé : demander à LIHA de préparer un espace de travail et ouvrir les applications utiles, puis vérifier le résultat à la souris et au clavier.
- Étendre Omarchy par des composants désactivables et des personnalisations ciblées ; garder le bureau utilisable lorsque LIHA est arrêtée ou hors connexion.
- Un espace de travail LIHA visible, avec reprise manuelle et arrêt immédiat accessibles à la souris et au clavier ; commande vocale d’arrêt complémentaire.
- En mode approbation, valider un ensemble d’actions compréhensible puis laisser LIHA l’exécuter ; redemander si le périmètre change. En accès complet, exécuter les tâches demandées sans interruptions ordinaires, avec maintien des confirmations destructives ; portée et durée des autorisations à préciser.
- Afficher les opérations réellement effectuées : applications manipulées, fichiers modifiés et résultats ; montrer une activité explicite pour les tâches exécutées par commande ou interface de programmation, sans simuler des clics.
- Conversation vocale activable par bouton, puis échange continu tant que la session est ouverte, état du microphone visible et possibilité d’interrompre la réponse ; transcription et synthèse françaises à évaluer séparément des abonnements de raisonnement.
- Conserver une mémoire consultable et corrigeable des préférences et procédures, ainsi qu’une reprise des tâches interrompues après vérification de leur état réel.
- Prévoir des sauvegardes et un retour arrière pour les modifications réversibles ; ne pas présenter un envoi externe ou une autre action irréversible comme annulable.
- Associer le contrôle graphique général à des intégrations propres aux applications lorsqu’elles offrent des commandes, scripts ou extensions ; conserver les résultats visibles et vérifier l’état réel après chaque tâche.
- Construire la première démonstration avec VS Code, un terminal et Blender, puis étendre les essais à Unreal Editor et à une application audiovisuelle choisie ; ordre proposé, non validé. L’automatisation Python documentée par Epic concerne l’éditeur Unreal et ne constitue pas un contrôle du jeu en cours : https://dev.epicgames.com/documentation/en-us/unreal-engine/scripting-the-unreal-editor-using-python.

## Suite après la première version

- Évaluer la transcription et la synthèse gratuites sur le matériel réel ; améliorer la qualité vocale après cet essai.
- Exécuter les scénarios pratiques du guide LIHA dans une session Omarchy compatible.
- Vérifier l’intégration des fenêtres, l’usage souris/clavier et la reprise manuelle sous Hyprland.
- Préparer l’environnement de test Linux et, après validation, l’installation sur le disque cible en préservant les données existantes.

Le dépôt personnel existe et la première extension est implémentée. Aucune installation de Linux, modification des partitions ou modification du démarrage Windows n’a été effectuée.
