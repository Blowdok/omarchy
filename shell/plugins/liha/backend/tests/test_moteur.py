"""Tests locaux sans modèle, microphone ou session graphique réels."""

import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import threading
import time
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from actions import Annulation, executer, processus_borne
from moteur import Moteur
from politique import Refus, chemin_autorise, doit_confirmer, dossier_autorise, proposition_validee


class VoixFictive:
  def diagnostiquer(self):
    return {"dictee": True, "synthese": True, "detail": "Essai", "nom_voix": "Essai"}

  def dicter(self, annulation):
    return "Ouvre mon projet."

  def parler(self, texte, annulation):
    return None


class TestPolitique(unittest.TestCase):
  def setUp(self):
    self.temporaire = tempfile.TemporaryDirectory(prefix="liha-test-")
    self.addCleanup(self.temporaire.cleanup)
    self.dossier = Path(self.temporaire.name).resolve()

  def test_dossier_precis(self):
    self.assertEqual(dossier_autorise(str(self.dossier)), self.dossier)
    for chemin in (str(Path.home()), self.dossier.anchor, "relatif"):
      with self.subTest(chemin=chemin), self.assertRaises(Refus):
        dossier_autorise(chemin)

  def test_traversee_secrets_et_configuration_interdits(self):
    for chemin in ("../autre", "/etc/passwd", "C:/Windows", "dossier\\autre", ".env", ".ssh/id_rsa", "AGENTS.md", "SKILL.md", "package.json", "config/settings.json", "service.desktop", "mot-de-passe/credentials.json"):
      with self.subTest(chemin=chemin), self.assertRaises(Refus):
        chemin_autorise(self.dossier, chemin)

  def test_liens_physiques_interdits(self):
    origine = self.dossier / "origine.txt"
    origine.write_text("texte", encoding="utf-8")
    try:
      os.link(origine, self.dossier / "copie.txt")
    except OSError:
      self.skipTest("Liens physiques indisponibles")
    with self.assertRaises(Refus):
      chemin_autorise(self.dossier, "copie.txt")

  def test_lien_symbolique_interdit(self):
    (self.dossier / "vrai").mkdir()
    try:
      (self.dossier / "lien").symlink_to(self.dossier / "vrai", target_is_directory=True)
    except OSError:
      self.skipTest("Création de liens symboliques non autorisée sur cette machine")
    with self.assertRaises(Refus):
      chemin_autorise(self.dossier, "lien/document.txt")

  def test_arguments_non_prevus_refuses(self):
    propositions = [
      {"outil": "ouvrir_application", "arguments": {"application": "terminal", "commande": "effacer"}},
      {"outil": "ouvrir_application", "arguments": {"application": "blender", "chemin": "scene.blend"}},
      {"outil": "focaliser_fenetre", "arguments": {"adresse": "0x01;exec bash"}},
      {"outil": "approuver", "arguments": {"accord": True}},
    ]
    for action in propositions:
      with self.subTest(action=action), self.assertRaises(Refus):
        proposition_validee({"actions": [action]}, self.dossier)

  def test_commande_confirmee_dans_les_deux_modes(self):
    action = {"outil": "commande", "arguments": {"commande": "printf bonjour"}}
    for mode in ("approbation", "complet"):
      self.assertTrue(doit_confirmer([action], mode, self.dossier))
    with self.assertRaises(Refus):
      executer(action, self.dossier, threading.Event())

  def test_ecriture_code_complete_avec_sauvegarde(self):
    cible = self.dossier / "exemple.py"
    cible.write_text("ancien\n", encoding="utf-8")
    action = {"outil": "ecrire_fichier", "arguments": {"chemin": "exemple.py", "contenu": "nouveau\n"}}
    self.assertFalse(doit_confirmer([action], "complet", self.dossier))
    self.assertTrue(doit_confirmer([action], "approbation", self.dossier))
    resultat = executer(action, self.dossier, threading.Event(), remplacement_autorise=True)
    self.assertEqual(cible.read_text(encoding="utf-8"), "nouveau\n")
    self.assertEqual((self.dossier / resultat["sauvegarde"]).read_text(encoding="utf-8"), "ancien\n")

  def test_ecriture_sans_approbation_ne_remplace_pas(self):
    cible = self.dossier / "notes.txt"
    cible.write_text("ancien", encoding="utf-8")
    with self.assertRaises(Refus):
      executer({"outil": "ecrire_fichier", "arguments": {"chemin": "notes.txt", "contenu": "nouveau"}}, self.dossier, threading.Event())
    self.assertEqual(cible.read_text(encoding="utf-8"), "ancien")

  def test_lecture_et_limite(self):
    cible = self.dossier / "notes.txt"
    cible.write_text("Bonjour", encoding="utf-8")
    action = {"outil": "lire_fichier", "arguments": {"chemin": "notes.txt"}}
    self.assertEqual(executer(action, self.dossier, threading.Event())["contenu"], "Bonjour")
    cible.write_bytes(b"x" * 65537)
    with self.assertRaises(Refus):
      executer(action, self.dossier, threading.Event())

  def test_secret_dans_contenu_masque(self):
    cible = self.dossier / "notes.txt"
    cible.write_text("-----BEGIN PRIVATE KEY-----", encoding="utf-8")
    with self.assertRaises(Refus):
      executer({"outil": "lire_fichier", "arguments": {"chemin": "notes.txt"}}, self.dossier, threading.Event())

  def test_creer_dossier_et_parent(self):
    action = {"outil": "creer_dossier", "arguments": {"chemin": "projet/sources"}}
    executer(action, self.dossier, threading.Event())
    self.assertTrue((self.dossier / "projet" / "sources").is_dir())

  def test_arret_processus(self):
    annulation = threading.Event()
    minuterie = threading.Timer(0.15, annulation.set)
    minuterie.start()
    try:
      debut = time.monotonic()
      with self.assertRaises(Annulation):
        processus_borne([sys.executable, "-c", "import time; time.sleep(30)"], self.dossier, annulation)
      self.assertLess(time.monotonic() - debut, 3)
    finally:
      minuterie.cancel()

  def test_delai_processus(self):
    with self.assertRaises(Refus):
      processus_borne([sys.executable, "-c", "import time; time.sleep(30)"], self.dossier, threading.Event(), delai=0.1)

  def test_sortie_processus_bornee(self):
    resultat = processus_borne([sys.executable, "-c", "print('x' * 100000)"], self.dossier, threading.Event())
    self.assertEqual(len(resultat["sortie"]), 32768)
    self.assertTrue(resultat["sortie_limitee"])

  def verifier_enfant_gardant_sortie(self, annuler):
    fichier_pid = self.dossier / "enfant.pid"
    code = "import subprocess, sys; from pathlib import Path; enfant=subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(4)'], cwd=Path(sys.argv[1]).anchor); Path(sys.argv[1]).write_text(str(enfant.pid))"
    annulation = threading.Event()
    minuterie = threading.Timer(0.3, annulation.set) if annuler else None
    if minuterie:
      minuterie.start()
    debut = time.monotonic()
    try:
      with self.assertRaises(Annulation if annuler else Refus):
        processus_borne([sys.executable, "-c", code, str(fichier_pid)], self.dossier, annulation, delai=5 if annuler else 0.3)
      self.assertLess(time.monotonic() - debut, 2, "Le parent termine, mais son enfant retient la sortie et bloque l'arrêt.")
    finally:
      if minuterie:
        minuterie.cancel()
      if fichier_pid.exists():
        try:
          os.kill(int(fichier_pid.read_text()), signal.SIGTERM)
        except OSError:
          pass

  def test_arret_apres_fin_parent_avec_enfant(self):
    self.verifier_enfant_gardant_sortie(annuler=True)

  def test_delai_apres_fin_parent_avec_enfant(self):
    self.verifier_enfant_gardant_sortie(annuler=False)


class TestMoteur(unittest.TestCase):
  def setUp(self):
    self.temporaire = tempfile.TemporaryDirectory(prefix="liha-moteur-")
    self.addCleanup(self.temporaire.cleanup)
    self.dossier = self.temporaire.name
    self.evenements = []

  def creer(self, proposer, executant=None, emission=None):
    moteur = Moteur(emission or self.evenements.append, proposer=proposer, executant=executant, service_voix=VoixFictive())
    self.addCleanup(moteur.arreter)
    return moteur

  def commencer(self, moteur, mode="approbation"):
    moteur.requete({"id": "essai", "methode": "discuter", "parametres": {"texte": "Prépare mon projet", "dossier": self.dossier, "mode": mode}})

  def attendre(self, condition):
    limite = time.monotonic() + 3
    while not condition() and time.monotonic() < limite:
      time.sleep(0.01)
    self.assertTrue(condition(), "État attendu non atteint")

  def test_discussion_simple(self):
    moteur = self.creer(lambda *args: {"reponse": "Bonjour Boss.", "actions": []})
    self.commencer(moteur)
    self.attendre(lambda: not moteur.occupe)
    self.assertTrue(any(e.get("texte") == "Bonjour Boss." for e in self.evenements))

  def test_appel_invalide_ne_bloque_pas(self):
    moteur = self.creer(lambda *args: {})
    for requete in ([], {"methode": "approuver", "parametres": {"accord": "oui"}}, {"methode": "inconnu"}):
      moteur.requete(requete)
    self.assertEqual(sum(e["type"] == "erreur" for e in self.evenements), 3)
    self.assertFalse(moteur.occupe)

  def test_approbation_exacte_non_modifiable(self):
    action = {"outil": "ecrire_fichier", "arguments": {"chemin": "notes.txt", "contenu": "original"}}
    propositions = iter([{"reponse": "Je crée le document.", "actions": [action]}, {"reponse": "Terminé.", "actions": []}])
    def emettre(evenement):
      self.evenements.append(evenement)
      if evenement["type"] == "approbation":
        evenement["actions"][0]["arguments"]["contenu"] = "modification non autorisée"
    moteur = self.creer(lambda *args: next(propositions), emission=emettre)
    self.commencer(moteur)
    self.attendre(lambda: moteur.approbation_attendue)
    self.assertFalse((Path(self.dossier) / "notes.txt").exists())
    action["arguments"]["contenu"] = "autre modification"
    moteur.requete({"methode": "approuver", "parametres": {"accord": True}})
    self.attendre(lambda: not moteur.occupe)
    self.assertEqual((Path(self.dossier) / "notes.txt").read_text(encoding="utf-8"), "original")

  def test_commande_ne_passe_pas_en_mode_complet(self):
    appels = []
    moteur = self.creer(lambda *args: {"actions": [{"outil": "commande", "arguments": {"commande": "commande-test"}}]}, lambda *args, **kwargs: appels.append(args))
    self.commencer(moteur, "complet")
    self.attendre(lambda: moteur.approbation_attendue)
    moteur.requete({"methode": "approuver", "parametres": {"accord": False}})
    self.attendre(lambda: not moteur.occupe)
    self.assertEqual(appels, [])

  def test_mode_complet_edition_code(self):
    fichier = Path(self.dossier) / "projet.py"
    fichier.write_text("ancien", encoding="utf-8")
    propositions = iter([{"actions": [{"outil": "ecrire_fichier", "arguments": {"chemin": "projet.py", "contenu": "nouveau"}}]}, {"actions": []}])
    moteur = self.creer(lambda *args: next(propositions))
    self.commencer(moteur, "complet")
    self.attendre(lambda: not moteur.occupe)
    self.assertEqual(fichier.read_text(encoding="utf-8"), "nouveau")
    self.assertFalse(any(e["type"] == "approbation" for e in self.evenements))

  def test_arret_pendant_attente(self):
    appels = []
    moteur = self.creer(lambda *args: {"actions": [{"outil": "lister_fenetres", "arguments": {}}]}, lambda *args, **kwargs: appels.append(args))
    self.commencer(moteur)
    self.attendre(lambda: moteur.approbation_attendue)
    moteur.requete({"methode": "arreter"})
    moteur.requete({"methode": "approuver", "parametres": {"accord": True}})
    self.attendre(lambda: not moteur.occupe)
    self.assertEqual(appels, [])

  def test_arret_ignore_reponse_tardive(self):
    appels = []
    debut = threading.Event()
    continuer = threading.Event()
    def proposer(*args):
      debut.set()
      continuer.wait(2)
      return {"actions": [{"outil": "lister_fenetres", "arguments": {}}]}
    moteur = self.creer(proposer, lambda *args, **kwargs: appels.append(args))
    self.commencer(moteur, "complet")
    self.attendre(debut.is_set)
    moteur.requete({"methode": "arreter"})
    continuer.set()
    self.attendre(lambda: not moteur.occupe)
    self.assertEqual(appels, [])

  def test_erreur_action_reparee_sans_executer_la_suite(self):
    propositions = iter([
      {"actions": [{"outil": "lire_fichier", "arguments": {"chemin": "absent.txt"}}, {"outil": "ecrire_fichier", "arguments": {"chemin": "ne-pas-creer.txt", "contenu": "non"}}]},
      {"reponse": "Le fichier n'existe pas ; je prépare un nouveau document.", "actions": [{"outil": "ecrire_fichier", "arguments": {"chemin": "nouveau.txt", "contenu": "oui"}}]},
      {"actions": []},
    ])
    moteur = self.creer(lambda *args: next(propositions))
    self.commencer(moteur, "complet")
    self.attendre(lambda: not moteur.occupe)
    self.assertTrue((Path(self.dossier) / "nouveau.txt").exists())
    self.assertFalse((Path(self.dossier) / "ne-pas-creer.txt").exists())

  def test_annulation_fournisseur_sans_erreur(self):
    def proposer(*args):
      raise InterruptedError("Arrêt demandé")
    moteur = self.creer(proposer)
    self.commencer(moteur)
    self.attendre(lambda: not moteur.occupe)
    self.assertFalse(any(e["type"] == "erreur" for e in self.evenements))

  def test_limite_huit_etapes(self):
    appels = []
    def executant(*args, **kwargs):
      appels.append(args)
      return {"resultat": "Essai"}
    moteur = self.creer(lambda *args: {"actions": [{"outil": "lister_fenetres", "arguments": {}}]}, executant)
    self.commencer(moteur, "complet")
    self.attendre(lambda: not moteur.occupe)
    self.assertEqual(len(appels), 8)

  def test_dictee_transcrit_sans_executer(self):
    moteur = self.creer(lambda *args: self.fail("Aucun fournisseur pendant la dictée"))
    moteur.requete({"methode": "dicter"})
    self.attendre(lambda: not moteur.occupe)
    self.assertTrue(any(e["type"] == "transcription" and e["texte"] == "Ouvre mon projet." for e in self.evenements))


if __name__ == "__main__":
  unittest.main()
