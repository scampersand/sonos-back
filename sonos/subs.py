import atexit
import logging
from queue import Empty
import threading
from .stoppable_thread import StoppableThread
from . import cache
from .sonos import sonos


logger = logging.getLogger(__name__)


def refresh_track(event=None):
    logger.info("refreshing track (%s)", event)
    try:
        value = sonos.get_current_track_info()
    except Exception:
        logger.exception("get_current_track_info failed")
    else:
        cache.set('CurrentTrack', value)


def refresh_transport(event=None):
    logger.info("refreshing transport (%s)", event)
    try:
        value = sonos.get_current_transport_info()
    except Exception:
        logger.exception("get_current_transport_info failed")
    else:
        cache.set('TransportInfo', value)


class EventSubscriptionThread(StoppableThread):
    def __init__(self, service, refreshers):
        super(EventSubscriptionThread, self).__init__()
        self.service = service
        self.refreshers = refreshers

    def refresh(self, event):
        for r in self.refreshers:
            r(event)

    def run(self):
        sub = self.service.subscribe()
        while True:
            try:
                event = sub.events.get(timeout=0.5)
            except Empty:
                event = None
            if self.stopped():
                sub.unsubscribe()
                return
            if event:
                self.refresh(event)


def start_threads():
    logger.info("starting subscription threads")
    refreshers = [refresh_transport, refresh_track]
    threads = [
        EventSubscriptionThread(sonos.avTransport, refreshers),
        EventSubscriptionThread(sonos.zoneGroupTopology, refreshers),
    ]
    for t in threads:
        t.start()
    logger.info("started subscription threads")

    # Now that we're subscribed, do the initial fetch(es) to the
    # process-wide cache.
    for r in refreshers:
        r()

    return threads


def stop_threads(threads):
    logger.info("stopping subscription threads")
    for t in threads:
        t.stop()
    for t in threads:
        t.join()
    logger.info("stopped subscription threads")


class SubscriptionMiddleware(object):
    def __init__(self, application):
        self.application = application
        self.lock = threading.Lock()
        self.subscribed = False
        self.threads = []

    def subscribe(self):
        if self.subscribed:
            return
        with self.lock:
            if self.subscribed:
                return
            self.subscribed = True
        atexit.register(self.unsubscribe)
        self.threads = start_threads()

    def unsubscribe(self):
        stop_threads(self.threads)

    def __call__(self, environ, start_response):
        self.subscribe()
        try:
            return self.application(environ, start_response)
        except:
            self.unsubscribe()
            raise
