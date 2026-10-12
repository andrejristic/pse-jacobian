#!/bin/sh
# Pokreni PSE-Jacobian iz njegovog direktorija (da module path radi).
# Ako postoji virtuelno okruženje ~/pse-venv, koristi njegov python automatski;
# u suprotnom padni na sistemski python3.
cd "$(dirname "$0")" || exit 1

if [ -x "$HOME/pse-venv/bin/python" ]; then
    PY="$HOME/pse-venv/bin/python"
else
    PY="python3"
fi

exec "$PY" run.py "$@"
