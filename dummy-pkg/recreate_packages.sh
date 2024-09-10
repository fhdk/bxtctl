#!/bin/bash
# git project root
PROJECTDIR="$(git rev-parse --show-toplevel)"

# test repos
ARMDIR="$PROJECTDIR/repo/testing/extra/aarch64"
X86DIR="$PROJECTDIR/repo/testing/extra/x86_64"
# test and create if not existing
if ! [[ -d "$ARMDIR"  ]]; then
  mkdir -p "$ARMDIR"
fi
if ! [[ -d "$X86DIR"  ]]; then
  mkdir -p "$X86DIR"
fi

# remove previous packages and signatures
find "$PROJECTDIR/dummy-repo" -type f -name "a-dummy*" -exec rm "{}" \; > /dev/null

# generate a version number
pkgver=$(date -d "today" +"%Y%m%d.%H%M")

# inject the version number into the PKGBUILD
sed -i 's|pkgver=.*|pkgver='"${pkgver}"'|g' "$PROJECTDIR/dummy-pkg/PKGBUILD"

# and the upload scratchpad
sed -i 's|pkgver = .*|pkgver = '\""${pkgver}"\"'|g' "$PROJECTDIR/scratchpads/0010_pkg_upload.py"

# build new packages
cd "$PROJECTDIR/pkg-dummy" || exit 1
PKGDEST="$PROJECTDIR/repo" makepkg -cC
cd "$PROJECTDIR" || exit 1

# sign the new packages
find "$PROJECTDIR/repo" -type f -name "*.pkg.tar.*" -exec signfile "{}" \;

# loop the files
for file in "$PROJECTDIR"/dummy-repo/*.pkg.tar.*
do
  # copy files to test repos
  cp "$file" "$X86DIR"
  cp "$file" "$ARMDIR"
  # clean up workspace
  rm "$file"
done
