#!/bin/sh
# Build pse-jacobian_<ver>_all.deb WITHOUT dpkg-deb, using ar + tar + gzip.
# Layout installed:
#   /opt/pse-jacobian/            the app (pse_jacobian/ + run.py)
#   /usr/bin/pse-jacobian         launcher (prefers ~/pse-venv, else python3)
#   /usr/share/applications/…     desktop entry
#   /usr/share/icons/hicolor/…    icon
#   /usr/share/doc/pse-jacobian/  guides + copyright
set -e

PKG=pse-jacobian
VER=0.1.0
ARCH=all

HERE="$(cd "$(dirname "$0")" && pwd)"
APP="$(cd "$HERE/.." && pwd)"          # the app/ directory
BUILD="$HERE/build"
ROOT="$BUILD/root"                     # the data tree (installed filesystem)
DEBIAN="$BUILD/control"                # the control tree

rm -rf "$BUILD"
mkdir -p "$ROOT/opt/$PKG" \
         "$ROOT/usr/bin" \
         "$ROOT/usr/share/applications" \
         "$ROOT/usr/share/icons/hicolor/256x256/apps" \
         "$ROOT/usr/share/doc/$PKG" \
         "$DEBIAN"

# --- app payload (exclude caches / packaging / build) ---
cp -r "$APP/pse_jacobian" "$ROOT/opt/$PKG/"
cp "$APP/run.py" "$ROOT/opt/$PKG/"
cp "$APP/requirements.txt" "$ROOT/opt/$PKG/" 2>/dev/null || true
find "$ROOT/opt/$PKG" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
find "$ROOT/opt/$PKG" -name '*.pyc' -delete 2>/dev/null || true

# --- launcher ---
cat > "$ROOT/usr/bin/$PKG" <<'EOF'
#!/bin/sh
# PSE-Jacobian launcher. Prefer the user's venv if present, else system python3.
APPDIR=/opt/pse-jacobian
if [ -x "$HOME/pse-venv/bin/python" ]; then
    PY="$HOME/pse-venv/bin/python"
else
    PY="python3"
fi
cd "$APPDIR" || exit 1
exec "$PY" run.py "$@"
EOF
chmod 0755 "$ROOT/usr/bin/$PKG"

# --- desktop entry ---
cat > "$ROOT/usr/share/applications/$PKG.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=PSE-Jacobian
Comment=Reproduce & audit the Jacobian Conjecture counterexample
Exec=$PKG
Icon=$PKG
Terminal=false
Categories=Education;Science;Math;
EOF

# --- icon ---
python3 "$HERE/make_icon.py" "$ROOT/usr/share/icons/hicolor/256x256/apps/$PKG.png" \
    >/dev/null 2>&1 || echo "napomena: ikona nije generisana (matplotlib?)"

# --- docs ---
cp "$APP/VODIC_SR.md" "$ROOT/usr/share/doc/$PKG/" 2>/dev/null || true
cp "$APP/GUIDE_EN.md" "$ROOT/usr/share/doc/$PKG/" 2>/dev/null || true
cat > "$ROOT/usr/share/doc/$PKG/copyright" <<EOF
PSE-Jacobian
Copyright (C) 2026 Andrej Ristic / ZeravaTech Inc.
EOF

# --- control metadata ---
ISIZE=$(du -sk "$ROOT" | cut -f1)
cat > "$DEBIAN/control" <<EOF
Package: $PKG
Version: $VER
Section: math
Priority: optional
Architecture: $ARCH
Maintainer: Andrej Ristic <andrej.s.ristic@gmail.com>
Depends: python3
Recommends: python3-pyside6 | python3-pyside6.qtwidgets, python3-sympy, python3-numpy, python3-matplotlib
Installed-Size: $ISIZE
Description: PSE-Jacobian — reproduce & audit the Jacobian Conjecture counterexample
 A PySide6 app that uses a PSE-architecture swarm to independently reproduce and audit
 the Alpoge / Claude Fable 5 counterexample to the Jacobian Conjecture (C^3 -> C^3).
 Tabs: Case, Workbench, Discovery (LLM-in-the-loop), n=2 Frontier, Family, Diagnostics
 (full PSE machinery), Chat, and exportable Reports with an append-only audit ledger.
 If a Python venv exists at ~/pse-venv it is used automatically; otherwise system python3
 and the recommended python3 packages are used.
EOF

# --- postinst: refresh desktop + icon caches (best-effort) ---
cat > "$DEBIAN/postinst" <<'EOF'
#!/bin/sh
set -e
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database -q /usr/share/applications || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -q -t -f /usr/share/icons/hicolor || true
fi
exit 0
EOF
chmod 0755 "$DEBIAN/postinst"

# --- assemble the .deb (ar members MUST be in this order) ---
cd "$BUILD"
echo "2.0" > debian-binary
tar --owner=0 --group=0 -czf control.tar.gz -C "$DEBIAN" .
tar --owner=0 --group=0 -czf data.tar.gz -C "$ROOT" .
OUT="$APP/${PKG}_${VER}_${ARCH}.deb"
rm -f "$OUT"
ar rc "$OUT" debian-binary control.tar.gz data.tar.gz

echo "Napravljeno: $OUT"
ls -la "$OUT"
