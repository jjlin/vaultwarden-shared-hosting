#!/bin/sh

BITWARDENRS_HOME="$(dirname $0)"
cd "${BITWARDENRS_HOME}"
. ./env.sh

if pgrep bitwarden_rs >/dev/null 2>&1; then
    echo "Killing existing bitwarden_rs process..."
    pkill bitwarden_rs
fi
nohup ./bitwarden_rs >>bitwarden_rs.log 2>&1 &
echo "Started bitwarden_rs."
