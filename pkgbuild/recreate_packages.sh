#!/bin/bash
# git project root
PROJECTDIR="$(git rev-parse --show-toplevel)"
# test repos
ARMDIR="$PROJECTDIR/repo/testing/extra/aarch64"
X86DIR="$PROJECTDIR/repo/testing/extra/x86_64"
# remove previous packages and signatures
find "$PROJECTDIR/repo" -type f -name "a-dummy*" -exec rm "{}" \; > /dev/null
# build new packages
PKGDEST="$PROJECTDIR/repo" makepkg -cC
# sign the new packages
find "$PROJECTDIR/repo" -type f -name "*.pkg.tar.*" -exec signfile "{}" \;
# loop the files
for file in "$PROJECTDIR"/repo/*.pkg.tar.*
do
  # copy files to rest repos
  cp "$file" "$X86DIR"
  cp "$file" "$ARMDIR"
  # clean up workspace
  rm "$file"
done



