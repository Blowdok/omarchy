"""Vérifie annulation, absence d'écoute implicite et sûreté des modèles vocaux."""

import hashlib
import io
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import threading
from types import SimpleNamespace
import unittest
from unittest.mock import MagicMock, patch
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import preparer_voix
import voix


class TestVoix(unittest.TestCase):
  def modules(self, annulation=None, resultat="ouvre blender"):
    reconnaissance = MagicMock()
    reconnaissance.AcceptWaveform.return_value = True
    reconnaissance.Result.return_value = '{"text": "' + resultat + '"}'
    reconnaissance.FinalResult.return_value = '{"text": "fin"}'
    if annulation:
      reconnaissance.AcceptWaveform.side_effect = lambda donnees: (annulation.set() or True)
    vosk = MagicMock()
    vosk.KaldiRecognizer.return_value = reconnaissance
    audio = MagicMock()
    audio.query_devices.return_value = {"max_input_channels": 1, "default_samplerate": 48000}

    def ouvrir_flux(**parametres):
      flux = MagicMock()
      flux.__enter__.side_effect = lambda: parametres["callback"](b"\x00\x00", 1, None, False)
      return flux

    audio.RawInputStream.side_effect = ouvrir_flux
    return vosk, audio

  def test_diagnostic_n_ouvre_pas_microphone(self):
    vosk, audio = self.modules()
    with patch.object(voix, "_modules_dictee", return_value=(vosk, audio)), patch.object(
      voix, "modele_present", return_value=True
    ), patch.object(voix.shutil, "which", return_value="/usr/bin/espeak-ng"):
      diagnostic = voix.diagnostiquer()
    self.assertTrue(diagnostic["dictee"])
    self.assertTrue(diagnostic["synthese"])
    self.assertIn("Vivienne n'est pas intégrée", diagnostic["detail"])
    self.assertIn("sans qualité HD", diagnostic["detail"])
    audio.RawInputStream.assert_not_called()
    vosk.Model.assert_not_called()

  def test_diagnostic_absence_composants_est_explicite(self):
    with patch.object(voix, "_modules_dictee", side_effect=RuntimeError("Vosk absent")), patch.object(
      voix.shutil, "which", return_value=None
    ):
      diagnostic = voix.diagnostiquer()
    self.assertFalse(diagnostic["dictee"])
    self.assertFalse(diagnostic["synthese"])
    self.assertIn("Vosk absent", diagnostic["detail"])

  def test_dictee_rend_une_phrase_et_ferme_le_flux(self):
    modules = self.modules()
    with patch.object(voix, "_modules_dictee", return_value=modules), patch.object(
      voix, "modele_present", return_value=True
    ):
      self.assertEqual(voix.dicter(threading.Event()), "ouvre blender")
    self.assertIn("model_path", modules[0].Model.call_args.kwargs)
    self.assertNotIn("lang", modules[0].Model.call_args.kwargs)

  def test_annulation_pendant_dictee_jette_le_texte(self):
    annulation = threading.Event()
    with patch.object(voix, "_modules_dictee", return_value=self.modules(annulation)), patch.object(
      voix, "modele_present", return_value=True
    ):
      self.assertEqual(voix.dicter(annulation), "")

  def test_annulation_avant_dictee_ne_charge_rien(self):
    annulation = threading.Event()
    annulation.set()
    with patch.object(voix, "_modules_dictee") as modules:
      self.assertEqual(voix.dicter(annulation), "")
    modules.assert_not_called()

  def test_dictee_sans_modele_ne_telecharge_pas(self):
    modules = self.modules()
    with patch.object(voix, "_modules_dictee", return_value=modules), patch.object(
      voix, "modele_present", return_value=False
    ):
      with self.assertRaisesRegex(RuntimeError, "Modèle français absent"):
        voix.dicter(threading.Event())
    modules[0].Model.assert_not_called()
    modules[1].RawInputStream.assert_not_called()

  def test_dictee_perte_audio_ne_livre_pas_transcription(self):
    vosk, audio = self.modules()

    def flux_en_perte(**parametres):
      flux = MagicMock()
      flux.__enter__.side_effect = lambda: parametres["callback"](b"\x00\x00", 1, None, True)
      return flux

    audio.RawInputStream.side_effect = flux_en_perte
    with patch.object(voix, "_modules_dictee", return_value=(vosk, audio)), patch.object(
      voix, "modele_present", return_value=True
    ):
      with self.assertRaisesRegex(RuntimeError, "données perdues"):
        voix.dicter(threading.Event())
    vosk.KaldiRecognizer.return_value.Result.assert_not_called()

  def test_dictee_limitee_meme_sans_son(self):
    vosk, audio = self.modules()
    audio.RawInputStream.side_effect = None
    with patch.object(voix, "_modules_dictee", return_value=(vosk, audio)), patch.object(
      voix, "modele_present", return_value=True
    ), patch.object(voix, "DUREE_DICTEE", 0.01):
      self.assertEqual(voix.dicter(threading.Event()), "fin")
    audio.RawInputStream.return_value.__exit__.assert_called_once()

  def test_synthese_transmet_texte_borne_sans_shell(self):
    processus = MagicMock(returncode=0)
    processus.poll.return_value = 0
    texte = "--help ; $(commande) " + "é" * 3000
    with patch.object(voix.shutil, "which", return_value="/usr/bin/espeak-ng"), patch.object(
      voix.subprocess, "Popen", return_value=processus
    ) as ouvrir:
      voix.parler(texte, threading.Event())
    self.assertFalse(ouvrir.call_args.kwargs["shell"])
    self.assertNotIn(texte, ouvrir.call_args.args[0])
    envoye = processus.communicate.call_args.kwargs["input"].decode("utf-8")
    self.assertTrue(envoye.startswith("--help ; $(commande)"))
    self.assertEqual(len(envoye), voix.LONGUEUR_SYNTHESE)

  def test_arret_synthese_termine_et_recolte_processus(self):
    annulation = threading.Event()
    processus = MagicMock()
    processus.poll.return_value = None

    def bloquer(**arguments):
      annulation.set()
      raise subprocess.TimeoutExpired("espeak-ng", 0.1)

    processus.communicate.side_effect = bloquer
    with patch.object(voix.shutil, "which", return_value="/usr/bin/espeak-ng"), patch.object(
      voix.subprocess, "Popen", return_value=processus
    ):
      voix.parler("Bonjour", annulation)
    processus.terminate.assert_called_once()
    processus.wait.assert_called_once()

  def test_modele_respecte_les_chemins_configures(self):
    with patch.dict(voix.os.environ, {"LIHA_MODELE_VOSK": "/modele/personnel"}, clear=True):
      self.assertEqual(voix.chemin_modele(), Path("/modele/personnel"))
    with patch.dict(voix.os.environ, {"XDG_DATA_HOME": "/donnees"}, clear=True):
      self.assertEqual(voix.chemin_modele(), Path("/donnees/liha/modeles/vosk-fr"))


class TestPreparationVoix(unittest.TestCase):
  def setUp(self):
    self.temporaire = tempfile.TemporaryDirectory()
    self.addCleanup(self.temporaire.cleanup)
    self.racine = Path(self.temporaire.name)
    self.archive = self.racine / "modele.zip"
    self.extraction = self.racine / "extraction"
    self.extraction.mkdir()

  def ecrire_archive(self, supplement=None):
    with zipfile.ZipFile(self.archive, "w") as archive:
      for fichier in voix.FICHIERS_MODELE:
        archive.writestr(preparer_voix.NOM_MODELE + "/" + fichier, "modèle simulé")
      if supplement is not None:
        archive.writestr(supplement, "contenu supplémentaire")

  def test_archive_valide_prepare_modele(self):
    self.ecrire_archive()
    modele = preparer_voix.extraire_archive(self.archive, self.extraction)
    self.assertTrue(voix.modele_present(modele))

  def test_archive_chemins_dangereux_refuses_avant_extraction(self):
    for nom in ("../sortie", "/sortie", "C:/sortie", "..\\sortie", "autre/modele", "vosk-model-small-fr-0.22/../../sortie"):
      with self.subTest(nom=nom):
        self.ecrire_archive(nom)
        with self.assertRaisesRegex(RuntimeError, "Archive du modèle refusée"):
          preparer_voix.extraire_archive(self.archive, self.extraction)
        self.assertEqual(list(self.extraction.iterdir()), [])

  def test_archive_lien_symbolique_refuse(self):
    lien = zipfile.ZipInfo(preparer_voix.NOM_MODELE + "/lien")
    lien.create_system = 3
    lien.external_attr = (stat.S_IFLNK | 0o777) << 16
    self.ecrire_archive(lien)
    with self.assertRaisesRegex(RuntimeError, "Archive du modèle refusée"):
      preparer_voix.extraire_archive(self.archive, self.extraction)

  def test_archive_trop_grande_refusee(self):
    self.ecrire_archive()
    with patch.object(preparer_voix, "TAILLE_EXTRAITE_MAXIMALE", 1):
      with self.assertRaisesRegex(RuntimeError, "trop volumineux"):
        preparer_voix.extraire_archive(self.archive, self.extraction)

  def test_publication_ne_remplace_pas_meme_dossier_vide(self):
    source = self.racine / "source"
    destination = self.racine / "destination"
    source.mkdir()
    destination.mkdir()
    (source / "preuve").write_text("préserver", encoding="utf-8")
    with self.assertRaises(OSError):
      preparer_voix.publier_sans_ecraser(source, destination)
    self.assertTrue((source / "preuve").exists())
    self.assertEqual(list(destination.iterdir()), [])

  def test_publication_atomique_modele_complet(self):
    self.ecrire_archive()
    source = preparer_voix.extraire_archive(self.archive, self.extraction)
    destination = self.racine / "destination"
    preparer_voix.publier_sans_ecraser(source, destination)
    self.assertTrue(voix.modele_present(destination))
    self.assertFalse(source.exists())

  def test_modele_existant_evite_reseau(self):
    self.ecrire_archive()
    source = preparer_voix.extraire_archive(self.archive, self.extraction)
    with patch.object(preparer_voix, "chemin_modele", return_value=source), patch.object(
      preparer_voix, "telecharger"
    ) as telechargement:
      self.assertFalse(preparer_voix.preparer())
    telechargement.assert_not_called()

  def test_empreinte_incorrecte_refuse_installation(self):
    client = SimpleNamespace(open=lambda *arguments, **options: io.BytesIO(b"archive modifiee"))
    with patch.object(preparer_voix.urllib.request, "build_opener", return_value=client):
      with self.assertRaisesRegex(RuntimeError, "SHA-256"):
        preparer_voix.telecharger(self.archive)

  def test_telechargement_borne_et_verifie(self):
    contenu = b"archive valide simulee"
    client = SimpleNamespace(open=lambda *arguments, **options: io.BytesIO(contenu))
    with patch.object(preparer_voix.urllib.request, "build_opener", return_value=client), patch.object(
      preparer_voix, "EMPREINTE_MODELE", hashlib.sha256(contenu).hexdigest()
    ):
      preparer_voix.telecharger(self.archive)
    self.assertEqual(self.archive.read_bytes(), contenu)


if __name__ == "__main__":
  unittest.main()
