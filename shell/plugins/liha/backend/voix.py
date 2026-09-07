"""Voix française locale ; aucun service réseau ni microphone ouvert au chargement.

Vosk et sounddevice suivent l'exemple officiel :
https://github.com/alphacep/vosk-api/blob/master/python/example/test_microphone.py
La synthèse utilise les options documentées d'eSpeak NG :
https://github.com/espeak-ng/espeak-ng/blob/master/src/espeak-ng.c
"""

from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import threading
import time


DUREE_DICTEE = 30.0
DUREE_SYNTHESE = 120.0
LONGUEUR_SYNTHESE = 2000
FICHIERS_MODELE = (
  "am/final.mdl",
  "conf/mfcc.conf",
  "conf/model.conf",
  "graph/HCLr.fst",
  "graph/Gr.fst",
)


def chemin_modele() -> Path:
  """Le modèle est préparé explicitement, jamais téléchargé par Vosk."""
  personnalise = os.environ.get("LIHA_MODELE_VOSK")
  if personnalise:
    return Path(personnalise).expanduser()
  donnees = os.environ.get("XDG_DATA_HOME")
  racine = Path(donnees).expanduser() if donnees else Path.home() / ".local/share"
  return racine / "liha/modeles/vosk-fr"


def modele_present(chemin: Path) -> bool:
  return all((chemin / fichier).is_file() for fichier in FICHIERS_MODELE)


def _modules_dictee():
  try:
    vosk = importlib.import_module("vosk")
    audio = importlib.import_module("sounddevice")
    return vosk, audio
  except (ImportError, OSError) as erreur:
    raise RuntimeError(
      "Dictée indisponible : préparer Vosk, sounddevice et PortAudio avec omarchy-setup-liha."
    ) from erreur


def diagnostiquer() -> dict:
  """Inventorie les composants et le périphérique, sans enregistrer de son."""
  dictee = False
  details = []
  try:
    _vosk, audio = _modules_dictee()
    if not modele_present(chemin_modele()):
      details.append("Modèle français absent ou incomplet : lancer omarchy-setup-liha --voix.")
    else:
      appareil = audio.query_devices(kind="input")
      if appareil["max_input_channels"] < 1:
        details.append("Aucun microphone par défaut disponible.")
      else:
        dictee = True
        details.append("Dictée locale Vosk prête ; microphone ouvert seulement sur demande.")
  except RuntimeError as erreur:
    details.append(str(erreur))
  except Exception:
    details.append("Microphone indisponible : vérifier le périphérique d'entrée et PortAudio.")
  synthese = bool(shutil.which("espeak-ng"))
  if synthese:
    details.append("Voix eSpeak NG française gratuite et synthétique, sans qualité HD.")
  else:
    details.append("Lecture vocale indisponible : installer espeak-ng avec omarchy-setup-liha --voix.")
  details.append("Vivienne n'est pas intégrée ; aucun service vocal payant n'est utilisé.")
  return {
    "dictee": dictee,
    "synthese": synthese,
    "detail": " ".join(details),
    "nom_voix": "eSpeak NG français" if synthese else "Aucune voix installée",
  }


def _texte_resultat(resultat: str, cle: str = "text") -> str:
  contenu = json.loads(resultat).get(cle, "")
  return contenu.strip() if isinstance(contenu, str) else ""


def dicter(annulation: threading.Event) -> str:
  """Capture une phrase, au maximum 30 secondes ; une annulation la supprime.

  Vosk termine un segment après la parole et son silence final. Le microphone
  est fermé avant de rendre la transcription, à relire avant tout envoi.
  Aucun audio n'est conservé sur disque.
  """
  if annulation.is_set():
    return ""
  vosk, audio = _modules_dictee()
  chemin = chemin_modele()
  if not modele_present(chemin):
    raise RuntimeError("Modèle français absent ou incomplet : lancer omarchy-setup-liha --voix.")
  blocs = queue.Queue(maxsize=20)
  perte_audio = threading.Event()

  def recevoir(donnees, nombre_trames, horodatage, statut):
    if annulation.is_set():
      return
    if statut:
      perte_audio.set()
    try:
      blocs.put_nowait(bytes(donnees))
    except queue.Full:
      perte_audio.set()

  try:
    appareil = audio.query_devices(kind="input")
    frequence = int(appareil["default_samplerate"])
    if not 8000 <= frequence <= 192000:
      raise RuntimeError("Fréquence du microphone non prise en charge.")
    vosk.SetLogLevel(-1)
    # Le chemin explicite est essentiel : Model(lang=...) peut télécharger.
    modele = vosk.Model(model_path=str(chemin))
    if annulation.is_set():
      return ""
    reconnaissance = vosk.KaldiRecognizer(modele, frequence)
    texte = ""
    with audio.RawInputStream(
      samplerate=frequence, blocksize=max(800, frequence // 10),
      dtype="int16", channels=1, callback=recevoir,
    ):
      echeance = time.monotonic() + DUREE_DICTEE
      while not annulation.is_set() and time.monotonic() < echeance:
        if perte_audio.is_set():
          raise RuntimeError("Capture audio interrompue : données perdues, recommencer la dictée.")
        try:
          donnees = blocs.get(timeout=max(0.001, min(0.1, echeance - time.monotonic())))
        except queue.Empty:
          continue
        if reconnaissance.AcceptWaveform(donnees):
          texte = _texte_resultat(reconnaissance.Result())
          if texte:
            break
      if not annulation.is_set() and not texte:
        texte = _texte_resultat(reconnaissance.FinalResult())
    # Revérifier après la fermeture : Stop ne doit jamais livrer du texte.
    if perte_audio.is_set() and not annulation.is_set():
      raise RuntimeError("Capture audio interrompue : données perdues, recommencer la dictée.")
    return "" if annulation.is_set() else texte
  except RuntimeError:
    raise
  except Exception as erreur:
    if annulation.is_set():
      return ""
    raise RuntimeError(
      "Dictée impossible : vérifier le microphone, le modèle français et le service audio."
    ) from erreur


def _arreter_processus(processus: subprocess.Popen) -> None:
  if processus.poll() is None:
    processus.terminate()
    try:
      processus.wait(timeout=1)
    except subprocess.TimeoutExpired:
      processus.kill()
      processus.wait(timeout=1)


def parler(texte: str, annulation: threading.Event) -> None:
  """Lecture française locale, interrompable et sans interpréteur de commandes."""
  if annulation.is_set() or not texte.strip():
    return
  executable = shutil.which("espeak-ng")
  if not executable:
    raise RuntimeError("Lecture vocale indisponible : installer espeak-ng avec omarchy-setup-liha --voix.")
  # Le texte reste sur stdin, jamais parmi les options ni dans une commande shell.
  contenu = " ".join(texte.replace("\x00", "").split())[:LONGUEUR_SYNTHESE].encode("utf-8")
  processus = subprocess.Popen(
    [executable, "-v", "fr", "-a", "80", "-s", "160", "-b", "1", "--stdin"],
    stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    shell=False,
  )
  echeance = time.monotonic() + DUREE_SYNTHESE
  try:
    while True:
      if annulation.is_set():
        return
      if time.monotonic() >= echeance:
        raise RuntimeError("Lecture vocale arrêtée après deux minutes.")
      try:
        processus.communicate(input=contenu, timeout=0.1)
        if processus.returncode:
          raise RuntimeError("La lecture vocale a échoué : vérifier la sortie audio.")
        return
      except subprocess.TimeoutExpired:
        # communicate conserve l'entrée non encore écrite après un timeout.
        contenu = None
  finally:
    _arreter_processus(processus)
    if processus.stdin:
      processus.stdin.close()
