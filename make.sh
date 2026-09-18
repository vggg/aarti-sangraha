#!/usr/bin/env bash
# Rebuild everything from source/aarti_master.json.
# The master is read-only to this pipeline; build.py refuses to run if its hash moved.
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="$PWD/build"

echo "==> US Letter large-print edition"
SPREAD=1 python3 build/build.py
python3 build/render.py
python3 build/validate.py Aarti_Sangraha_Letter_LargePrint.pdf

echo "==> A5 spreads"
PAGE=A5 SPREAD=1 python3 build/build.py
python3 build/render2.py booklet_a5.html Aarti_A5_pages.pdf 148mm 210mm
python3 build/validate.py Aarti_A5_pages.pdf

echo "==> Imposed A4 booklet"
python3 build/impose.py
python3 build/validate.py Aarti_Sangraha_A4_Booklet.pdf
python3 build/check_imposition.py

echo "==> QR"
python3 build/make_qr.py "${SITE_URL:?set SITE_URL to your published Pages URL}"

echo "==> done"
