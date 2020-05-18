#!/bin/bash
#

# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")
echo $SCRIPTPATH
PROJECTROOTPATH="$(dirname "$SCRIPTPATH")"
echo $PROJECTROOTPATH

export PYTHONPATH=$PYTHONPATH:"${SCRIPTPATH}"
export PYTHONPATH=$PYTHONPATH:"${SCRIPTPATH}/asr-google"
export PYTHONPATH=$PYTHONPATH:"${SCRIPTPATH}/asr-ibm"
export PYTHONPATH=$PYTHONPATH:"${SCRIPTPATH}/asr-msoft"
export PYTHONPATH=$PYTHONPATH:"${SCRIPTPATH}/eval"

source ${SCRIPTPATH}/venv/bin/activate
${SCRIPTPATH}/venv/bin/python3  ${SCRIPTPATH}/eval/__init__.py