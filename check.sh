#!/bin/sh

BITWARDENRS_HOME="$(dirname $0)"
cd "${BITWARDENRS_HOME}"
. ./env.sh

if ! curl -fsS "http://${ROCKET_ADDRESS}:${ROCKET_PORT}/alive" >/dev/null; then
    echo "bitwarden_rs server not alive, restarting it..."
    ./start.sh
fi
