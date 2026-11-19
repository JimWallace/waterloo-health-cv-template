#!/bin/sh
# Install or update template/ from a release of the template repository.
#
#   sh scripts/update_template.sh latest     # newest release (git tag v*)
#   sh scripts/update_template.sh v1.2.0     # a given release (or a branch, for testing)
#
# The repository and the installed release are in cv.toml [template]. template/
# is a plain copy (Overleaf can't use git submodules), replaced as a whole: don't
# edit files in it; change the template repository and release instead. Your own
# settings belong in apr-formatting.tex.
# TEMPLATE_SRC=<path or URL> overrides the repository (for testing).
set -eu
cd "$(dirname "$0")/.."
tag=${1:?usage: sh scripts/update_template.sh <tag>|latest}
src=${TEMPLATE_SRC:-https://github.com/$(python3 scripts/cvlib.py template.repo)}
if [ "$tag" = latest ]; then
  tag=$(git ls-remote --tags --refs "$src" 'v*' | sed 's|.*refs/tags/||' | sort -V | tail -1)
  [ -n "$tag" ] || { echo "No releases (v* tags) in $src." >&2; exit 1; }
fi
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
git clone -q --depth 1 --branch "$tag" "$src" "$tmp/src" 2>/dev/null \
  || { echo "Could not fetch $tag from $src." >&2; exit 1; }
rm -rf template && mkdir template
(cd "$tmp/src" && git archive HEAD) | tar -x -C template
# The starter kit, the template repository's own CI and its README images are not part of the template.
rm -rf template/starter template/.github template/docs template/new-cv.sh
sed -i.bak "s|^version = \"[^\"]*\"|version = \"$tag\"|" cv.toml && rm -f cv.toml.bak
echo "template/ is now $tag from $src."
