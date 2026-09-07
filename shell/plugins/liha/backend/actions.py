"""Actions système explicites. Aucun résultat externe ne devient une instruction."""

import json
import os
from pathlib import Path
import signal
import stat
import subprocess
import threading
import time
import uuid

from politique import APPLICATIONS, Refus, chemin_autorise, proposition_validee, sans_secret


class Annulation(RuntimeError):
  pass


def verifier_annulation(annulation):
  if annulation.is_set():
    raise Annulation("Tâche arrêtée.")


def terminer_processus(processus):
  try:
    if os.name == "posix":
      os.killpg(processus.pid, signal.SIGTERM)
    else:
      processus.terminate()
    processus.wait(timeout=0.5)
  except (ProcessLookupError, OSError):
    pass
  except subprocess.TimeoutExpired:
    try:
      if os.name == "posix":
        os.killpg(processus.pid, signal.SIGKILL)
      else:
        processus.kill()
      processus.wait(timeout=1)
    except (OSError, subprocess.TimeoutExpired):
      pass
  finally:
    if os.name == "posix":
      # Le shell peut déjà être terminé alors qu'un enfant ignore SIGTERM.
      try:
        os.killpg(processus.pid, signal.SIGKILL)
      except (ProcessLookupError, PermissionError):
        pass


def processus_borne(arguments, dossier, annulation, delai=45):
  verifier_annulation(annulation)
  sortie = bytearray()
  environnement = os.environ.copy()
  for nom in ("BASH_ENV", "ENV"):
    environnement.pop(nom, None)
  processus = subprocess.Popen(arguments, cwd=str(dossier), stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, env=environnement, start_new_session=os.name == "posix")
  def lire():
    try:
      while True:
        bloc = processus.stdout.read(4096)
        if not bloc:
          return
        if len(sortie) < 32768:
          sortie.extend(bloc[:32768 - len(sortie)])
    finally:
      # Le lecteur ferme son propre tuyau ; un close depuis l'autre thread
      # attendrait son verrou si un descendant conservait stdout ouvert.
      processus.stdout.close()
  lecteur = threading.Thread(target=lire, daemon=True)
  lecteur.start()
  debut = time.monotonic()
  try:
    # Un shell terminé n'implique pas EOF : ses enfants héritent de stdout.
    while processus.poll() is None or lecteur.is_alive():
      if annulation.wait(0.05):
        terminer_processus(processus)
        raise Annulation("Tâche arrêtée ; processus interrompu.")
      if time.monotonic() - debut > delai:
        terminer_processus(processus)
        raise Refus("Délai maximal de l'action dépassé ; processus interrompu.")
    verifier_annulation(annulation)
    texte = sortie.decode("utf-8", errors="replace")
    # Ne pas afficher les éventuels secrets émis par un programme.
    sans_secret(texte)
    return {"code": processus.returncode, "sortie": texte, "sortie_limitee": len(sortie) >= 32768}
  finally:
    if processus.poll() is None:
      terminer_processus(processus)
    lecteur.join(timeout=0.1)


def ouvrir_application(arguments, dossier, annulation):
  nom = arguments["application"]
  commande = list(APPLICATIONS[nom])
  if nom == "navigateur":
    racine = os.environ.get("OMARCHY_PATH")
    if not racine:
      raise Refus("OMARCHY_PATH doit être défini par la session Omarchy.")
    commande[0] = str(Path(racine) / "bin" / commande[0])
  if "chemin" in arguments:
    commande.append(str(chemin_autorise(dossier, arguments["chemin"])))
  verifier_annulation(annulation)
  processus = subprocess.Popen(commande, cwd=str(dossier), stdin=subprocess.DEVNULL,
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                              start_new_session=os.name == "posix")
  if annulation.wait(0.2):
    terminer_processus(processus)
    raise Annulation("Ouverture interrompue.")
  if processus.poll() not in {None, 0}:
    raise Refus("L'application n'a pas pu démarrer : " + nom + ".")
  # L'application appartient désormais à l'utilisateur ; Arrêter n'en ferme pas les documents.
  threading.Thread(target=processus.wait, daemon=True).start()
  return {"application": nom, "resultat": "Lancement demandé ; vérifier la fenêtre à l'écran."}


def lire_fichier(cible):
  if not stat.S_ISREG(cible.lstat().st_mode):
    raise Refus("Seuls les fichiers ordinaires sont lisibles.")
  drapeaux = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
  descripteur = os.open(cible, drapeaux)
  with os.fdopen(descripteur, "rb") as fichier:
    statut = os.fstat(fichier.fileno())
    if not stat.S_ISREG(statut.st_mode) or statut.st_nlink > 1 or statut.st_size > 65536:
      raise Refus("Fichier trop volumineux ou possédant plusieurs liens physiques.")
    brut = fichier.read(65537)
  if len(brut) > 65536 or b"\x00" in brut:
    raise Refus("Seuls les fichiers texte de 64 Kio maximum sont lisibles.")
  try:
    return sans_secret(brut.decode("utf-8"))
  except UnicodeDecodeError as erreur:
    raise Refus("Le fichier n'est pas un texte UTF-8.") from erreur


def executer(action, dossier, annulation, remplacement_autorise=False):
  verifier_annulation(annulation)
  proposition_validee({"reponse": "", "actions": [action]}, dossier)
  outil, arguments = action["outil"], action["arguments"]
  if outil == "ouvrir_application":
    return ouvrir_application(arguments, dossier, annulation)
  if outil == "lister_fenetres":
    resultat = processus_borne(["hyprctl", "clients", "-j"], dossier, annulation, 5)
    if resultat["code"] != 0:
      raise Refus("La session Hyprland n'est pas disponible.")
    fenetres = json.loads(resultat["sortie"])
    return [{"adresse": f.get("address"), "titre": f.get("title", ""), "application": f.get("class", "")} for f in fenetres[:100]]
  if outil == "focaliser_fenetre":
    return processus_borne(["hyprctl", "dispatch", "focuswindow", "address:" + arguments["adresse"]], dossier, annulation, 5)
  if outil == "commande":
    if not remplacement_autorise:
      raise Refus("Une commande libre exige une approbation humaine explicite.")
    return processus_borne(["/bin/bash", "--noprofile", "--norc", "-c", arguments["commande"]], dossier, annulation)
  cible = chemin_autorise(dossier, arguments.get("chemin", "."), outil == "ecrire_fichier")
  if outil == "creer_dossier":
    verifier_annulation(annulation)
    cible.mkdir(parents=True, exist_ok=True)
    return {"chemin": arguments["chemin"], "resultat": "Dossier disponible."}
  if outil == "lister_fichiers":
    if not cible.is_dir():
      raise Refus("Ce chemin n'est pas un dossier.")
    elements = []
    for enfant in cible.iterdir():
      verifier_annulation(annulation)
      try:
        chemin_autorise(dossier, enfant.relative_to(dossier).as_posix())
      except Refus:
        continue
      elements.append({"nom": enfant.name, "type": "dossier" if enfant.is_dir() else "fichier"})
      if len(elements) >= 200:
        break
    return {"elements": sorted(elements, key=lambda e: e["nom"].casefold()), "limite": 200}
  if outil == "lire_fichier":
    return {"chemin": arguments["chemin"], "contenu": lire_fichier(cible)}
  if outil == "ecrire_fichier":
    contenu = arguments["contenu"].encode("utf-8")
    sauvegarde = None
    if cible.exists():
      if not remplacement_autorise:
        raise Refus("Le fichier existe : son remplacement exige une approbation.")
      statut_initial = cible.stat()
      ancien = lire_fichier(cible)
      sauvegarde = cible.with_name(cible.name + ".liha-sauvegarde-" + uuid.uuid4().hex[:12])
      with sauvegarde.open("xb") as fichier:
        fichier.write(ancien.encode("utf-8"))
      os.chmod(sauvegarde, 0o600)
      temporaire = cible.with_name(cible.name + ".liha-ecriture-" + uuid.uuid4().hex)
      try:
        with temporaire.open("xb") as fichier:
          fichier.write(contenu)
          fichier.flush()
          os.fsync(fichier.fileno())
        os.chmod(temporaire, stat.S_IMODE(statut_initial.st_mode))
        verifier_annulation(annulation)
        chemin_autorise(dossier, arguments["chemin"], True)
        statut_actuel = cible.stat()
        if any(getattr(statut_initial, cle) != getattr(statut_actuel, cle) for cle in ("st_dev", "st_ino", "st_mtime_ns", "st_size")):
          raise Refus("Le fichier a changé pendant l'édition ; remplacement annulé pour préserver tes modifications.")
        os.replace(temporaire, cible)
      finally:
        if temporaire.exists():
          temporaire.unlink()
    else:
      verifier_annulation(annulation)
      # O_EXCL empêche d'écraser un fichier apparu après l'autorisation.
      with cible.open("xb") as fichier:
        fichier.write(contenu)
    return {"chemin": arguments["chemin"], "octets": len(contenu), "sauvegarde": sauvegarde.name if sauvegarde else None}
  raise Refus("Outil inconnu.")
