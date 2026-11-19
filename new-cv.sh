#!/bin/sh
# Start a new CV repository from this template:
#
#   sh waterloo-health-cv-template/new-cv.sh my-cv
#
# Copies starter/ to my-cv/, installs this template's newest release in
# my-cv/template/ (scripts/update_template.sh), and makes the first commit.
set -eu
here=$(cd "$(dirname "$0")" && pwd)
dest=${1:?usage: sh new-cv.sh <new directory>}
[ ! -e "$dest" ] || { echo "$dest already exists." >&2; exit 1; }
cp -R "$here/starter" "$dest"
cd "$dest"
git init -q -b main
release=$(git ls-remote --tags --refs "$here" 'v*' | sed 's|.*refs/tags/||' | sort -V | tail -1)
TEMPLATE_SRC="$here" sh scripts/update_template.sh "${release:-main}"
git add -A
git commit -q -m "Start my CV from waterloo-health-cv-template ${release:-main}"
cat <<MSG
Created $dest with template ${release:-main}. Next:
  1. Put your name, GitHub login and publication ids in $dest/cv.toml.
  2. Replace the fictional CV (main.tex and the .bib files) with your own.
  3. python3 scripts/check_cv.py, then latexmk main.tex && latexmk apr.tex.
  4. Push to a new GitHub repository; AUTOMATION.md lists the one-time setup.
MSG
