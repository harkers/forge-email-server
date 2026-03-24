#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../app/public"
python3 -m http.server 4173
