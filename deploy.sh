#!/bin/sh

# If a command fails then the deploy stops
# set -e

printf "\033[0;32mDeploying updates to GitHub...\033[0m\n"

hugo

cd public
git add -A
msg="rebuilding site $(date)"
if [ -n "$*" ]; then
    msg="$*"
fi
git commit -m "$msg"
git push origin master

cd ..
git add -A
git commit -m "$msg"
git push