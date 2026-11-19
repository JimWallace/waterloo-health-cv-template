#!/bin/sh
# Check that PDFs are valid PDF/UA-2 (accessible) and PDF/A-4f (archival), with
# veraPDF (the PDF Association's reference validator). The template makes them
# so (template/uwhealthcv-pdfa.tex). veraPDF checks what a machine can: tags,
# alt text, fonts, metadata; not whether the reading order makes sense.
#
#     scripts/check_pdfa.sh main.pdf apr.pdf
#
# Installs the pinned veraPDF release (needs Java 11 or newer) under the
# temporary directory on first use. Exits 1 if a file is not compliant and
# lists the failed rules (clause-test of ISO 14289-2 or ISO 19005-4) for each file.
set -eu

VERSION=1.30.4
SHA256=04415ef3f149526a3048b9889723e81320ddf013bd891bcc7f0f297f3eadcc23
URL="https://software.verapdf.org/releases/1.30/verapdf-greenfield-$VERSION-installer.zip"
HOME_DIR="${TMPDIR:-/tmp}/verapdf-$VERSION"

if [ ! -x "$HOME_DIR/verapdf" ]; then
  work=$(mktemp -d)
  curl -sSfL -o "$work/verapdf.zip" "$URL"
  echo "$SHA256  $work/verapdf.zip" | sha256sum -c - >/dev/null
  unzip -q "$work/verapdf.zip" -d "$work"
  cat > "$work/auto-install.xml" <<EOF
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<AutomatedInstallation langpack="eng">
<com.izforge.izpack.panels.htmlhello.HTMLHelloPanel id="welcome"/>
<com.izforge.izpack.panels.target.TargetPanel id="install_dir">
<installpath>$HOME_DIR</installpath>
</com.izforge.izpack.panels.target.TargetPanel>
<com.izforge.izpack.panels.packs.PacksPanel id="sdk_pack_select">
<pack index="0" name="veraPDF GUI" selected="true"/>
<pack index="1" name="veraPDF Batch files" selected="true"/>
<pack index="2" name="veraPDF Validation model" selected="false"/>
<pack index="3" name="veraPDF Documentation" selected="false"/>
<pack index="4" name="veraPDF Sample Plugins" selected="false"/>
</com.izforge.izpack.panels.packs.PacksPanel>
<com.izforge.izpack.panels.install.InstallPanel id="install"/>
<com.izforge.izpack.panels.finish.FinishPanel id="finish"/>
</AutomatedInstallation>
EOF
  java -jar "$work"/verapdf-greenfield-*/verapdf-izpack-installer-*.jar "$work/auto-install.xml" >/dev/null
  rm -rf "$work"
fi

status=0
for flavour in ua2 4f; do
  "$HOME_DIR/verapdf" --flavour "$flavour" --format text --verbose "$@" || status=1
done
exit $status
