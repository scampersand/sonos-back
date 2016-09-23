#!/usr/bin/env python

from queue import Empty
import soco
from soco.events import event_listener
import logging
logging.basicConfig(level=logging.DEBUG)
device = next(d for d in soco.discover() if d.player_name == 'Amy')
sub = device.avTransport.subscribe()

while True:
    try:
        event = sub.events.get(timeout=0.5)
        import ipdb; ipdb.set_trace()
    except Empty:
        pass
    except KeyboardInterrupt:
        break

sub.unsubscribe()
event_listener.stop()

