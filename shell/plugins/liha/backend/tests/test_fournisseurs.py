"""Validation du contrat des fournisseurs, sans réseau ni compte réel."""

import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import fournisseurs


class ContratFournisseurs(unittest.TestCase):
  def test_plan_decode_sans_executer(self):
    proposition = fournisseurs.decoder(json.dumps({"reponse": "Je vais ouvrir Blender.", "actions": [
      {"outil": "ouvrir_application", "arguments_json": '{"application":"blender"}'}]}))
    self.assertEqual(proposition["actions"], [{"outil": "ouvrir_application", "arguments": {"application": "blender"}}])

  def test_approuver_ne_peut_pas_etre_forge(self):
    with self.assertRaises(ValueError):
      fournisseurs.decoder('{"reponse":"ok","actions":[],"accord":true}')

  def test_contrat_refuse_actions_non_objets(self):
    for action in (None, [], {"outil": "commande", "arguments_json": "[]"}):
      with self.subTest(action=action), self.assertRaises(ValueError):
        fournisseurs.decoder(json.dumps({"reponse": "", "actions": [action]}))

  def test_pas_de_cle_api_heritee(self):
    with patch.dict(os.environ, {"OPENAI_API_KEY": "valeur-factice", "XAI_API_KEY": "valeur-factice", "PATH": "outils"}, clear=True):
      self.assertEqual(fournisseurs.environnement(), {"PATH": "outils"})

  def test_grok_environnement_ne_detourne_pas_fournisseur(self):
    with patch.dict(os.environ, {
      "GROK_HOME": "/session-personnelle", "GROK_MODELS_BASE_URL": "https://exemple.invalid",
      "GROK_MODELS_LIST_URL": "https://exemple.invalid/modeles", "GROK_DEFAULT_MODEL": "autre",
      "GROK_AGENT": "/agent-personnel", "GROK_CURSOR_HOOKS_ENABLED": "1", "PATH": "outils",
    }, clear=True):
      self.assertEqual(fournisseurs.environnement(), {"GROK_HOME": "/session-personnelle", "PATH": "outils"})

  def test_codex_configuration_isolee_et_lecture_seule(self):
    commande = fournisseurs.commande_codex("codex", Path("travail"), Path("schema"), Path("sortie"))
    self.assertIn("--ignore-user-config", commande)
    self.assertIn("--ephemeral", commande)
    self.assertEqual(commande[commande.index("--sandbox") + 1], "read-only")
    self.assertIn('forced_login_method="chatgpt"', commande)
    self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", commande)
    self.assertIn("shell_tool", commande)

  def test_aucun_repli_payant(self):
    with self.assertRaises(ValueError):
      fournisseurs.proposer("openrouter", [], {}, threading.Event())

  def test_annulation_avant_creation_processus(self):
    annulation = threading.Event()
    annulation.set()
    with patch.object(fournisseurs.subprocess, "Popen") as lancement, self.assertRaises(InterruptedError):
      fournisseurs.executer(["jamais"], ".", annulation)
    lancement.assert_not_called()

  def test_processus_reel_sortie_utf8(self):
    with tempfile.TemporaryDirectory() as temporaire:
      sortie = fournisseurs.executer([sys.executable, "-X", "utf8", "-c", "print('Réponse française')"], temporaire, threading.Event())
      self.assertIn("Réponse française", sortie)

  def test_processus_reel_arrete(self):
    annulation = threading.Event()
    minuterie = threading.Timer(0.3, annulation.set)
    with tempfile.TemporaryDirectory() as temporaire:
      minuterie.start()
      try:
        with self.assertRaises(InterruptedError):
          fournisseurs.executer([sys.executable, "-c", "import time; time.sleep(20)"], temporaire, annulation)
      finally:
        minuterie.cancel()

  @unittest.skipUnless(os.name == "posix", "Interruption des descendants prévue pour la cible Linux")
  def test_arret_recolte_enfant_meme_apres_fin_du_fournisseur(self):
    annulation = threading.Event()
    minuterie = threading.Timer(0.2, annulation.set)
    programme = "import subprocess,sys; subprocess.Popen([sys.executable,'-c','import time; time.sleep(20)'])"
    debut = time.monotonic()
    minuterie.start()
    try:
      with self.assertRaises(InterruptedError):
        fournisseurs.executer([sys.executable, "-c", programme], ".", annulation, delai=2)
    finally:
      minuterie.cancel()
    self.assertLess(time.monotonic() - debut, 3)

  @unittest.skipUnless(os.name == "posix", "Interruption des descendants prévue pour la cible Linux")
  def test_delai_reste_actif_apres_fin_du_fournisseur(self):
    programme = "import subprocess,sys; subprocess.Popen([sys.executable,'-c','import time; time.sleep(20)'])"
    debut = time.monotonic()
    with self.assertRaisesRegex(RuntimeError, "délai prévu"):
      fournisseurs.executer([sys.executable, "-c", programme], ".", threading.Event(), delai=0.2)
    self.assertLess(time.monotonic() - debut, 3)

  def test_erreur_fournisseur_masquee(self):
    with tempfile.TemporaryDirectory() as temporaire:
      with self.assertRaisesRegex(RuntimeError, "Le fournisseur a échoué") as erreur:
        fournisseurs.executer([sys.executable, "-c", "import sys; print('detail-prive',file=sys.stderr); sys.exit(1)"], temporaire, threading.Event())
      self.assertNotIn("detail-prive", str(erreur.exception))


class ConfigurationGrok(unittest.TestCase):
  def setUp(self):
    self.temporaire = tempfile.TemporaryDirectory()
    self.addCleanup(self.temporaire.cleanup)
    self.racine = Path(self.temporaire.name)
    self.personnel = self.racine / "personnel"
    self.systeme = self.racine / "systeme"
    self.personnel.mkdir()
    self.systeme.mkdir()
    self.enterContext(patch.dict(os.environ, {"GROK_HOME": str(self.personnel)}))
    self.enterContext(patch.object(fournisseurs, "CONFIGURATION_GROK_SYSTEME", self.systeme))

  def test_grok_minimal_accepte_sans_lancement(self):
    (self.personnel / "config.toml").write_text('[models]\ndefault="grok-build"\n[ui]\ntheme="sombre"', encoding="utf-8")
    with patch.object(fournisseurs.subprocess, "Popen") as lancement:
      fournisseurs.verifier_grok()
    lancement.assert_not_called()

  def test_hook_session_hors_config_refuse_avant_fournisseur(self):
    hooks = self.personnel / "hooks"
    hooks.mkdir()
    (hooks / "session.json").write_text('{"hooks":{"SessionStart":[]}}', encoding="utf-8")
    with patch.object(fournisseurs.shutil, "which", return_value="grok"), patch.object(
      fournisseurs.subprocess, "Popen"
    ) as lancement, self.assertRaisesRegex(RuntimeError, "hooks ou extensions"):
      fournisseurs.proposer("grok", [], {}, threading.Event())
    lancement.assert_not_called()

  def test_plugins_et_chemins_hooks_sont_refuses(self):
    for nom in ("plugins", "hooks-paths"):
      with self.subTest(nom=nom):
        cible = self.personnel / nom
        cible.write_text("configuration simulée", encoding="utf-8")
        try:
          with self.assertRaises(RuntimeError):
            fournisseurs.verifier_grok()
        finally:
          cible.unlink()

  def test_toutes_configurations_gerees_sont_refusees(self):
    for racine in (self.personnel, self.systeme):
      for nom in ("managed_config.toml", "requirements.toml"):
        with self.subTest(racine=racine.name, nom=nom):
          fichier = racine / nom
          fichier.write_text("# configuration externe", encoding="utf-8")
          try:
            with self.assertRaisesRegex(RuntimeError, "configuration gérée"):
              fournisseurs.verifier_grok()
          finally:
            fichier.unlink()

  def test_configurations_executables_ou_provider_externe_refusees(self):
    contenus = (
      '[auth]\nauth_provider_command="/outil/personnel"',
      '[hooks]\nSessionStart=[]',
      '[model."grok-build"]\nbase_url="https://exemple.invalid"',
      '[models]\nextra_headers={"personnel"="exemple"}',
      '[[version_overrides]]\nversion=">=0.0.0"',
      '[plugins]\npaths=["/extensions"]',
      '[mcp_servers.exemple]\ncommand="exemple"',
    )
    for contenu in contenus:
      with self.subTest(contenu=contenu):
        (self.personnel / "config.toml").write_text(contenu, encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "hors du périmètre vérifié"):
          fournisseurs.verifier_grok()

  def test_diagnostic_grok_bloque_explique_limite(self):
    (self.personnel / "hooks-paths").write_text("/hooks-personnels", encoding="utf-8")
    with patch.object(fournisseurs.shutil, "which", return_value="client"):
      diagnostic = fournisseurs.diagnostiquer()
    self.assertFalse(diagnostic["grok"]["disponible"])
    self.assertTrue(diagnostic["codex"]["disponible"])
    self.assertIn("personnel n'a pas été modifié", diagnostic["grok"]["detail"])


if __name__ == "__main__":
  unittest.main()
