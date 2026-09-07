#!/bin/bash

set -euo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/base-test.sh"
require_command jq
require_command rg
require_command timeout

liha_test_base=$(realpath -- "${TMPDIR:-/tmp}")
liha_test_tmp=$(mktemp -d "$liha_test_base/liha-installation.XXXXXXXX")

nettoyer() {
  local chemin
  chemin=$(realpath -- "$liha_test_tmp")
  if [[ $chemin == "$liha_test_base"/liha-installation.* && $chemin != "$liha_test_base" ]]; then
    rm -rf -- "$chemin"
  fi
}
trap nettoyer EXIT

mkdir -p "$liha_test_tmp/bin"
cat > "$liha_test_tmp/bin/omarchy-shell" <<'SH'
#!/bin/bash
set -euo pipefail
case "$*" in
  "shell rescanPlugins")
    printf 'rescan\n' >> "$LIHA_TEST_JOURNAL"
    printf '0\n' > "$LIHA_TEST_COMPTE"
    ;;
  "shell listPlugins")
    tentative=$(<"$LIHA_TEST_COMPTE")
    tentative=$((tentative + 1))
    printf '%s\n' "$tentative" > "$LIHA_TEST_COMPTE"
    if (( LIHA_TEST_SEUIL > 0 && tentative >= LIHA_TEST_SEUIL )); then
      printf 'liste %s presente\n' "$tentative" >> "$LIHA_TEST_JOURNAL"
      printf '[{"id":"blowvizion.liha","enabled":false}]\n'
    else
      printf 'liste %s absente\n' "$tentative" >> "$LIHA_TEST_JOURNAL"
      printf '[{"id":"omarchy.menu","enabled":true}]\n'
    fi
    ;;
  *)
    printf 'Appel IPC inattendu : %s\n' "$*" >&2
    exit 90
    ;;
esac
SH

cat > "$liha_test_tmp/bin/omarchy-plugin-enable" <<'SH'
#!/bin/bash
set -euo pipefail
if ! rg -q '^liste [0-9]+ presente$' "$LIHA_TEST_JOURNAL"; then
  printf 'activation-prematuree\n' >> "$LIHA_TEST_JOURNAL"
  exit 91
fi
printf 'activation %s\n' "$*" >> "$LIHA_TEST_JOURNAL"
SH

cat > "$liha_test_tmp/bin/sleep" <<'SH'
#!/bin/bash
set -euo pipefail
(( $# == 1 )) && [[ $1 == "0.25" ]] || exit 92
printf 'attente %s\n' "$1" >> "$LIHA_TEST_JOURNAL"
SH

for commande in omarchy-pkg-add python3; do
  cat > "$liha_test_tmp/bin/$commande" <<'SH'
#!/bin/bash
printf 'interdit %s\n' "${0##*/}" >> "$LIHA_TEST_JOURNAL"
exit 93
SH
done
chmod +x "$liha_test_tmp/bin/"*

creer_source() {
  local source=$1
  mkdir -p "$source/shell/plugins/liha/backend" "$source/bin"
  printf '{"id":"blowvizion.liha"}\n' > "$source/shell/plugins/liha/manifest.json"
  printf '# Moteur de test, jamais exécuté.\n' > "$source/shell/plugins/liha/backend/moteur.py"
  printf '#!/bin/bash\nexit 94\n' > "$source/bin/omarchy-launch-liha"
}

nouveau_cas() {
  liha_cas="$liha_test_tmp/$1"
  liha_utilisateur="$liha_cas/utilisateur"
  liha_systeme="$liha_cas/systeme"
  liha_source="$liha_cas/source personnelle"
  liha_journal="$liha_cas/appels"
  liha_sortie="$liha_cas/sortie"
  mkdir -p "$liha_utilisateur" "$liha_systeme" "$liha_cas/configuration-alternative" "$liha_cas/donnees"
  : > "$liha_journal"
  creer_source "$liha_source"
  liha_seuil=1
}

installer() {
  timeout 15 env HOME="$liha_utilisateur" OMARCHY_PATH="$liha_systeme" \
    XDG_CONFIG_HOME="$liha_cas/configuration-alternative" XDG_DATA_HOME="$liha_cas/donnees" \
    PATH="$liha_test_tmp/bin:$PATH" LIHA_TEST_JOURNAL="$liha_journal" \
    LIHA_TEST_COMPTE="$liha_cas/consultations" LIHA_TEST_SEUIL="$liha_seuil" \
    bash "$ROOT/bin/omarchy-setup-liha" "$@" > "$liha_sortie" 2>&1
}

compter() {
  local nombre
  nombre=$(rg -c "$1" "$liha_journal" || true)
  printf '%s' "${nombre:-0}"
}

verifier_activation() {
  local activations
  activations=$(compter '^activation blowvizion\.liha --section right$')
  (( activations == 1 )) || fail "LIHA doit être activée exactement une fois" "$(cat "$liha_journal")"
  ! rg -q '^(activation-prematuree|interdit)' "$liha_journal" || fail "une étape interdite ou prématurée a été appelée"
}

nouveau_cas integree
creer_source "$liha_systeme"
installer || fail "installation de la source intégrée" "$(cat "$liha_sortie")"
cible="$liha_utilisateur/.config/omarchy/plugins/blowvizion.liha"
[[ ! -e $cible && ! -L $cible ]] || fail "la source intégrée ne doit pas créer une seconde extension"
cmp -s "$liha_systeme/bin/omarchy-launch-liha" "$liha_utilisateur/.local/bin/omarchy-launch-liha" || fail "le lanceur intégré doit être installé"
[[ -f $liha_cas/donnees/applications/blowvizion-liha.desktop ]] || fail "le raccourci d'application doit être installé"
[[ ! -e $liha_cas/configuration-alternative/omarchy ]] || fail "le registre doit utiliser HOME/.config, pas XDG_CONFIG_HOME"
verifier_activation
pass "LIHA intégrée : lanceur et raccourci installés sans extension dupliquée"

: > "$liha_journal"
installer || fail "reconfiguration de la source intégrée" "$(cat "$liha_sortie")"
[[ ! -e $cible && ! -L $cible ]] || fail "la reconfiguration intégrée ne doit pas dupliquer l'extension"
verifier_activation
pass "LIHA peut être reconfigurée depuis la même source intégrée"

nouveau_cas cible_preservee
cible="$liha_utilisateur/.config/omarchy/plugins/blowvizion.liha"
mkdir -p "$cible"
printf 'installation personnelle à préserver\n' > "$cible/temoin"
if installer --source "$liha_source"; then
  fail "une cible LIHA différente doit être refusée"
fi
[[ -d $cible && ! -L $cible ]] || fail "la cible différente a été remplacée"
[[ $(<"$cible/temoin") == "installation personnelle à préserver" ]] || fail "le contenu de la cible différente a été modifié"
[[ ! -s $liha_journal ]] || fail "le registre ne doit pas être modifié après un conflit de cible"
pass "LIHA préserve et refuse une cible existante différente"

nouveau_cas doublon_integre
creer_source "$liha_systeme"
if installer --source "$liha_source"; then
  fail "un clone concurrent à une extension intégrée doit être refusé"
fi
[[ ! -s $liha_journal ]] || fail "le registre ne doit pas activer un clone concurrent"
pass "LIHA refuse deux sources concurrentes du même identifiant"

# Git Bash peut copier au lieu de créer un lien : ne pas annoncer ce cas validé.
mkdir -p "$liha_test_tmp/sonde-source"
if ln -s "$liha_test_tmp/sonde-source" "$liha_test_tmp/sonde-lien" 2>/dev/null && [[ -L $liha_test_tmp/sonde-lien ]]; then
  nouveau_cas clone
  installer --source "$liha_source" || fail "installation depuis un clone" "$(cat "$liha_sortie")"
  cible="$liha_utilisateur/.config/omarchy/plugins/blowvizion.liha"
  [[ -L $cible && $(realpath -- "$cible") == "$liha_source/shell/plugins/liha" ]] || fail "le clone doit être lié au chemin du registre"
  [[ ! -e $liha_cas/configuration-alternative/omarchy ]] || fail "le clone doit être découvert dans HOME/.config"
  verifier_activation
  pass "LIHA lie le clone externe au registre, y compris un chemin avec espaces"

  : > "$liha_journal"
  installer --source "$liha_source" || fail "reconfiguration de la même source" "$(cat "$liha_sortie")"
  [[ -L $cible && $(realpath -- "$cible") == "$liha_source/shell/plugins/liha" ]] || fail "la reconfiguration ne doit pas remplacer le lien"
  cmp -s "$liha_source/bin/omarchy-launch-liha" "$liha_utilisateur/.local/bin/omarchy-launch-liha" || fail "la reconfiguration doit conserver un lanceur correct"
  verifier_activation
  pass "LIHA peut être reconfigurée avec la même source"
else
  case "$(uname -s)" in
    MINGW*|MSYS*|CYGWIN*) pass "liens symboliques natifs indisponibles : liaison du clone et reconfiguration de ce lien non vérifiées" ;;
    *) fail "le système ne permet pas de créer les liens symboliques nécessaires au test" ;;
  esac
fi

nouveau_cas decouverte_differee
creer_source "$liha_systeme"
liha_seuil=3
installer || fail "attente de la découverte du registre" "$(cat "$liha_sortie")"
consultations=$(compter '^liste ')
attentes=$(compter '^attente 0\.25$')
(( consultations == 3 && attentes == 2 )) || fail "l'activation doit attendre la découverte effective" "$(cat "$liha_journal")"
verifier_activation
[[ $(tail -n 1 "$liha_journal") == "activation blowvizion.liha --section right" ]] || fail "l'activation doit suivre la dernière consultation"
pass "LIHA attend la découverte effective avant activation"

nouveau_cas registre_absent
creer_source "$liha_systeme"
liha_seuil=0
code=0
installer || code=$?
(( code != 0 && code != 124 )) || fail "l'absence de découverte doit échouer sans dépasser la borne du test"
consultations=$(compter '^liste ')
attentes=$(compter '^attente ')
(( consultations > 0 && consultations <= 20 && attentes <= 20 )) || fail "l'attente de découverte doit être bornée à vingt consultations" "$(cat "$liha_journal")"
activations=$(compter '^activation')
(( activations == 0 )) || fail "aucune activation n'est permise si le registre ne découvre pas LIHA"
rg -q "n'a pas encore chargé LIHA" "$liha_sortie" || fail "l'absence de découverte doit être expliquée"
pass "LIHA échoue explicitement après une attente bornée sans activer une extension absente"
