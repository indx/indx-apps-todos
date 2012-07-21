#!/bin/bash

# This is a default file, and is overridden on first run.

export PATH="${SECURESTORE_HOME}/4store:$PATH"
export ME=`whoami`
export HOME=`ls -d ~`


export KBNAME="webbox_$ME"
export RWW_JAR="${SECURESTORE_HOME}/rww/read-write-web.jar"
export RWW_PORT="8213"
export LOG_RWW="/tmp/rww.log"
export LOG_SECURESTORE="/tmp/webbox_server.log"
export LOG_4S="/tmp/4store.log"
export PORT="8212"
export RWW_LD="$HOME/.webbox/data/rww"
mkdir -p "$RWW_LD"
