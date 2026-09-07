"""Génère l’identité BV-LIHA sans police ni ressource graphique externe.

Utilisation : python scripts/generer-identite-bv-liha.py
Les exports PNG nécessitent PySide6 ; --sans-png génère uniquement SVG et ASCII.
Les tracés géométriques appartiennent à BlowVizion et suivent la licence du dépôt.
L’aperçu Plymouth assemble le nouveau logo et les éléments du thème existant ;
il ne constitue pas une capture de démarrage réel.
"""

from __future__ import annotations

import argparse
from pathlib import Path


RACINE = Path(__file__).resolve().parents[1]

SVG = '''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="188" viewBox="0 0 800 188" role="img" aria-labelledby="titre description">
  <title id="titre">BV-LIHA</title>
  <desc id="description">Linux Intelligent Hybride Autonome, par BlowVizion. Lettres géométriques originales sans police.</desc>
  <g fill="none" stroke="#9ece6a" stroke-width="14" stroke-linecap="square" stroke-linejoin="round">
    <g id="sigle">
      <path transform="translate(83 44)" d="M0 100V0H38Q64 0 64 25T38 50H0M38 50Q70 50 70 75T38 100H0"/>
      <path transform="translate(189 44)" d="M0 0L34 100L68 0"/>
    </g>
    <path transform="translate(291 44)" d="M0 50H32"/>
    <path transform="translate(357 44)" d="M0 0V100H60"/>
    <path transform="translate(455 44)" d="M0 0H44M22 0V100M0 100H44"/>
    <path transform="translate(537 44)" d="M0 0V100M70 0V100M0 50H70"/>
    <path transform="translate(645 44)" d="M0 100L36 0L72 100M13 65H59"/>
  </g>
</svg>
'''

# Une grille originale commune aux deux variantes terminal ; caractères ASCII.
LETTRES = {
    "B": ["11110", "10001", "10001", "11110", "10001", "10001", "11110"],
    "V": ["10001", "10001", "10001", "10001", "01010", "01010", "00100"],
    "-": ["00000", "00000", "00000", "11111", "00000", "00000", "00000"],
    "L": ["10000", "10000", "10000", "10000", "10000", "10000", "11111"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
    "H": ["10001", "10001", "10001", "11111", "10001", "10001", "10001"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
}


def dessiner_ascii(texte: str, largeur_pixel: int = 1) -> list[str]:
    return [
        (" " * (2 * largeur_pixel)).join(
            "".join(("#" if valeur == "1" else " ") * largeur_pixel for valeur in LETTRES[lettre][ligne])
            for lettre in texte
        ).rstrip()
        for ligne in range(7)
    ]


def ecrire_texte(chemin: Path, contenu: str) -> None:
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(contenu, encoding="utf-8", newline="\n")


def exporter_png() -> None:
    try:
        from PySide6.QtCore import QRectF, Qt
        from PySide6.QtGui import QImage, QPainter
        from PySide6.QtSvg import QSvgRenderer
    except ImportError as erreur:
        raise SystemExit("L’export PNG nécessite PySide6 ; utilise --sans-png pour les textes et le SVG.") from erreur

    rendu = QSvgRenderer(str(RACINE / "logo.svg"))
    if not rendu.isValid():
        raise SystemExit("Le SVG BV-LIHA est invalide.")

    for nom in ("default/sddm/omarchy/logo.png", "default/plymouth/logo.png", "icon.png"):
        icone = nom == "icon.png"
        image = QImage(300 if icone else 800, 300 if icone else 188, QImage.Format.Format_ARGB32)
        image.fill(Qt.GlobalColor.transparent)
        peintre = QPainter(image)
        peintre.setRenderHint(QPainter.RenderHint.Antialiasing)
        if icone:
            dimensions = rendu.boundsOnElement("sigle")
            largeur = 236.0
            hauteur = largeur * dimensions.height() / dimensions.width()
            rendu.render(peintre, "sigle", QRectF((300 - largeur) / 2, (300 - hauteur) / 2, largeur, hauteur))
        else:
            rendu.render(peintre)
        peintre.end()
        destination = RACINE / nom
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not image.save(str(destination)):
            raise SystemExit(f"Impossible d’écrire {destination}.")
        print(f"PNG créé : {nom} ({image.width()} × {image.height()})")


def exporter_apercu_plymouth() -> None:
    """Recompose l’aperçu selon la géométrie de bin/omarchy-plymouth-preview."""
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QColor, QImage, QPainter

    dossier = RACINE / "default/plymouth"

    def charger(nom: str, recolorer: bool = False) -> QImage:
        image = QImage(str(dossier / nom))
        if image.isNull():
            raise SystemExit(f"Impossible de charger l’élément Plymouth {nom}.")
        if recolorer:
            image = image.convertToFormat(QImage.Format.Format_ARGB32_Premultiplied)
            peintre = QPainter(image)
            peintre.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
            peintre.fillRect(image.rect(), QColor("#c0caf5"))
            peintre.end()
        return image

    logo = charger("logo.png")
    saisie = charger("entry.png", recolorer=True)
    cadenas = charger("lock.png", recolorer=True)
    point = charger("bullet.png", recolorer=True)
    largeur, hauteur = 1920, 1080
    logo_x = (largeur - logo.width()) // 2
    logo_y = (hauteur - logo.height()) // 2
    saisie_x = (largeur - saisie.width()) // 2
    saisie_y = logo_y + logo.height() + 40
    cadenas_hauteur = int(saisie.height() * 0.8)
    cadenas_largeur = int(84 * cadenas_hauteur / 96)
    cadenas_x = saisie_x - cadenas_largeur - 15
    cadenas_y = saisie_y + saisie.height() // 2 - cadenas_hauteur // 2
    point_y = saisie_y + saisie.height() // 2 - 4

    apercu = QImage(largeur, hauteur, QImage.Format.Format_ARGB32)
    apercu.fill(QColor("#1a1b26"))
    peintre = QPainter(apercu)
    peintre.drawImage(logo_x, logo_y, logo)
    peintre.drawImage(saisie_x, saisie_y, saisie)
    peintre.drawImage(cadenas_x, cadenas_y, cadenas.scaled(
        cadenas_largeur, cadenas_hauteur, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
    ))
    point = point.scaled(7, 7, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    for index in range(4):
        peintre.drawImage(saisie_x + 20 + index * 12, point_y, point)
    peintre.end()
    destination = dossier / "preview-unlock.png"
    if not apercu.save(str(destination)):
        raise SystemExit(f"Impossible d’écrire {destination}.")
    print(f"Aperçu généré : default/plymouth/preview-unlock.png ({largeur} × {hauteur})")


def principal() -> None:
    arguments = argparse.ArgumentParser(description=__doc__)
    arguments.add_argument("--sans-png", action="store_true", help="Générer uniquement le SVG et les deux fichiers ASCII.")
    options = arguments.parse_args()

    ecrire_texte(RACINE / "logo.svg", SVG)
    lignes_logo = dessiner_ascii("BV-LIHA")
    lignes_logo += ["", "BlowVizion".center(47).rstrip()]
    ecrire_texte(RACINE / "logo.txt", "\n".join(lignes_logo) + "\n")
    lignes_icone = dessiner_ascii("BV", largeur_pixel=2)
    lignes_icone += ["", "BV-LIHA".center(24).rstrip()]
    ecrire_texte(RACINE / "icon.txt", "\n".join(lignes_icone) + "\n")
    if not options.sans_png:
        exporter_png()
        exporter_apercu_plymouth()


if __name__ == "__main__":
    principal()
