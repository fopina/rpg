#!/bin/bash

set -e

echo $GITHUB_AUTH_SECRET > ~/.git-credentials && chmod 0600 ~/.git-credentials
git config --global credential.helper store
git config --global user.email "fopina-travisci@users.noreply.github.com"
git config --global user.name "Publishing bot"
git config --global push.default simple

mv public ../
git fetch origin gh-pages
git checkout gh-pages
rm -fr *
mv ../public/* .
rmdir ../public/
git add -A
git commit -m "rebuilding site on `date`, commit ${TRAVIS_COMMIT} and job ${TRAVIS_JOB_NUMBER}" || true
git push
