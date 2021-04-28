#!/bin/sh

VAULTWARDEN_HOME="$(dirname $0)"
cd "${VAULTWARDEN_HOME}"
. ./env.sh

if ! curl -fsS "http://${ROCKET_ADDRESS}:${ROCKET_PORT}/alive" >/dev/null; then
    echo "vaultwarden server not alive, restarting it..."
    ./start.sh
fi
