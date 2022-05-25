#!/bin/bash

function track () {
    ./tracker.py $@
}

if [[ $1 ]]
then
    track --url "$1" -u -d
else
    track -u -d
fi

# if there are changes
if [[ $(git status --short | wc -l) > 0 ]]
then
    git config --local user.name "Commit Bot"
    git config --local user.email "<>"

    VERSION="v$(track -pv)"
    git add -A
    git commit -m "$VERSION"
    git tag "$VERSION"
fi
