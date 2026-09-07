#!/bin/bash

set -euo pipefail
source "$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)/base-test.sh"
require_command python3
python3 -m unittest discover -s "$ROOT/shell/plugins/liha/backend/tests" -p 'test_*.py'
pass "moteur LIHA : politique, fournisseurs et voix"
