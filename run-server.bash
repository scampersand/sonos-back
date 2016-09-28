#!/bin/bash

export FLASK_APP=sonos/app.py
export FLASK_DEBUG=1

# If -h not specified, choose an IP address to listen on.
# This could also be "0" but then doesn't display a nice clickable link.
case " $*" in
    *' --host'|*' -h')
        true
        ;;
    *)
        ip=$(ip a | grep -o '172[.0-9]*' | head -n1)
        set -- "$@" -h ${ip:-0}
        ;;
esac

# If -p not specified, choose a port automatically based on the UID.
case " $*" in
    *' --port'|*' -p')
        true
        ;;
    *)
        set -- "$@" -p $((5000 + EUID % 10000))
        ;;
esac

flask run "$@"
