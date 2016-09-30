"""
Stand-in for flask.run to start event listener and subscription threads
ahead of the app, and stop them afterward. This ensures that we unsubscribe
and stop the event listener even when werkzeug automatically reloads the
application, or when we hit ctrl-c

Okay, that's bogus. This doesn't work with the Werkzeug reloader either.
"""

import logging
import os
import sys
import flask.cli
import soco.config
from soco.events import event_listener
from sonos.sonos import sonos  # yep
from sonos import subs


def run():
    # Override default soco config from environment.
    if os.environ.get('SOCO_CACHE_ENABLED'):
        soco.config.CACHE_ENABLED = (os.environ['SOCO_CACHE_ENABLED'].lower() in
                                     ['0', 'no', 'off', 'false'])
    if os.environ.get('SOCO_EVENT_LISTENER_PORT'):
        soco.config.EVENT_LISTENER_PORT = int(os.environ['SOCO_EVENT_LISTENER_PORT'])

    # Start the event listener thread immediately, since it's not threadsafe
    # and will try to start twice through the subscription threads.
    event_listener.start(sonos)

    try:
        # Start the subscription threads.
        # This immediately populates the cache of SONOS responses.
        threads = subs.start_threads()

        # Run flask. This depends on FLASK_APP being set in the environemnt.
        try:
            sys.argv.insert(1, 'run')  # like "flask run" for flask.cli.main()
            return flask.cli.main()
        finally:
            subs.stop_threads(threads)
    finally:
        event_listener.stop()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    sys.exit(run())