#!/usr/bin/env bash
set -Eeuo pipefail

VERSION="${VERSION:-0.4.0+20260716}"
ARCH="${ARCH:-arm64}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
SOURCE_DIR="${SOURCE_DIR:-$REPO_ROOT/autocar/pop}"
OUTPUT_DIR="${OUTPUT_DIR:-$REPO_ROOT/migration_data/packages}"
PACKAGE="gong-rc-pop"
BUILD_ROOT="$(mktemp -d)"

cleanup() {
  rm -rf "$BUILD_ROOT"
}
trap cleanup EXIT

if [[ ! -f "$SOURCE_DIR/__init__.py" ]]; then
  echo "pop source not found: $SOURCE_DIR" >&2
  exit 1
fi
command -v dpkg-deb >/dev/null || {
  echo "dpkg-deb is required" >&2
  exit 1
}

PACKAGE_ROOT="$BUILD_ROOT/${PACKAGE}_${VERSION}_${ARCH}"
INSTALL_ROOT="$PACKAGE_ROOT/usr/lib/python3/dist-packages/pop"
mkdir -p "$PACKAGE_ROOT/DEBIAN" "$INSTALL_ROOT" "$OUTPUT_DIR"

cp -a "$SOURCE_DIR/." "$INSTALL_ROOT/"
find "$INSTALL_ROOT" -type d -name __pycache__ -prune -exec rm -rf {} +
find "$INSTALL_ROOT" -type f \( -name '*.pyc' -o -name '*.pyo' \) -delete
find "$INSTALL_ROOT" -type d -exec chmod 0755 {} +
find "$INSTALL_ROOT" -type f -exec chmod 0644 {} +

install -D -m 0755 "$REPO_ROOT/migration_data/scripts/install_pop_ai_dependencies.sh" \
  "$PACKAGE_ROOT/usr/share/gong-rc-pop/install_pop_ai_dependencies.sh"
mkdir -p "$PACKAGE_ROOT/usr/bin"
ln -s ../share/gong-rc-pop/install_pop_ai_dependencies.sh \
  "$PACKAGE_ROOT/usr/bin/gong-rc-pop-install-ai"

cat >"$PACKAGE_ROOT/DEBIAN/control" <<EOF
Package: $PACKAGE
Version: $VERSION
Section: python
Priority: optional
Architecture: $ARCH
Maintainer: gong_rc_2026 migration <noreply@localhost>
Depends: python3 (>= 3.8), python3-smbus, python3-numpy, python3-opencv, python3-pyaudio, python3-traitlets, python3-ipywidgets, python3-jetson-gpio
Recommends: libopenblas-dev, libopenmpi-dev, libjpeg-dev, zlib1g-dev, libpng-dev, libsndfile1-dev, libhdf5-dev, liblapack-dev, libblas-dev, gfortran, python3-h5py
Description: Hanback POP hardware education library for gong_rc_2026
 Source snapshot of the POP hardware and robotics teaching library, including
 the model assets used by the migrated Xavier NX class environment. Run
 gong-rc-pop-install-ai to install the Jetson AI framework dependencies.
EOF

cat >"$PACKAGE_ROOT/DEBIAN/postinst" <<'EOF'
#!/bin/sh
set -e
chmod -R a+rX /usr/lib/python3/dist-packages/pop
if command -v ldconfig >/dev/null 2>&1; then
  ldconfig
fi
exit 0
EOF
chmod 0755 "$PACKAGE_ROOT/DEBIAN/postinst"

OUTPUT="$OUTPUT_DIR/${PACKAGE}_${VERSION}_${ARCH}.deb"
dpkg-deb --root-owner-group --build "$PACKAGE_ROOT" "$OUTPUT"
dpkg-deb --info "$OUTPUT"
sha256sum "$OUTPUT"
echo "POP_DEB=$OUTPUT"
