#!/bin/bash

set -x

function track () {
    ./tracker.py $@
}

if [[ $1 ]]
then
    track --url "$1" -u -d
else
    track -u -d
fi

git config --local user.name "Commit Bot"
git config --local user.email "<>"
    
# if there are changes
if [[ $(git status --short | wc -l) > 0 ]]
then
    VERSION="v$(track -pv)"
    git add -A
    git commit -m "$VERSION"
    git tag "$VERSION"
fi

date >> latest-run.txt
git add -A
git commit -m "keep-alive: repo"
