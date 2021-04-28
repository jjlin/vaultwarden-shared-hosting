#!/bin/sh

VAULTWARDEN_HOME="$(dirname $0)"
cd "${VAULTWARDEN_HOME}"
. ./env.sh

if pgrep vaultwarden >/dev/null 2>&1; then
    echo "Killing existing vaultwarden process..."
    pkill vaultwarden
fi
nohup ./vaultwarden >>vaultwarden.log 2>&1 &
echo "Started vaultwarden."
