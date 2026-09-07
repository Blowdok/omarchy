"""Essai explicite sur abonnement réel : crée uniquement un fichier dans un dossier temporaire."""

import argparse
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import time


def main():
  options = argparse.ArgumentParser(description=__doc__)
  options.add_argument("--fournisseur", choices=("codex", "grok"), default="codex")
  choix = options.parse_args()
  moteur = Path(__file__).resolve().parents[1] / "moteur.py"
  with tempfile.TemporaryDirectory(prefix="liha-essai-") as dossier:
    processus = subprocess.Popen([sys.executable, "-u", str(moteur)], stdin=subprocess.PIPE,
      stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
    termine, erreurs = threading.Event(), []
    evenements = []

    def lire():
      for ligne in processus.stdout:
        evenement = json.loads(ligne)
        evenements.append(evenement)
        if evenement["type"] == "approbation":
          processus.stdin.write(json.dumps({"methode": "approuver", "parametres": {"accord": False}}) + "\n")
          processus.stdin.flush()
          erreurs.append("Le fournisseur a proposé une action hors du scénario autorisé.")
        if evenement["type"] == "erreur":
          erreurs.append(evenement["texte"])
        if evenement["type"] == "termine":
          termine.set()

    lecteur = threading.Thread(target=lire, daemon=True)
    lecteur.start()
    debut = time.monotonic()
    try:
      requete = {"id": "essai", "methode": "discuter", "parametres": {
        "dossier": dossier, "mode": "complet", "fournisseur": choix.fournisseur,
        "texte": "Crée avec ecrire_fichier le fichier bonjour-liha.txt contenant exactement les 12 caractères entre guillemets : \"Bonjour Boss\" (sans les guillemets, sans point final). Ne lance aucune commande. Quand le résultat confirme la création, termine sans autre action."}}
      processus.stdin.write(json.dumps(requete) + "\n")
      processus.stdin.flush()
      if not termine.wait(150):
        raise RuntimeError("Délai de l’essai dépassé.")
      if erreurs:
        raise RuntimeError(" ; ".join(erreurs))
      contenu = (Path(dossier) / "bonjour-liha.txt").read_text(encoding="utf-8")
      if contenu.strip() != "Bonjour Boss":
        raise RuntimeError("Contenu du fichier inattendu : " + repr(contenu[:80]))
      actions = [e["nom"] for e in evenements if e["type"] == "action" and e["etat"] == "terminee"]
      print(json.dumps({"fournisseur": choix.fournisseur, "reussi": True,
        "actions": actions, "duree_secondes": round(time.monotonic() - debut, 1)}, ensure_ascii=False))
    finally:
      processus.stdin.close()
      try:
        processus.wait(timeout=8)
      except subprocess.TimeoutExpired:
        processus.kill()
        processus.wait(timeout=3)
      lecteur.join(timeout=2)
      processus.stdout.close()
      processus.stderr.close()


if __name__ == "__main__":
  main()
