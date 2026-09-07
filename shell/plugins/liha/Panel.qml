pragma ComponentBehavior: Bound
import QtQuick
import QtQuick.Layouts
import QtQuick.Controls as Controls
import Quickshell
import Quickshell.Io
import qs.Commons
import qs.Ui as Ui

Item {
  id: root

  property string omarchyPath: Quickshell.env("OMARCHY_PATH")
  property var shell: null
  property var manifest: null
  property var pluginRegistry: null
  readonly property bool opened: fenetre.visible
  property bool fermetureHote: false
  property bool pret: false
  property bool occupe: false
  property bool approbationAttendue: false
  property bool lecture: false
  property string activite: "repos"
  property string fournisseur: "codex"
  property string mode: "approbation"
  property string erreur: ""
  property string derniereReponse: ""
  property string raisonApprobation: ""
  property string actionsApprobation: ""
  property string onglet: "conversation"
  property bool reglages: true
  property bool reglagesVoix: false
  property bool lectureAutomatique: false
  property var fournisseurs: ({})
  property var voix: ({ dictee: false, synthese: false, detail: "Vérification des composants vocaux…", nom_voix: "" })
  property int numeroRequete: 0
  readonly property color secondaire: Qt.alpha(Color.foreground, 0.68)
  readonly property bool dicteeEnCours: activite === "dictee"
  readonly property bool fournisseurDisponible: fournisseurs[fournisseur] !== undefined && fournisseurs[fournisseur].disponible === true
  readonly property string statut: !pret ? (moteur.running ? "Connexion au moteur" : "Moteur arrêté") : approbationAttendue ? "Ton accord est attendu" : dicteeEnCours ? "Microphone actif" : occupe ? "Tâche en cours" : lecture ? "Lecture vocale" : "Prête à recevoir ta demande"

  function open(payloadJson) {
    fermetureHote = false
    fenetre.visible = true
    if (!moteur.running) demarrer()
    else requete("etat", {})
    Qt.callLater(function() { saisie.forceActiveFocus() })
  }

  function close() {
    fermetureHote = true
    fenetre.visible = false
    fermetureHote = false
  }

  function fermer() {
    if (shell && typeof shell.hide === "function") shell.hide("blowvizion.liha")
    else close()
  }

  function demarrer() {
    erreur = ""
    pret = false
    delaiDemarrage.restart()
    moteur.running = true
  }

  function requete(methode, parametres) {
    if (!moteur.running) {
      erreur = "Le moteur LIHA est arrêté. Utilise « Reconnecter »."
      return false
    }
    numeroRequete += 1
    moteur.write(JSON.stringify({ id: String(numeroRequete), methode: methode, parametres: parametres || {} }) + "\n")
    return true
  }

  function envoyer() {
    var texte = saisie.text.trim()
    if (!pret || !fournisseurDisponible || occupe || !texte || !dossier.text.trim()) return
    erreur = ""
    if (requete("discuter", { texte: texte, fournisseur: fournisseur, mode: mode, dossier: dossier.text.trim() })) {
      occupe = true
      activite = "discussion"
      saisie.text = ""
      onglet = "conversation"
      reglages = false
      reglagesVoix = false
    }
  }

  // Exposé à shell.call pour que le raccourci d'arrêt reste indépendant du focus.
  function arreter() {
    if (moteur.running) {
      requete("arreter", {})
      requete("voix_arreter", {})
    }
  }

  function approuver(accord) {
    if (!approbationAttendue) return
    approbationAttendue = false
    requete("approuver", { accord: accord })
  }

  function recevoir(ligne) {
    var evenement
    try { evenement = JSON.parse(ligne) }
    catch (e) {
      erreur = "Réponse du moteur illisible. La conversation n'a pas été interprétée."
      return
    }
    if (evenement.type === "etat") {
      pret = true
      delaiDemarrage.stop()
      occupe = evenement.occupe === true
      approbationAttendue = evenement.approbation_attendue === true
      activite = evenement.activite || "repos"
      lecture = evenement.lecture === true
      fournisseurs = evenement.fournisseurs || ({})
      voix = evenement.voix || ({})
    } else if (evenement.type === "message") {
      var contenu = String(evenement.texte || "")
      var auteur = evenement.role === "user" ? "Toi" : evenement.role === "assistant" ? "LIHA" : "Système"
      if (contenu) messages.append({ auteur: auteur, contenu: contenu })
      if (evenement.role === "assistant" && contenu) {
        derniereReponse = contenu
        if (lectureAutomatique && voix.synthese === true) requete("parler", { texte: contenu })
      }
      Qt.callLater(function() { conversation.positionViewAtEnd() })
    } else if (evenement.type === "action") {
      actions.append({ nom: String(evenement.nom || "Action"), etatAction: String(evenement.etat || ""), detail: typeof evenement.detail === "string" ? evenement.detail : JSON.stringify(evenement.detail || {}) })
      Qt.callLater(function() { journal.positionViewAtEnd() })
    } else if (evenement.type === "approbation") {
      approbationAttendue = true
      reglages = false
      reglagesVoix = false
      raisonApprobation = String(evenement.raison || "Vérifie les actions proposées avant de donner ton accord.")
      actionsApprobation = (evenement.actions || []).map(function(action) {
        return String(action.outil || "Action") + "\n" + JSON.stringify(action.arguments || {}, null, 2)
      }).join("\n\n")
    } else if (evenement.type === "transcription") {
      var transcription = String(evenement.texte || "").trim()
      if (transcription) saisie.text = saisie.text ? saisie.text + "\n" + transcription : transcription
      Qt.callLater(function() { saisie.forceActiveFocus() })
    } else if (evenement.type === "erreur") {
      erreur = String(evenement.texte || "Une erreur est survenue.")
    } else if (evenement.type === "termine") {
      // L'état du moteur est la source de vérité, notamment pour la voix parallèle.
      requete("etat", {})
    }
  }

  function diagnosticFournisseur() {
    var etat = fournisseurs[fournisseur]
    if (!etat) return pret ? "Fournisseur non détecté. Actualise après son installation." : "Vérification du fournisseur…"
    return String(etat.detail || etat.raison || (etat.disponible === true ? "Fournisseur disponible" : "Fournisseur indisponible"))
  }

  function applications() {
    if (!lanceurApplications.running) lanceurApplications.running = true
  }

  ListModel { id: messages }
  ListModel { id: actions }

  Process {
    id: lanceurApplications
    command: ["omarchy-shell", "shell", "summon", "omarchy.menu", '{"menu":"apps"}']
    onExited: function(code) {
      if (code !== 0) root.erreur = "Le menu des applications n'a pas pu être ouvert."
    }
  }

  Timer {
    id: delaiDemarrage
    interval: 15000
    onTriggered: if (!root.pret) root.erreur = "Le moteur ne répond pas. Vérifie que Python 3 est installé, puis utilise « Reconnecter ». Pour configurer la voix : « omarchy setup liha --voix »."
  }

  Process {
    id: moteur
    command: [decodeURIComponent(String(Qt.resolvedUrl("backend/demarrer")).replace(/^file:\/\//, ""))]
    stdinEnabled: true
    onStarted: root.requete("etat", {})
    stdout: SplitParser { onRead: function(ligne) { root.recevoir(ligne) } }
    // Les diagnostics sont transmis par JSON ; ne pas afficher stderr qui peut contenir des données sensibles.
    stderr: SplitParser { onRead: function(ligne) {} }
    onExited: function(code) {
      root.pret = false
      root.occupe = false
      root.approbationAttendue = false
      root.lecture = false
      root.activite = "repos"
      delaiDemarrage.stop()
      root.erreur = "Le moteur LIHA s'est arrêté (code " + code + "). Tu peux le reconnecter."
    }
  }

  component Texte: Text {
    textFormat: Text.PlainText
    color: Color.foreground
    font.family: Style.font.family
    font.pixelSize: Style.font.body
    wrapMode: Text.Wrap
  }

  component Bouton: Ui.Button {
    focusable: true
    opacity: enabled ? 1 : 0.42
  }

  FloatingWindow {
    id: fenetre
    visible: false
    title: "LIHA · BlowVizion"
    color: Color.background
    implicitWidth: Style.space(760)
    implicitHeight: Style.space(860)
    minimumSize: Qt.size(Style.space(580), Style.space(680))
    onVisibleChanged: {
      if (!visible && !root.fermetureHote && root.shell && typeof root.shell.hide === "function")
        root.shell.hide("blowvizion.liha")
    }

    FocusScope {
      anchors.fill: parent
      focus: true
      Keys.onEscapePressed: root.fermer()

      ColumnLayout {
        anchors.fill: parent
        anchors.margins: Style.spacing.panelPadding
        spacing: Style.space(12)

        RowLayout {
          Layout.fillWidth: true
          spacing: Style.space(12)
          Rectangle {
            implicitWidth: Style.space(5)
            implicitHeight: Style.space(40)
            radius: Style.cornerRadius
            color: Color.accent
          }
          ColumnLayout {
            Layout.fillWidth: true
            spacing: Style.space(3)
            Texte { text: "LIHA"; font.pixelSize: Style.font.display; font.bold: true }
            Texte { text: "Ton assistante dans BV-LIHA · BlowVizion"; color: root.secondaire; font.pixelSize: Style.font.bodySmall }
          }
          Bouton {
            text: "Applications"
            tooltipText: "Ouvrir les applications installées"
            onClicked: root.applications()
          }
          Bouton { text: "Masquer"; tooltipText: "Masquer ce panneau ; la tâche continue"; onClicked: root.fermer() }
        }

        RowLayout {
          Layout.fillWidth: true
          Rectangle {
            implicitWidth: Style.space(7)
            implicitHeight: implicitWidth
            radius: width / 2
            color: root.erreur ? Color.urgent : root.occupe || root.lecture ? Color.accent : root.secondaire
          }
          Texte { Layout.fillWidth: true; text: root.statut; color: root.secondaire; font.pixelSize: Style.font.bodySmall }
          Bouton {
            text: root.pret ? "Actualiser" : "Reconnecter"
            fontSize: Style.font.bodySmall
            enabled: !root.occupe
            onClicked: {
              root.erreur = ""
              if (moteur.running) root.requete("etat", {})
              else root.demarrer()
            }
          }
          Bouton {
            text: "Arrêter"
            bordered: true
            foreground: Color.urgent
            tooltipText: "Interrompre la tâche, le microphone et la lecture vocale"
            enabled: root.occupe || root.lecture || root.approbationAttendue
            onClicked: root.arreter()
          }
        }

        RowLayout {
          Layout.fillWidth: true
          spacing: Style.space(12)
          visible: root.reglages && !root.approbationAttendue
          Ui.Dropdown {
            Layout.fillWidth: true
            label: "Fournisseur"
            value: root.fournisseur
            options: [{ value: "codex", label: "Codex · abonnement" }, { value: "grok", label: "Grok · abonnement" }]
            enabled: !root.occupe
            onChanged: function(valeur) { root.fournisseur = valeur }
          }
          Ui.Dropdown {
            Layout.fillWidth: true
            label: "Autonomie"
            value: root.mode
            options: [{ value: "approbation", label: "Demande d'approbation" }, { value: "complet", label: "Accès complet" }]
            enabled: !root.occupe
            onChanged: function(valeur) { root.mode = valeur }
          }
        }

        ColumnLayout {
          Layout.fillWidth: true
          visible: root.reglages && !root.approbationAttendue
          spacing: Style.space(5)
          Texte { text: "Dossier de travail autorisé"; color: root.secondaire; font.pixelSize: Style.font.caption; font.bold: true }
          Ui.TextField {
            id: dossier
            Layout.fillWidth: true
            placeholderText: "/home/ton-compte/Projets/mon-projet"
            enabled: !root.occupe
            selectByMouse: true
          }
          Texte {
            Layout.fillWidth: true
            text: root.mode === "complet" ? "LIHA avance librement dans les outils autorisés. Les opérations destructives restent soumises à ton accord." : "LIHA prépare ses actions et attend ton accord avant de modifier ton environnement."
            color: root.secondaire
            font.pixelSize: Style.font.caption
          }
        }

        Ui.BorderSurface {
          Layout.fillWidth: true
          Layout.preferredHeight: alerte.implicitHeight + Style.space(18)
          visible: root.erreur !== ""
          color: Qt.alpha(Color.urgent, 0.08)
          borderSpec: Border.controlSpec("normal", Color.urgent, Color.urgent)
          radius: Style.cornerRadius
          Texte {
            id: alerte
            anchors.fill: parent
            anchors.margins: Style.space(9)
            text: root.erreur
            color: Color.urgent
            font.pixelSize: Style.font.bodySmall
            maximumLineCount: 4
            elide: Text.ElideRight
          }
        }

        RowLayout {
          Layout.fillWidth: true
          Bouton { text: "Conversation"; selected: root.onglet === "conversation"; onClicked: root.onglet = "conversation" }
          Bouton { text: "Activité"; selected: root.onglet === "activite"; onClicked: root.onglet = "activite" }
          Item { Layout.fillWidth: true }
          Bouton { text: "Réglages"; selected: root.reglages; enabled: !root.approbationAttendue; onClicked: { root.reglages = !root.reglages; root.reglagesVoix = false } }
          Bouton { text: "Voix"; selected: root.reglagesVoix; enabled: !root.approbationAttendue; onClicked: { root.reglagesVoix = !root.reglagesVoix; root.reglages = false } }
        }

        ColumnLayout {
          Layout.fillWidth: true
          visible: root.reglagesVoix
          spacing: Style.space(5)
          Texte { Layout.fillWidth: true; text: root.voix.detail || "Voix indisponible."; color: root.secondaire; font.pixelSize: Style.font.bodySmall }
          Bouton {
            text: root.lectureAutomatique ? "Lecture automatique activée" : "Activer la lecture des réponses"
            selected: root.lectureAutomatique
            enabled: root.voix.synthese === true
            onClicked: root.lectureAutomatique = !root.lectureAutomatique
          }
        }

        Item {
          Layout.fillWidth: true
          Layout.fillHeight: true
          Layout.minimumHeight: Style.space(95)

          Column {
            anchors.centerIn: parent
            width: Math.min(parent.width - Style.space(20), Style.space(460))
            spacing: Style.space(12)
            visible: root.onglet === "conversation" && messages.count === 0
            Texte { width: parent.width; text: "Qu'est-ce qu'on fait ensemble ?"; font.pixelSize: Style.font.heading; font.bold: true }
            Texte { width: parent.width; text: "Choisis un dossier, puis écris ta demande ou dicte-la. Tu verras ici les réponses et dans Activité les actions réellement exécutées."; color: root.secondaire }
          }

          ListView {
            id: conversation
            anchors.fill: parent
            visible: root.onglet === "conversation"
            model: messages
            spacing: Style.space(14)
            clip: true
            boundsBehavior: Flickable.StopAtBounds
            Controls.ScrollBar.vertical: Controls.ScrollBar { policy: Controls.ScrollBar.AsNeeded }
            delegate: Rectangle {
              id: carteMessage
              required property string auteur
              required property string contenu
              width: conversation.width - Style.space(12)
              height: messageColonne.implicitHeight + Style.space(22)
              radius: Style.cornerRadius
              color: auteur === "Toi" ? Qt.alpha(Color.accent, 0.09) : Qt.alpha(Color.foreground, 0.035)
              Column {
                id: messageColonne
                x: Style.space(12)
                y: Style.space(11)
                width: parent.width - Style.space(24)
                spacing: Style.space(6)
                Texte { text: carteMessage.auteur; font.bold: true; color: carteMessage.auteur === "Toi" ? Color.accent : Color.foreground; font.pixelSize: Style.font.caption }
                TextEdit {
                  width: parent.width
                  text: carteMessage.contenu
                  textFormat: TextEdit.PlainText
                  readOnly: true
                  selectByMouse: true
                  wrapMode: TextEdit.Wrap
                  color: Color.foreground
                  selectionColor: Qt.alpha(Color.accent, 0.35)
                  font.family: Style.font.family
                  font.pixelSize: Style.font.body
                }
              }
            }
          }

          Texte {
            anchors.centerIn: parent
            width: parent.width - Style.space(24)
            visible: root.onglet === "activite" && actions.count === 0
            text: "Aucune action exécutée pour le moment. Les commandes et leurs résultats apparaîtront ici pendant le travail."
            color: root.secondaire
          }

          ListView {
            id: journal
            anchors.fill: parent
            visible: root.onglet === "activite"
            model: actions
            spacing: Style.space(14)
            clip: true
            boundsBehavior: Flickable.StopAtBounds
            Controls.ScrollBar.vertical: Controls.ScrollBar { policy: Controls.ScrollBar.AsNeeded }
            delegate: Column {
              id: ligneAction
              required property string nom
              required property string etatAction
              required property string detail
              width: journal.width - Style.space(12)
              spacing: Style.space(5)
              Texte { width: parent.width; text: ligneAction.nom + (ligneAction.etatAction ? " · " + ligneAction.etatAction : ""); font.bold: true; color: Color.accent }
              TextEdit {
                width: parent.width
                text: ligneAction.detail
                textFormat: TextEdit.PlainText
                readOnly: true
                selectByMouse: true
                wrapMode: TextEdit.Wrap
                color: root.secondaire
                selectionColor: Qt.alpha(Color.accent, 0.35)
                font.family: Style.font.family
                font.pixelSize: Style.font.bodySmall
              }
            }
          }
        }

        Ui.BorderSurface {
          Layout.fillWidth: true
          Layout.preferredHeight: Style.space(205)
          visible: root.approbationAttendue
          color: Qt.alpha(Color.accent, 0.07)
          borderSpec: Border.controlSpec("focus", Color.foreground, Color.accent)
          radius: Style.cornerRadius
          ColumnLayout {
            anchors.fill: parent
            anchors.margins: Style.space(12)
            spacing: Style.space(8)
            Texte { text: "Ton accord avant d'agir"; font.bold: true; color: Color.accent }
            Controls.ScrollView {
              id: defilementApprobation
              Layout.fillWidth: true
              Layout.fillHeight: true
              clip: true
              contentWidth: availableWidth
              TextEdit {
                width: defilementApprobation.availableWidth
                text: root.raisonApprobation + "\n\n" + root.actionsApprobation
                textFormat: TextEdit.PlainText
                readOnly: true
                selectByMouse: true
                wrapMode: TextEdit.Wrap
                color: Color.foreground
                selectionColor: Qt.alpha(Color.accent, 0.35)
                font.family: Style.font.family
                font.pixelSize: Style.font.bodySmall
              }
            }
            RowLayout {
              Bouton { text: "Refuser"; bordered: true; onClicked: root.approuver(false) }
              Item { Layout.fillWidth: true }
              Bouton { text: "Autoriser ces actions"; selected: true; bordered: true; onClicked: root.approuver(true) }
            }
          }
        }

        Ui.BorderSurface {
          Layout.fillWidth: true
          Layout.preferredHeight: Style.space(92)
          visible: !root.approbationAttendue
          color: Qt.alpha(Color.foreground, 0.035)
          borderSpec: Border.controlSpec(saisie.activeFocus ? "focus" : "normal", Color.foreground, Color.accent)
          radius: Style.cornerRadius
          Controls.ScrollView {
            anchors.fill: parent
            anchors.margins: Style.space(8)
            clip: true
            Controls.TextArea {
              id: saisie
              placeholderText: root.dicteeEnCours ? "Parle, le microphone est actif…" : "Écris ta demande à LIHA…"
              color: Color.foreground
              placeholderTextColor: root.secondaire
              selectionColor: Qt.alpha(Color.accent, 0.35)
              font.family: Style.font.family
              font.pixelSize: Style.font.body
              wrapMode: TextEdit.Wrap
              selectByMouse: true
              background: Item {}
              Keys.onPressed: function(event) {
                if ((event.key === Qt.Key_Return || event.key === Qt.Key_Enter) && (event.modifiers & Qt.ControlModifier)) {
                  root.envoyer()
                  event.accepted = true
                }
              }
            }
          }
        }

        RowLayout {
          Layout.fillWidth: true
          visible: !root.approbationAttendue
          Bouton {
            text: root.dicteeEnCours ? "Annuler la dictée" : "Dicter"
            bordered: true
            selected: root.dicteeEnCours
            enabled: root.pret && root.voix.dictee === true && !root.lecture && (!root.occupe || root.dicteeEnCours)
            tooltipText: "La dictée reste un brouillon : relis-la avant de l'envoyer"
            onClicked: {
              if (root.dicteeEnCours) root.arreter()
              else if (root.requete("dicter", {})) {
                root.occupe = true
                root.activite = "dictee"
              }
            }
          }
          Bouton {
            text: root.lecture ? "Couper la voix" : "Lire la réponse"
            enabled: root.pret && root.voix.synthese === true && !root.dicteeEnCours && (root.lecture || root.derniereReponse !== "")
            onClicked: root.lecture ? root.requete("voix_arreter", {}) : root.requete("parler", { texte: root.derniereReponse })
          }
          Item { Layout.fillWidth: true }
          Bouton {
            text: "Envoyer"
            selected: true
            bordered: true
            enabled: root.pret && root.fournisseurDisponible && !root.occupe && saisie.text.trim() !== "" && dossier.text.trim() !== ""
            tooltipText: "Ctrl + Entrée"
            onClicked: root.envoyer()
          }
        }

        Texte {
          Layout.fillWidth: true
          text: root.diagnosticFournisseur() + " · Ctrl + Entrée : envoyer"
          color: root.secondaire
          font.pixelSize: Style.font.caption
          maximumLineCount: 2
          elide: Text.ElideRight
        }
      }
    }
  }
}
