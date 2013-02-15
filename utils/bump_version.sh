#!/bin/bash
exit_usage() {
    echo "Usage: $0 openerp_version release_number"
    echo ""
    echo "openerp_version: Openerp version this release is built for"
    echo "release_number: Release number in format yyyymmddxx xx is the release number of the day first release 00, second release 01. ie. 1978091500"
    echo ""
    echo "example:"
    echo "$0 6.1 2012021000"
    exit 1
}

case $# in
    2 ) oe_version=$1
        release_number=$2;;
    * ) exit_usage;;
esac

function parse_git_dirty {
  [[ $(git status 2> /dev/null | tail -n1) != "nothing to commit (working directory clean)" ]] && echo "Changes pending to commit"
}

if parse_git_dirty; then
    echo "Please commit or stage them before make a new release"
    exit 1
fi

echo "[INFO] Pulling on master and dev"
git checkout master
git pull
git checkout dev
git pull

version="openerp$oe_version-rev$release_number"

echo "[INFO] New release $version"

if $(grep -q "$version" Changes); then
    echo "Release already exist"
    exit 1
else
    branch="release_$version"
    read -p ">>> Press any key to create release branch or CTRL+C to stop " ans
    echo "[INFO] Creating a new release branch for $version"
    git checkout -b $branch

    for I in $(ls src/*/__openerp__.py); do
        echo "[INFO] Bumping $version into $I"
        sed -i "s/openerp[0-9].[0-9]-rev[0-9]\{10\}/$version/g" $I
    done

    echo "[INFO] Bumping $version into Changes"
    sed -i "1s/.*/$version\n&/" Changes

    git commit -a -m "Release $version"

    read -p ">>> Press any key to merge on master or CTRL+C to stop " ans

    echo "[INFO] Merging in master"
    git checkout master
    git merge --no-ff $branch

    read -p ">>> Press any key to tag and push or CTRL+C to stop " ans
    echo "[INFO] Creating new tag and pushing"
    git tag -a $version -m "New release $version"
    git push
    git push --tags

    read -p ">>> Press any key to merge in dev or CTRL+C to stop " ans

    echo "[INFO] Merging in dev"
    git checkout dev
    git merge --no-ff $branch

    read -p ">>> Press any key to push dev or CTRL+C to stop " ans
    echo "[INFO] Pushing dev"
    git push
fi
