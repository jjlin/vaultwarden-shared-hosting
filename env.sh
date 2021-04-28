# This file is also read by a Python script, and doesn't support
# full shell syntax. Don't use quotes in values.

# The address of the vaultwarden backend. You shouldn't need to change this.
ROCKET_ADDRESS=localhost

# The port that the vaultwarden backend is configured to listen on.
# You only need to change this in the unlikely event that some other program
# on the shared host is already using this port.
ROCKET_PORT=28973

export ROCKET_ADDRESS ROCKET_PORT
