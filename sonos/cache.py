"""
Simple process-wide cache of responses. These include a timestamp so they can
be either invalidated by events or by expiration.
"""
from collections import namedtuple
from datetime import datetime, timedelta


CacheItem = namedtuple('CacheItem', ['created', 'value'])
_cache = {}
_missing = object()


def older_than(item, max_age):
    delta = datetime.utcnow() - item.created
    return delta > timedelta(seconds=max_age)


def get_item(key, default=None, max_age=0):
    try:
        item = _cache[key]
    except KeyError:
        return default
    if max_age and older_than(item, max_age):
        return default
    return item


def get(key, default=None, max_age=0):
    item = get_item(key, _missing, max_age)
    return default if item is _missing else item.value


def set(key, value):
    _cache[key] = CacheItem(
        created=datetime.utcnow(),
        value=value,
    )


def delete(key):
    try:
        del _cache[key]
    except KeyError:
        pass