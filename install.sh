#!/bin/bash
#

# Absolute path to this script, e.g. /home/user/bin/foo.sh
SCRIPT=$(readlink -f "$0")
# Absolute path this script is in, thus /home/user/bin
SCRIPTPATH=$(dirname "$SCRIPT")
echo $SCRIPTPATH
PROJECTROOTPATH="$(dirname "$SCRIPTPATH")"
echo $PROJECTROOTPATH

#virtualenv -p python3 venv
#brew install ffmpeg
#brew install sox

#source ${SCRIPTPATH}/venv/bin/activate
##${SCRIPTPATH}/venv/bin/pip3 list
#${SCRIPTPATH}/venv/bin/python -m pip install --upgrade pip
#${SCRIPTPATH}/venv/bin/pip3 install -r requirements.txt