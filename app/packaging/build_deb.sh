#!/usr/bin/env bash
# Build pse-jacobian_<version>_amd64.deb (self-contained PyInstaller bundle).
# Run from a checkout; the Python project is in app/. Release build on Ubuntu 22.04.
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"       # app/packaging
APP="$(dirname "$HERE")"                    # app
REPO="$(dirname "$APP")"                    # repo root
PY="${PYTHON:-$APP/.venv/bin/python}"
VERSION="${1:-0.1.0}"; ARCH="${ARCH:-amd64}"; PKG="pse-jacobian"
STAGE="$HERE/stage"; OUT="$REPO/dist"

echo "== PyInstaller bundle"
rm -rf "$APP/build/pyi" "$STAGE"
"$PY" -m PyInstaller --noconfirm --clean --onedir --name "$PKG" \
  --distpath "$APP/build/pyi/dist" --workpath "$APP/build/pyi/work" --specpath "$APP/build/pyi" \
  --collect-submodules pse_jacobian --collect-data pse_jacobian \
  --collect-all matplotlib \
  "$HERE/entry.py"

APPDIR="$STAGE/opt/$PKG"; mkdir -p "$APPDIR"
cp -a "$APP/build/pyi/dist/$PKG/." "$APPDIR/"
cp "$REPO/LICENSE" "$APPDIR/LICENSE"; cp "$REPO/NOTICE" "$APPDIR/NOTICE"

mkdir -p "$STAGE/usr/bin" "$STAGE/usr/share/applications" \
         "$STAGE/usr/share/icons/hicolor/256x256/apps" \
         "$STAGE/usr/share/doc/$PKG" "$STAGE/DEBIAN"
ln -s "/opt/$PKG/$PKG" "$STAGE/usr/bin/$PKG"
cp "$HERE/$PKG.png" "$STAGE/usr/share/icons/hicolor/256x256/apps/$PKG.png"
cp "$REPO/LICENSE" "$STAGE/usr/share/doc/$PKG/LICENSE"; cp "$REPO/NOTICE" "$STAGE/usr/share/doc/$PKG/NOTICE"
cat > "$STAGE/usr/share/applications/$PKG.desktop" <<DESK
[Desktop Entry]
Type=Application
Name=PSE-Jacobian
Comment=Reproduce and audit the Jacobian Conjecture counterexample
Exec=$PKG
Icon=$PKG
Terminal=false
Categories=Education;Science;Math;
DESK

SIZE="$(du -sk "$STAGE/opt" "$STAGE/usr" | awk '{s+=$1} END{print s}')"
cat > "$STAGE/DEBIAN/control" <<CTL
Package: $PKG
Version: $VERSION
Section: science
Priority: optional
Architecture: $ARCH
Installed-Size: $SIZE
Maintainer: Andrej Ristic <andrej.s.ristic@gmail.com>
Depends: libc6 (>= 2.34), libgl1, libegl1, libfontconfig1, libxkbcommon0, libdbus-1-3
Homepage: https://github.com/andrejristic/pse-jacobian
Description: PSE-Jacobian - reproduce and audit the Jacobian Conjecture counterexample
 A Partial Self-Extension swarm that independently reproduces and audits a
 counterexample to the Jacobian Conjecture over the complex numbers, with a
 symbolic math engine, Guardians, and a plain-language report.
CTL

echo "== dpkg-deb"; mkdir -p "$OUT"
DEB="$OUT/${PKG}_${VERSION}_${ARCH}.deb"
dpkg-deb --root-owner-group -Zxz --build "$STAGE" "$DEB"
echo "built $DEB"
