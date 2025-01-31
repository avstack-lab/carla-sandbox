#!/usr/bin/env bash

set -e

VERSION=${1:-"multi-agent-aerial-utsa"}
DATAFOLDER=${2:-/data/$(whoami)}
MAXFILES=${3:-10}

DATAFOLDER=${DATAFOLDER%/}  # remove trailing slash
DATAFOLDER="${DATAFOLDER}/CARLA"

DOWNLOAD="https://g-b0ef78.1d0d8d.03c0.data.globus.org/datasets/carla"

if [ "$VERSION" = "multi-agent-aerial-utsa" ]; then
    echo "Preparing to download UTSA dataset..."
    SAVESUB="multi-agent-aerial-utsa/raw"
    SUBDIR="multi-agent-aerial-utsa"
    files=(
        run_2025-01-24_15:23:46
        run_2025_01-24_15:25:51
        run_2025-01-24_15:28:00
        run_2025-01-24_15:30:12
        run_2025-01-24_15:32:23
        run_2025-01-24_15:34:32
        run_2025-01-24_15:36:41
        run_2025-01-24_15:38:51
        run_2025-01-24_15:41:01
        run_2025-01-24_15:43:11
    )
else
    echo "Cannot understand input version ${VERSION}!"
fi

SAVEFULL="${DATAFOLDER}/${SAVESUB}"
mkdir -p $SAVEFULL

echo "Downloading up to $MAXFILES files"
COUNT=0

for FILE in ${files[@]}; do
    shortname="${FILE}.tar.gz"
    fullname="${SAVEFULL}/${shortname}"
    F_REP="${FILE//-/:}"
    evidence="${SAVEFULL}/${F_REP}/.full_download"

    # -- check for evidence of full download
    if [ -f "$evidence" ]; then
        echo -e "$shortname exists and already unzipped\n"
    # -- check for existing tar.gz file
    elif [ -f "$DOWNLOAD/$SAVESUB/$shortname" ]; then
        echo -e "$shortname exists...unzipping\n"
        tar -xvf "$fullname" -C "$SAVEFULL" --force-local
        mv "$DATAFOLDER/$SAVESUB/$SUBDIR/$FILE" "$DATAFOLDER/$SAVESUB/$FILE"  # this is a result of a saving error previously
        rm -r "$DATAFOLDER/$SAVESUB/$SUBDIR"
        rm "$DATAFOLDER/$SAVESUB/${FILE}.tar.gz"
    # -- otherwise, download again
    else
        echo "Downloading ${shortname}"
        wget -P "$SAVEFULL" "$DOWNLOAD/$SAVESUB/$shortname"
        tar -xvf "$fullname" -C "$SAVEFULL" --force-local
        mv "$DATAFOLDER/$SAVESUB/$SUBDIR/$F_REP" "$DATAFOLDER/$SAVESUB/$F_REP"  # this is a result of a saving error previously
        rm -r "$DATAFOLDER/$SAVESUB/$SUBDIR"
        rm "$DATAFOLDER/$SAVESUB/${FILE}.tar.gz"
    fi
    
    # -- add evidence of successful download
    touch "$evidence"

    # -- check downloads
    COUNT=$((COUNT+1))
    echo "Downloaded $COUNT / $MAXFILES files!"
    if [[ $COUNT -ge $MAXFILES ]]; then
            echo "Finished downloading $COUNT files"
            break
    fi
done
