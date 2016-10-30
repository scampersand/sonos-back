#!/bin/bash

export FLASK_APP=sonos/app.py

# Normally we'd want FLASK_DEBUG=1 which enables the automatic reloader, but
# it doesn't work with the event subscription thread etc. So keep this zero for
# now.
export FLASK_DEBUG=0

# If -h not specified, choose an IP address to listen on.
# This could also be "0" but then doesn't display a nice clickable link.
case " $*" in
    *' --host'|*' -h')
        true
        ;;
    *)
        ip=$(ip a | grep -o '172\.20\.[.0-9]*' | head -n1)
        set -- "$@" --host ${ip:-0}
        ;;
esac

# If -p not specified, choose a port automatically based on the UID.
case " $*" in
    *' --port'|*' -p')
        true
        ;;
    *)
        set -- "$@" --port $((5000 + EUID % 10000))
        ;;
esac

# Choose an event listener port automatically based on the UID,
# otherwise all the backends on the system will default to port 1400.
# This environment variable is picked up by sonos/__main__.py
if [[ -z $SOCO_EVENT_LISTENER_PORT ]]; then
    export SOCO_EVENT_LISTENER_PORT=$((6000 + EUID % 10000))
fi

python ./server.py "$@"
