from datetime import datetime
import time
from .. import cache


def test_cache_get():
    cache._cache.clear()
    assert cache.get('x') is None
    assert cache.get('x', 1) == 1
    assert cache.get_item('x') is None
    assert cache.get_item('x', 1) == 1
    cache.set('x', 42)
    assert cache.get('x') == 42
    item = cache.get_item('x')
    assert item.value == 42


def test_cache_created():
    cache._cache.clear()
    cache.set('x', 42)
    item = cache.get_item('x')
    now = datetime.utcnow()
    assert now > item.created
    assert (now - item.created).total_seconds() < 3
    old_created = item.created
    cache.set('x', 42)
    item = cache.get_item('x')
    assert item.created > old_created


def test_cache_max_age():
    cache._cache.clear()
    cache.set('x', 42)
    assert cache.get('x') == 42
    time.sleep(1.1)
    assert cache.get('x', max_age=2) == 42
    assert cache.get('x', max_age=1) is None


def test_cache_delete():
    cache._cache.clear()
    cache.set('x', 42)
    assert cache.get('x') == 42
    cache.delete('x')
    assert cache.get('x') is None