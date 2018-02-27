#!/usr/bin/env bash
mkdir ~/bin
PATH=~/bin:$PATH
curl https://s3.amazonaws.com/ygomi-hub-rdb/3rd/repo > ~/bin/repo
chmod a+x ~/bin/repo

echo "START PULL THE CODE"
mkdir sourcescode
cd sourcescode
repo init -u ssh://git@stash.ygomi.com:7999/rc/manifest.git -b master
repo sync

cd core
git clone ssh://git@stash.ygomi.com:7999/rc/algorithm_sam.git