#!/bin/bash

set -x

SCRIPT=$(readlink -f "$0")
# SCRIPT_DIR="$( cd "$( dirname "$0" )" && pwd )"

SCRIPTPATH=`dirname $SCRIPT`
DIR=$(dirname "$SCRIPTPATH")

ARCHNAME="cutter.tar.gz"
HOSTNAME="tc"

echo ${DIR}

rm ${DIR}/${ARCHNAME}

tar -zcvf ${DIR}/${ARCHNAME} \
--exclude="./.idea" \
--exclude="./.venv" \
--exclude="./.git" \
--exclude="./media" \
--exclude="./${ARCHNAME}" \
--exclude="./ideas.txt" \
--exclude="./passwd.txt" \
--exclude="./.gitignore" \
--exclude="./cutter/settings.dev.py" \
--exclude="*.pyc" \
--exclude="./*/__pycache__" \
-C ${DIR} .

scp ${DIR}/${ARCHNAME} ${HOSTNAME}:/root/tmp/