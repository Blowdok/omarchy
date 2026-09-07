# Vérification des licences et de la provenance — LIHA V1

Vérification du 7 septembre 2026, limitée aux ajouts LIHA et à leur usage sur le poste personnel de Blowdok. Les guides IA Legol, Maître IA et propriété intellectuelle ont servi à organiser cette revue documentaire ; elle ne constitue pas une certification juridique globale du système.

## Conclusion pour cette version

Le développement personnel peut continuer avec la licence d'Omarchy conservée, les composants vocaux libres ci-dessous et les connexions officielles aux abonnements existants. La voix ne nécessite aucun service facturé. Les modèles Codex et Grok restent des services distants soumis aux droits, quotas et conditions du compte utilisé : LIHA ne doit pas être présenté comme un système IA entièrement gratuit ou entièrement hors ligne.

## Composants vérifiés

| Élément | Fait vérifié | Conséquence pour LIHA |
|---|---|---|
| Omarchy | Le fichier [LICENSE](../../LICENSE) contient la licence MIT et la mention de David Heinemeier Hansson. | Conserver ce fichier et les notices existantes dans le dépôt personnel et toute copie distribuée ; ne pas s'attribuer le code amont. |
| Vosk 0.3.45 | Le moteur est publié sous [Apache 2.0](https://github.com/alphacep/vosk-api/blob/master/COPYING) ; la [version Python choisie](https://pypi.org/project/vosk/0.3.45/) est épinglée dans les dépendances vocales. | Utilisation locale sans service facturé ; conserver les licences et notices applicables en cas de redistribution. |
| Modèle `vosk-model-small-fr-0.22` | Le [catalogue officiel](https://alphacephei.com/vosk/models) indique Apache 2.0 pour ce modèle français précis. | Télécharger ce modèle explicitement ; ne pas supposer que tous les autres modèles Vosk possèdent la même licence. |
| sounddevice 0.5.6 | La [licence du projet](https://github.com/spatialaudio/python-sounddevice/blob/master/LICENSE) est MIT. | Conserver copyright et licence si le composant est redistribué. |
| PortAudio | La [licence officielle](https://portaudio.com/license.html) permet l'utilisation, la modification et la distribution avec conservation de ses notices. | Dépendance audio système, installée séparément ; ne pas supprimer ses mentions. |
| eSpeak NG | Le [code officiel](https://github.com/espeak-ng/espeak-ng/blob/master/src/espeak-ng.c) annonce GPL version 3 ou ultérieure, avec le [texte de licence](https://github.com/espeak-ng/espeak-ng/blob/master/COPYING). | LIHA appelle le programme externe installé par le gestionnaire de paquets ; avant d'en intégrer des binaires dans une ISO distribuée, vérifier les obligations GPL, notamment l'accès au code source correspondant. |
| Vivienne / voix Microsoft | Microsoft documente Vivienne parmi les [voix HD d'Azure Speech](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/high-definition-voices). Aucun droit de transfert ou de redistribution d'un paquet Windows dans Linux n'a été établi par cette revue. | Aucun paquet Vivienne n'est extrait, copié ou distribué. La voix V1 est eSpeak NG français, synthétique et non HD. |

L'archive officielle du modèle français a été téléchargée dans un répertoire temporaire de vérification : 42 233 323 octets, SHA-256 `cabf6180e177eb9b3a9a9d43a437bd5e549f3a7d09525e5d69a3fed787be12ad`. Cette empreinte est épinglée dans `preparer_voix.py` ; elle identifie l'archive examinée, sans prétendre remplacer une signature de l'éditeur. Aucun modèle binaire n'est ajouté au dépôt.

## Abonnements et absence de frais supplémentaires

- **Codex** : la [documentation d'authentification](https://learn.chatgpt.com/docs/auth) distingue connexion ChatGPT et clé API facturée à l'usage. LIHA impose la connexion ChatGPT et ne configure aucune clé API ; les [quotas et crédits supplémentaires](https://learn.chatgpt.com/docs/pricing) restent ceux du compte. Les réglages de facturation et les droits réels de Blowdok n'ont pas été audités : l'absence d'API dans LIHA ne certifie pas les réglages de facturation d'un compte externe.
- **Grok** : l'[annonce officielle du 25 mai 2026](https://x.ai/news/grok-build-cli) propose Grok Build aux abonnés SuperGrok et X Premium Plus, avec un mode utilisable dans les scripts. Cela ne prouve ni l'accès du compte de Blowdok ni un droit de redistribution du client ou du service. Utiliser le client officiel et le compte personnel, sans achat ni activation d'API payante.
- **OpenRouter et Azure Speech** : aucun adaptateur payant ni achat automatique dans cette V1. Le téléchargement initial de Vosk nécessite Internet, puis la transcription et la lecture restent locales ; le texte envoyé à Codex ou Grok quitte cependant le poste.

## Limites avant une éventuelle distribution

Le nom **BV-LIHA — Linux Intelligent Hybride Autonome**, marque **BlowVizion**, est retenu pour le système ; **LIHA** reste son assistante. La notice DHH et le texte MIT sont conservés mot pour mot, avec attribution distincte des modifications propres à Blowdok. Le README explique l’origine et l’indépendance du projet ; [MARQUE.md](../../MARQUE.md) fixe sa présentation. La [page de marque Omarchy](https://omarchy.org/brand/) réserve les droits sur son identité : les références amont restent descriptives et ne constituent pas un aval. L’usage public du nom Linux est documenté par la [Linux Foundation](https://www.linuxfoundation.org/legal/the-linux-mark) ; aucune recherche de disponibilité juridique du nom BV-LIHA n’est revendiquée.

Cette revue couvre les composants directs ajoutés pour LIHA ; elle n'inventorie pas toutes leurs dépendances transitives, les paquets d'Omarchy, les polices, les ressources graphiques ou les conditions de VS Code, Blender et Unreal Engine. Avant une ISO publique ou une offre commerciale, réaliser cet inventaire sur les versions réellement empaquetées, vérifier les notices et sources à fournir, ainsi que les droits sur le nom et l'identité visuelle. Ne pas annoncer que tous les logiciels installables sont gratuits pour tout usage commercial.
