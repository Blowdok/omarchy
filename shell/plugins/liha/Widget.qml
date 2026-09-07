import QtQuick
import qs.Ui

BarWidget {
  id: root
  moduleName: "blowvizion.liha"

  implicitWidth: bouton.implicitWidth
  implicitHeight: bouton.implicitHeight

  WidgetButton {
    id: bouton
    anchors.fill: parent
    bar: root.bar
    text: root.vertical ? "L" : "LIHA"
    tooltipText: "LIHA · Texte et voix\nClic droit : applications"
    onPressed: function(boutonSouris) {
      if (!root.bar) return
      if (boutonSouris === Qt.RightButton)
        root.bar.run("omarchy-shell shell summon omarchy.menu '{\"menu\":\"apps\"}'")
      else if (boutonSouris === Qt.LeftButton)
        root.bar.run("omarchy-shell shell toggle blowvizion.liha '{}'")
    }
  }
}
