#!/bin/bash

cd "$(dirname "$0")"

# $1 -> config

if [ -z "$1" ]; then
    echo 'Provide the path to a yaml config!'
    echo "Example: $0 /path/to/config.yaml"
    echo "Using /files/config.yaml as default"
    CFG_FILE=$(pwd)/files/config.yml
elif [[ "$1" == *"--"* ]]; then
    echo 'Provide the path to a yaml config!'
    echo "Example: $0 /path/to/config.yaml"
    echo "Using /files/config.yaml as default"
    CFG_FILE=$(pwd)/files/config.yml
else
    CFG_FILE=$(readlink -f "$1")
fi

IMGNAME='chrono-mate'

docker build -t $IMGNAME . > /dev/null 2>&1

if [[ "$1" == *"--"* ]]; then
    docker run -it --rm --network=host \
    -v "$CFG_FILE":"/usr/src/files/config.yml" \
    -v $(pwd)/files/workbooks:/usr/src/files/workbooks \
    $IMGNAME /usr/src/files/config.yml "${@:1}"
else
    docker run -it --rm --network=host \
    -v "$CFG_FILE":"/usr/src/files/config.yml" \
    -v $(pwd)/files/workbooks:/usr/src/files/workbooks \
    $IMGNAME /usr/src/files/config.yml "${@:2}"
fi