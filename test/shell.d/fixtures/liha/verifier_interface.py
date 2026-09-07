"""Vérifie le panneau réel avec Qt et un transport simulé, sans agent ni Wayland.

Exécution dans un environnement Python isolé avec PySide6-Essentials :
  python test/shell.d/fixtures/liha/verifier_interface.py --sortie /tmp/liha-qt
Les doublures Quickshell sont temporaires et ne sont jamais installées.
"""

import argparse
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile

os.environ["QT_QPA_PLATFORM"] = "offscreen"
os.environ["QT_QUICK_BACKEND"] = "software"

from PySide6.QtCore import QPointF, Qt, QTimer, QUrl, qVersion
from PySide6.QtGui import QFontDatabase, QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QQmlEngine, QQmlExpression
from PySide6.QtQuick import QQuickWindow
from PySide6.QtTest import QTest

arguments = argparse.ArgumentParser(description=__doc__)
arguments.add_argument("--sortie", type=Path, required=True)
options = arguments.parse_args()
sortie = options.sortie.resolve()
sortie.mkdir(parents=True, exist_ok=True)
racine = Path(__file__).resolve().parents[4]
temporaire = tempfile.TemporaryDirectory(prefix="liha-qt-")
imports = Path(temporaire.name)


def fichier(nom, contenu):
    chemin = imports / nom
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(contenu, encoding="utf-8")


for dossier in ("Ui", "Commons"):
    shutil.copytree(racine / "shell" / dossier, imports / "qs" / dossier)

fichier("Quickshell/qmldir", "module Quickshell\nsingleton Quickshell 1.0 Quickshell.qml\nFloatingWindow 1.0 FloatingWindow.qml\n")
fichier("Quickshell/Quickshell.qml", """pragma Singleton
import QtQuick
QtObject {
  function env(nom) { return nom === "HOME" ? "/home/essai" : "" }
  function execDetached(args) {}
}""")
fichier("Quickshell/FloatingWindow.qml", """import QtQuick
import QtQuick.Window
Window {
  transientParent: null
  property real implicitWidth: 760
  property real implicitHeight: 860
  property size minimumSize: Qt.size(0, 0)
  width: implicitWidth
  height: implicitHeight
  minimumWidth: minimumSize.width
  minimumHeight: minimumSize.height
}""")
fichier("Quickshell/Io/qmldir", "module Quickshell.Io\nProcess 1.0 Process.qml\nSplitParser 1.0 SplitParser.qml\nStdioCollector 1.0 StdioCollector.qml\nFileView 1.0 FileView.qml\n")
fichier("Quickshell/Io/Process.qml", """import QtQuick
QtObject {
  property var command: []
  property bool running: false
  property bool stdinEnabled: false
  property QtObject stdout: null
  property QtObject stderr: null
  property var requetes: []
  signal started()
  signal exited(int code)
  onRunningChanged: if (running) Qt.callLater(function() { started() })
  function write(texte) { requetes = requetes.concat([texte]) }
}""")
fichier("Quickshell/Io/SplitParser.qml", "import QtQuick\nQtObject { signal read(string data) }")
fichier("Quickshell/Io/StdioCollector.qml", 'import QtQuick\nQtObject { property string text: ""; property bool waitForEnd: false; signal streamFinished() }')
fichier("Quickshell/Io/FileView.qml", """import QtQuick
QtObject {
  property string path: ""
  property bool watchChanges: false
  property bool printErrors: false
  signal loaded()
  signal loadFailed()
  signal fileChanged()
  function text() { return "" }
  function reload() {}
}""")

app = QGuiApplication(sys.argv)
if os.name == "nt":
    # Le moteur Qt hors écran ne trouve pas toujours les polices Windows.
    polices = Path(os.environ.get("SystemRoot", "C:/Windows")) / "Fonts"
    for nom in ("consola.ttf", "consolab.ttf"):
        if (polices / nom).is_file():
            QFontDatabase.addApplicationFont(str(polices / nom))
engine = QQmlApplicationEngine()
engine.addImportPath(str(imports))
engine.load(QUrl.fromLocalFile(str(racine / "shell/plugins/liha/Panel.qml")))
if not engine.rootObjects():
    raise SystemExit(1)
root = engine.rootObjects()[0]
fenetres = app.allWindows()


def expression(texte):
    expr = QQmlExpression(QQmlEngine.contextForObject(root), root, texte)
    resultat, _ = expr.evaluate()
    if expr.hasError():
        raise RuntimeError(expr.error().toString())
    return resultat


def envoyer(evenement):
    expression("recevoir(" + json.dumps(json.dumps(evenement, ensure_ascii=False)) + ")")


def fenetre():
    return next(f for f in fenetres if f.isVisible())


def capture(nom):
    app.processEvents()
    image = fenetre().grabWindow()
    if image.isNull() or not image.save(str(sortie / (nom + ".png"))):
        raise RuntimeError("La capture Qt a échoué : " + nom)


def bouton(texte):
    pile = [fenetre().contentItem()]
    while pile:
        item = pile.pop()
        if item.property("text") == texte and item.property("focusable") is True:
            return item
        pile.extend(item.childItems())
    raise RuntimeError("Bouton introuvable : " + texte)


def clic(texte):
    item = bouton(texte)
    assert item.isEnabled() and item.isVisible(), texte
    position = item.mapToScene(QPointF(item.width() / 2, item.height() / 2)).toPoint()
    QTest.mouseClick(fenetre(), Qt.LeftButton, Qt.NoModifier, position)
    app.processEvents()


def requetes():
    return [json.loads(t) for t in json.loads(expression("JSON.stringify(moteur.requetes)"))]


def phase_initiale():
    if "Consolas" in QFontDatabase.families():
        expression('Style.resolvedFontFamily = "Consolas"')
    expression('open("{}")')
    envoyer({"type": "etat", "occupe": False, "approbation_attendue": False, "activite": "repos", "lecture": False,
             "fournisseurs": {"codex": {"disponible": True, "detail": "Codex installé · authentification à vérifier lors de la première demande"}, "grok": {"disponible": False, "detail": "Grok non installé"}},
             "voix": {"dictee": False, "synthese": False, "detail": "Dictée : modèle Vosk manquant. Lecture : eSpeak NG manquant.", "nom_voix": ""}})
    QTimer.singleShot(350, phase_conversation)


def phase_conversation():
    capture("accueil")
    envoyer({"type": "message", "role": "user", "texte": "Ouvre le projet de mon site et explique-moi comment le lancer."})
    envoyer({"type": "message", "role": "assistant", "texte": "Je vais examiner les fichiers du projet pour trouver la commande de lancement. Je te demanderai ensuite ton accord avant d’exécuter les actions proposées."})
    expression("reglages = false")
    QTimer.singleShot(200, phase_approbation)


def phase_approbation():
    capture("conversation")
    envoyer({"type": "action", "nom": "lire_fichier", "etat": "terminée", "detail": "Lecture de package.json dans le dossier autorisé."})
    envoyer({"type": "approbation", "raison": "Les actions suivantes ouvriront ton projet et un terminal. Vérifie le dossier avant de donner ton accord.",
             "actions": [{"outil": "ouvrir_application", "arguments": {"application": "code", "chemin": "/home/essai/Projets/site-vitrine"}}, {"outil": "ouvrir_terminal", "arguments": {"dossier": "/home/essai/Projets/site-vitrine"}}]})
    QTimer.singleShot(200, phase_minimum)


def phase_minimum():
    capture("approbation")
    fenetre().resize(580, 680)
    QTimer.singleShot(200, phase_interactions)


def phase_interactions():
    capture("approbation-minimum")
    clic("Autoriser ces actions")
    assert requetes()[-1]["methode"] == "approuver" and requetes()[-1]["parametres"]["accord"] is True
    expression('occupe = false; approbationAttendue = false; activite = "repos"; dossier.text = "/home/essai/Projets/essai"; saisie.text = "Ouvre mon projet"; saisie.forceActiveFocus()')
    QTest.keyClick(fenetre(), Qt.Key_Return, Qt.ControlModifier)
    app.processEvents()
    assert requetes()[-1]["methode"] == "discuter", requetes()
    assert requetes()[-1]["parametres"]["dossier"] == "/home/essai/Projets/essai"
    assert root.property("occupe") is True
    clic("Arrêter")
    assert [r["methode"] for r in requetes()[-2:]] == ["arreter", "voix_arreter"]
    avant = len(requetes())
    envoyer({"type": "transcription", "texte": "Ma demande orale"})
    assert expression("saisie.text") == "Ma demande orale"
    assert len(requetes()) == avant
    expression('occupe = false; activite = "repos"; fournisseur = "grok"')
    assert not bouton("Envoyer").isEnabled()
    assert not bouton("Dicter").isEnabled()
    expression("close()")
    assert root.property("opened") is False and expression("moteur.running") is True
    expression('open("{}")')
    assert root.property("opened") is True and expression("messages.count") == 2
    expression('reglages = true; erreur = "Le fournisseur n’est pas authentifié. Ouvre un terminal, connecte-toi avec ton abonnement existant, puis actualise le panneau LIHA. Aucun appel payant n’a été effectué."')
    capture("erreur-minimum")
    controles = ["approbation à la souris", "envoi Ctrl+Entrée", "arrêt pendant une tâche", "transcription en brouillon sans envoi", "fournisseur absent désactivé", "microphone absent désactivé", "conversation conservée après masquage"]
    rapport = {"nature": "Panneau réel et composants Omarchy réels ; fenêtre et transport Quickshell simulés. Aucun agent réel, microphone ou environnement Wayland testé.", "qt": qVersion(), "controles": controles}
    (sortie / "rapport.json").write_text(json.dumps(rapport, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("Contrôles Qt réussis. Rendus à inspecter : " + str(sortie))
    app.quit()


def echec_exception(type_erreur, erreur, trace):
    sys.__excepthook__(type_erreur, erreur, trace)
    app.exit(1)


sys.excepthook = echec_exception
QTimer.singleShot(0, phase_initiale)
QTimer.singleShot(10000, lambda: app.exit(2))
code = app.exec()
engine.deleteLater()
app.processEvents()
temporaire.cleanup()
sys.exit(code)
