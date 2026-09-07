"""Frontière d'autorisation locale, indépendante des réponses du modèle."""

import json
from pathlib import Path
import re


class Refus(ValueError):
  """Action non permise par le contrat local."""


APPLICATIONS = {
  "code": ("code",),
  "terminal": ("xdg-terminal-exec",),
  "blender": ("blender",),
  "unreal": ("UnrealEditor",),
  "obs": ("obs",),
  "audacity": ("audacity",),
  "kdenlive": ("kdenlive",),
  "navigateur": ("omarchy-launch-browser",),
  "fichiers": ("nautilus",),
}

OUTILS = [
  {"nom": "ouvrir_application", "description": "Ouvre une application du catalogue, sans commande ni option arbitraire.", "arguments": {"application": "nom du catalogue", "chemin": "dossier relatif facultatif, seulement code ou fichiers"}},
  {"nom": "lister_fenetres", "description": "Liste les fenêtres du bureau Hyprland.", "arguments": {}},
  {"nom": "focaliser_fenetre", "description": "Active une fenêtre existante.", "arguments": {"adresse": "adresse 0x... retournée par lister_fenetres"}},
  {"nom": "lister_fichiers", "description": "Liste jusqu'à 200 fichiers du dossier autorisé, hors secrets et liens.", "arguments": {"chemin": "chemin relatif, . par défaut"}},
  {"nom": "creer_dossier", "description": "Crée un dossier et ses parents dans le dossier de travail autorisé.", "arguments": {"chemin": "chemin relatif"}},
  {"nom": "lire_fichier", "description": "Lit un fichier texte UTF-8 de 64 Kio maximum dans le dossier autorisé.", "arguments": {"chemin": "chemin relatif"}},
  {"nom": "ecrire_fichier", "description": "Écrit un fichier texte dans le dossier autorisé. Sauvegarde avant remplacement. Configuration d'exécution et secrets interdits.", "arguments": {"chemin": "chemin relatif", "contenu": "texte UTF-8, 64 Kio maximum"}},
  {"nom": "commande", "description": "Exécute une commande Bash affichée intégralement et TOUJOURS soumise à confirmation humaine ; peut agir hors du dossier. Jamais de privilèges administrateur automatiques.", "arguments": {"commande": "commande Bash exacte, 4000 caractères maximum"}},
]

# Une liste d'actions bornées, et non une estimation du danger par le modèle.
AUTONOMES = frozenset({"ouvrir_application", "lister_fenetres", "focaliser_fenetre", "lister_fichiers", "creer_dossier", "lire_fichier", "ecrire_fichier"})
INTERDITS = frozenset({
  "agents.md", "skill.md", "claude.md", "gemini.md", "codex.md", "copilot-instructions.md",
  "makefile", "gnumakefile", "cmakelists.txt", "dockerfile", "compose.yml", "compose.yaml",
  "package.json", "pyproject.toml", "setup.py", "setup.cfg", "cargo.toml", "build.rs",
  "justfile", "taskfile.yml", "taskfile.yaml", "requirements.txt",
  "id_rsa", "id_ed25519", "credentials", "credentials.json", "secrets", "secrets.json",
  "passwd", "shadow", "authorized_keys", "known_hosts", "settings.json", "tasks.json",
})
SUFFIXES_INTERDITS = frozenset({".pem", ".key", ".p12", ".pfx", ".kdbx", ".env", ".desktop", ".service", ".socket", ".timer", ".code-workspace"})
MOTIF_SECRET = re.compile(r"(?i)(?:-----BEGIN [A-Z ]*PRIVATE KEY-----|\b(?:sk|ghp|github_pat|xai)-[A-Za-z0-9_-]{16,}|\bghp_[A-Za-z0-9]{20,}|\b(?:api[_-]?key|access[_-]?token|password|mot[_ -]?de[_ -]?passe)\s*[:=]\s*[\"']?[^\s\"']{8,})")


def sans_secret(texte):
  if MOTIF_SECRET.search(texte):
    raise Refus("Contenu susceptible de contenir un secret : accès refusé.")
  return texte


def dossier_autorise(valeur):
  if not isinstance(valeur, str) or not valeur.strip() or len(valeur) > 4096:
    raise Refus("Choisis un dossier de travail existant.")
  chemin = Path(valeur).expanduser()
  if not chemin.is_absolute():
    raise Refus("Le dossier de travail doit être un chemin absolu.")
  if any(p.is_symlink() for p in (chemin, *chemin.parents)):
    raise Refus("Le dossier de travail ne doit pas traverser de lien symbolique.")
  chemin = chemin.resolve(strict=True)
  if not chemin.is_dir():
    raise Refus("Le dossier de travail doit être un dossier existant.")
  if chemin == Path(chemin.anchor) or chemin == Path.home().resolve():
    raise Refus("Choisis un dossier de projet précis, pas la racine ou tout ton dossier personnel.")
  if any(p.name.startswith(".") for p in (chemin, *chemin.parents) if p.name):
    raise Refus("Les dossiers cachés ne peuvent pas servir de dossier de travail.")
  if str(chemin) in {"/etc", "/usr", "/var", "/boot", "/root", "/proc", "/sys", "/dev", "/run"} or any(str(p) in {"/etc", "/usr", "/var", "/boot", "/root", "/proc", "/sys", "/dev", "/run"} for p in chemin.parents):
    raise Refus("Les dossiers du système ne peuvent pas servir de dossier de travail.")
  return chemin


def chemin_autorise(dossier, valeur, ecriture=False):
  if not isinstance(valeur, str) or not valeur or len(valeur) > 1024 or "\x00" in valeur:
    raise Refus("Chemin relatif invalide.")
  relatif = Path(valeur)
  if relatif.is_absolute() or "\\" in valeur or ":" in valeur or ".." in relatif.parts:
    raise Refus("Le chemin doit rester relatif au dossier autorisé, sans remontée.")
  for partie in relatif.parts:
    nom = partie.lower()
    if nom.startswith(".") or nom in INTERDITS or Path(nom).suffix in SUFFIXES_INTERDITS or any(mot in nom for mot in ("secret", "credential", "token", "password")):
      raise Refus("Chemin réservé, configuration d'exécution ou secret : accès refusé.")
  candidat = dossier / relatif
  for parent in (candidat, *candidat.parents):
    if parent == dossier.parent:
      break
    if parent.is_symlink():
      raise Refus("Les liens symboliques ne sont pas autorisés.")
  cible = candidat.resolve()
  if cible != dossier and dossier not in cible.parents:
    raise Refus("Le chemin sort du dossier autorisé.")
  if cible.exists() and cible.is_file() and cible.stat().st_nlink > 1:
    raise Refus("Les fichiers avec plusieurs liens physiques ne sont pas autorisés.")
  if ecriture and (cible == dossier or (cible.exists() and not cible.is_file())):
    raise Refus("La cible doit être un fichier texte.")
  return cible


def proposition_validee(proposition, dossier):
  if not isinstance(proposition, dict) or set(proposition) - {"reponse", "actions"}:
    raise Refus("Réponse du fournisseur invalide.")
  reponse = proposition.get("reponse", "")
  actions = proposition.get("actions", [])
  if not isinstance(reponse, str) or len(reponse) > 16000 or not isinstance(actions, list) or len(actions) > 6:
    raise Refus("Réponse ou nombre d'actions hors limites.")
  sans_secret(reponse)
  copie = json.loads(json.dumps(actions, ensure_ascii=False))
  for action in copie:
    if not isinstance(action, dict) or set(action) != {"outil", "arguments"}:
      raise Refus("Chaque action doit contenir uniquement outil et arguments.")
    outil, arguments = action["outil"], action["arguments"]
    if not isinstance(outil, str) or not isinstance(arguments, dict):
      raise Refus("Action invalide.")
    schemas = {
      "ouvrir_application": ({"application"}, {"chemin"}),
      "lister_fenetres": (set(), set()),
      "focaliser_fenetre": ({"adresse"}, set()),
      "lister_fichiers": (set(), {"chemin"}),
      "creer_dossier": ({"chemin"}, set()),
      "lire_fichier": ({"chemin"}, set()),
      "ecrire_fichier": ({"chemin", "contenu"}, set()),
      "commande": ({"commande"}, set()),
    }
    if outil not in schemas:
      raise Refus("Outil inconnu : aucune exécution.")
    requis, optionnels = schemas[outil]
    if not requis <= set(arguments) or set(arguments) - requis - optionnels or any(not isinstance(v, str) for v in arguments.values()):
      raise Refus("Arguments invalides pour " + outil + ".")
    if outil == "ouvrir_application":
      if arguments["application"] not in APPLICATIONS:
        raise Refus("Application absente du catalogue.")
      if "chemin" in arguments:
        if arguments["application"] not in {"code", "fichiers"}:
          raise Refus("Cette application s'ouvre sans fichier ni option dans cette version.")
        if not chemin_autorise(dossier, arguments["chemin"]).is_dir():
          raise Refus("L'application doit ouvrir un dossier existant.")
    elif outil in {"lire_fichier", "lister_fichiers", "creer_dossier", "ecrire_fichier"}:
      cible = chemin_autorise(dossier, arguments.get("chemin", "."), outil == "ecrire_fichier")
      if outil == "ecrire_fichier":
        if len(arguments["contenu"].encode("utf-8")) > 65536:
          raise Refus("Écriture limitée à 64 Kio.")
        sans_secret(arguments["contenu"])
    elif outil == "focaliser_fenetre" and not re.fullmatch(r"0x[0-9a-fA-F]{1,16}", arguments["adresse"]):
      raise Refus("Adresse de fenêtre invalide.")
    elif outil == "commande":
      commande = arguments["commande"]
      if not commande.strip() or len(commande) > 4000 or "\x00" in commande:
        raise Refus("Commande vide ou trop longue.")
      sans_secret(commande)
  return {"reponse": reponse, "actions": copie}


def doit_confirmer(actions, mode, dossier):
  if mode not in {"approbation", "complet"}:
    raise Refus("Mode d'autorisation inconnu.")
  if not actions:
    return False
  if mode == "approbation":
    return True
  for action in actions:
    if action["outil"] not in AUTONOMES:
      return True
  return False
