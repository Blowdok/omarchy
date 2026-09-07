"""Préparation explicite du modèle français Vosk, sans écraser une installation.

Source et licence Apache 2.0 : https://alphacephei.com/vosk/models
Empreinte de l'archive officielle vérifiée le 7 septembre 2026.
"""

from __future__ import annotations

import ctypes
import hashlib
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
import tempfile
import time
import urllib.parse
import urllib.request
import zipfile

from voix import chemin_modele, modele_present


NOM_MODELE = "vosk-model-small-fr-0.22"
ADRESSE_MODELE = f"https://alphacephei.com/vosk/models/{NOM_MODELE}.zip"
EMPREINTE_MODELE = "cabf6180e177eb9b3a9a9d43a437bd5e549f3a7d09525e5d69a3fed787be12ad"
TAILLE_ARCHIVE_MAXIMALE = 64 * 1024 * 1024
TAILLE_EXTRAITE_MAXIMALE = 128 * 1024 * 1024
DUREE_TELECHARGEMENT_MAXIMALE = 300


class RedirectionOfficielle(urllib.request.HTTPRedirectHandler):
  def redirect_request(self, requete, fichier, code, message, entetes, nouvelle_url):
    destination = urllib.parse.urlsplit(nouvelle_url)
    if destination.scheme != "https" or destination.netloc != "alphacephei.com":
      raise RuntimeError("Redirection du modèle refusée : le téléchargement doit rester sur le site officiel HTTPS.")
    return super().redirect_request(requete, fichier, code, message, entetes, nouvelle_url)


def telecharger(destination: Path) -> None:
  empreinte = hashlib.sha256()
  total = 0
  echeance = time.monotonic() + DUREE_TELECHARGEMENT_MAXIMALE
  client = urllib.request.build_opener(RedirectionOfficielle())
  with client.open(ADRESSE_MODELE, timeout=20) as reponse, destination.open("xb") as sortie:
    while True:
      if time.monotonic() >= echeance:
        raise RuntimeError("Téléchargement du modèle trop long : réessayer ultérieurement.")
      bloc = reponse.read(1024 * 1024)
      if not bloc:
        break
      total += len(bloc)
      if total > TAILLE_ARCHIVE_MAXIMALE:
        raise RuntimeError("Archive du modèle trop volumineuse : téléchargement interrompu.")
      empreinte.update(bloc)
      sortie.write(bloc)
  if empreinte.hexdigest() != EMPREINTE_MODELE:
    raise RuntimeError("L'empreinte SHA-256 du modèle diffère de la version vérifiée : installation refusée.")


def extraire_archive(archive: Path, destination: Path) -> Path:
  """Valide toutes les entrées avant extraction dans un répertoire privé vide."""
  if any(destination.iterdir()):
    raise RuntimeError("Le répertoire temporaire d'extraction doit être vide.")
  with zipfile.ZipFile(archive) as fichier_zip:
    entrees = fichier_zip.infolist()
    if not entrees or len(entrees) > 1000:
      raise RuntimeError("Nombre de fichiers inattendu dans le modèle.")
    if sum(entree.file_size for entree in entrees) > TAILLE_EXTRAITE_MAXIMALE:
      raise RuntimeError("Modèle décompressé trop volumineux.")
    noms = set()
    for entree in entrees:
      nom = entree.orig_filename
      chemin = PurePosixPath(nom)
      mode = stat.S_IFMT(entree.external_attr >> 16)
      if (
        not nom or "\x00" in nom or "\\" in nom or ":" in nom
        or chemin.is_absolute() or ".." in chemin.parts
        or any(partie in ("", ".") for partie in nom.rstrip("/").split("/"))
        or chemin.parts[0] != NOM_MODELE
        or mode not in (0, stat.S_IFDIR, stat.S_IFREG)
        or bool(entree.flag_bits & 1)
      ):
        raise RuntimeError("Archive du modèle refusée : chemin, lien ou type de fichier dangereux.")
      cle = str(chemin).casefold()
      if cle in noms:
        raise RuntimeError("Archive du modèle refusée : fichier dupliqué.")
      noms.add(cle)
      cible = destination.joinpath(*chemin.parts).resolve()
      if not cible.is_relative_to(destination.resolve()):
        raise RuntimeError("Archive du modèle refusée : chemin sortant du répertoire temporaire.")
    for entree in entrees:
      cible = destination.joinpath(*PurePosixPath(entree.filename).parts)
      if entree.is_dir():
        cible.mkdir(parents=True, exist_ok=True)
      else:
        cible.parent.mkdir(parents=True, exist_ok=True)
        with fichier_zip.open(entree) as entree_binaire, cible.open("xb") as sortie:
          shutil.copyfileobj(entree_binaire, sortie, length=1024 * 1024)
  modele = destination / NOM_MODELE
  if not modele_present(modele):
    raise RuntimeError("Archive du modèle incomplète : les fichiers de reconnaissance sont absents.")
  return modele


def publier_sans_ecraser(source: Path, destination: Path) -> None:
  """Publication atomique sans remplacement, même si deux préparations concourent.

  Sous Linux, renameat2(RENAME_NOREPLACE) protège aussi les dossiers vides :
  https://man7.org/linux/man-pages/man2/rename.2.html
  """
  if os.name == "nt":
    os.rename(source, destination)  # Sous Windows, une destination existante est refusée.
  elif sys.platform.startswith("linux"):
    bibliotheque = ctypes.CDLL(None, use_errno=True)
    try:
      renommer = bibliotheque.renameat2
    except AttributeError as erreur:
      raise RuntimeError("Publication atomique indisponible : renameat2 est requis.") from erreur
    renommer.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
    renommer.restype = ctypes.c_int
    if renommer(-100, os.fsencode(source), -100, os.fsencode(destination), 1) != 0:
      numero = ctypes.get_errno()
      raise OSError(numero, os.strerror(numero), str(destination))
  else:
    raise RuntimeError("Préparation du modèle prise en charge sous Linux et Windows uniquement.")


def preparer() -> bool:
  """Renvoie False si le modèle existe déjà, True après une nouvelle installation."""
  destination = chemin_modele().absolute()
  if destination.exists() or destination.is_symlink():
    if modele_present(destination):
      return False
    raise RuntimeError("Le chemin du modèle existe mais est incomplet : aucun fichier n'a été remplacé.")
  destination.parent.mkdir(parents=True, exist_ok=True)
  with tempfile.TemporaryDirectory(prefix=".liha-voix-", dir=destination.parent) as temporaire:
    racine = Path(temporaire)
    archive = racine / "modele.zip"
    telecharger(archive)
    extraction = racine / "extraction"
    extraction.mkdir()
    modele = extraire_archive(archive, extraction)
    publier_sans_ecraser(modele, destination)
  return True


def main() -> int:
  try:
    if preparer():
      print("Modèle français Vosk installé ; la dictée reste locale et le microphone reste fermé.")
    else:
      print("Modèle français déjà présent ; aucun téléchargement ni remplacement.")
    return 0
  except (OSError, RuntimeError, zipfile.BadZipFile) as erreur:
    print(f"Préparation vocale interrompue : {erreur}", file=sys.stderr)
    return 1


if __name__ == "__main__":
  sys.exit(main())
