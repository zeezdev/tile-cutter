#!/bin/bash

set -x

SCRIPT=$(readlink -f "$0")
# SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"

SCRIPTPATH=`dirname $SCRIPT`
DIR=$(dirname "$SCRIPTPATH")

echo ${DIR}

virtualenv -p /usr/bin/python3 ${DIR}/.venv
source ${DIR}/.venv/bin/activate
pip install -U -r ${DIR}/requirements.txt

mkdir -p ${DIR}/media
mkdir -p ${DIR}/logs 

cd ${DIR}
bower update
