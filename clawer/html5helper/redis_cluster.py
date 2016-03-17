# -*- coding: utf-8 -*-
import cPickle as pickle
import random
import time
import zlib

from django.conf import settings

from redis import StrictRedis, ConnectionError, TimeoutError

from .pylocache import LocalCache


def dumps_zip(value):
    pickled_value = pickle.dumps(value, 2)
    zip_pickled_value = zlib.compress(pickled_value)
    return zip_pickled_value


def loads_zip(zip_pickled_value):
    pickled_value = zlib.decompress(zip_pickled_value)
    value = pickle.loads(pickled_value)
    return value


if settings.REDIS_DATA_COMPRESSED:
    r_loads = loads_zip
    r_dumps = dumps_zip
else:
    r_loads = pickle.loads
    r_dumps = lambda v: pickle.dumps(v, 2)


class PickledRedis(StrictRedis):
    """
    a pickled redis client
    """

    def get(self, name):
        pickled_value = super(PickledRedis, self).get(name)
        if pickled_value is None:
            return None
        return r_loads(pickled_value)

    def mget(self, keys, *args):
        if not keys:
            return []
        pickled_value_list = super(PickledRedis, self).mget(keys, *args)
        res = []
        for pickled_value in pickled_value_list:
            if pickled_value is None:
                res.append(None)
            else:
                res.append(r_loads(pickled_value))
        return res

    def set(self, name, value, ex=None, px=None, nx=False, xx=False):
        return super(PickledRedis, self).set(name, r_dumps(value), ex, px, nx, xx)

    def setnx(self, name, value):
        return super(PickledRedis, self).setnx(name, r_dumps(value))

    def getset(self, name, value):
        pickled_value = super(PickledRedis, self).getset(name, r_dumps(value))
        if pickled_value is None:
            return None
        return r_loads(pickled_value)

    def incr(self, name, amount=1):
        """
        this method is a original method! not use pickle and not use zip
        """
        return super(PickledRedis, self).incr(name, amount)

    def get_incr(self, name):
        """
        you should use get_incr method, if you set key through incr method
        this method is a original method! not use pickle and not use zip
        """
        return super(PickledRedis, self).get(name)



class RedisCluster(object):
    """
    redis cluster class
    """

    def __init__(self, node_name="default"):
        """
        read settings
        """
        conf = settings.REDIS_CLUSTER[node_name]
        timeout = conf.get("TIMEOUT")  # milliseconds
        locache_timeout = conf.get("LOCAL_CACHE_TIMEOUT")  # seconds
        if locache_timeout:
            self.cache = LocalCache(expires=locache_timeout)
        else:
            self.cache = None
        self.timeout = timeout and timeout/1000 or None
        self.db = conf.get("DB", 0)
        self.try_times = conf.get("TRY_TIMES", 1)
        self.master = None
        self.slaves = []
        servers = conf.get("SERVERS", [])
        self._set_master_slavers(servers)

    def _set_master_slavers(self, servers):
        """
        set master and slavers
        """
        if len(servers):
            try:
                host, port = servers[0].split(":")
                self.master = PickledRedis(host=host, port=int(port), db=self.db, socket_timeout=self.timeout)
            except (ValueError, TypeError):
                pass
        for server in servers[1:]:
            try:
                host, port = server.split(":")
                rclient = PickledRedis(host=host, port=int(port), socket_timeout=self.timeout)
            except (ValueError, TypeError):
                pass
            else:
                self.slaves.append(rclient)

    def get(self, key):
        """
        from all workers
        """
        if not self.slaves:
            return None
        # try to get data from local cache
        if self.cache:
            res = self.cache.get(key)
            if res:
                return res
        # get data from redis
        idx_dict = dict.fromkeys(range(len(self.slaves)))
        res = None
        for i in range(self.try_times):
            if len(idx_dict) > 0:
                idx = random.choice(idx_dict.keys())
                client = self.slaves[idx]
                try:
                    res = client.get(key)
                except (ConnectionError, TimeoutError):
                    idx_dict.pop(idx, None)
                else:
                    if res and self.cache:
                        self.cache.set(key, res)
                    break
        return res

    def get_incr(self, key):
        """
        from all workers
        """
        if not self.slaves:
            return None
        # get data from redis
        idx_dict = dict.fromkeys(range(len(self.slaves)))
        res = None
        for i in range(self.try_times):
            if len(idx_dict) > 0:
                idx = random.choice(idx_dict.keys())
                client = self.slaves[idx]
                try:
                    res = client.get_incr(key)
                except (ConnectionError, TimeoutError):
                    idx_dict.pop(idx, None)
                else:
                    break
        if res is None:
            res = 0
        else:
            res = int(res)
        return res

    def mget(self, keys, *args):
        """
        from all workers
        """
        res = [None]*len(keys)
        if not self.slaves:
            return res
        # get data from redis
        idx_dict = dict.fromkeys(range(len(self.slaves)))
        for i in range(self.try_times):
            if len(idx_dict) > 0:
                idx = random.choice(idx_dict.keys())
                client = self.slaves[idx]
                try:
                    res = client.mget(keys, *args)
                except (ConnectionError, TimeoutError):
                    idx_dict.pop(idx, None)
                else:
                    break
        return res

    def keys(self, pattern='*'):
        """
        from all workers
        """
        if not self.slaves:
            return []
        # get keys
        idx_dict = dict.fromkeys(range(len(self.slaves)))
        res = []
        for i in range(self.try_times):
            if len(idx_dict) > 0:
                idx = random.choice(idx_dict.keys())
                client = self.slaves[idx]
                try:
                    res = client.keys(pattern)
                except (ConnectionError, TimeoutError):
                    idx_dict.pop(idx, None)
                else:
                    break
        return res

    def set(self, key, value, timeout=None):
        """
        only write in master
        timeout is milliseconds
        """
        if self.master:
            self.master.set(key, value, px=timeout)

    def setnx(self, name, value):
        if self.master:
            return self.master.setnx(name, value)

    def getset(self, name, value):
        if self.master:
            return self.master.getset(name, value)

    def incr(self, name):
        if self.master:
            return self.master.incr(name)

    def delete(self, key):
        """
        only write in master
        """
        if self.master:
            self.master.delete(key)

#default_redis_cluster = RedisCluster("default")


class RedisLock(object):
    def __init__(self, r, key, expires=3, timeout=3):
        """
        Distributed locking using Redis SETNX and GETSET.

        Usage::

            with RedisLock('my_lock'):
                print "Critical section"

        :param  expires     We consider any existing lock older than
                            ``expires`` seconds to be invalid in order to
                            detect crashed clients. This value must be higher
                            than it takes the critical section to execute.
        :param  timeout     If another client has already obtained the lock,
                            sleep for a maximum of ``timeout`` seconds before
                            giving up. A value of 0 means we never wait.
        """
        self.redis = r
        self.key = key
        self.timeout = timeout
        self.expires = expires

    def __enter__(self):
        timeout = self.timeout
        while timeout >= 0:
            expires = time.time() + self.expires + 1

            if self.redis.setnx(self.key, expires):
                # We gained the lock; enter critical section
                return

            current_value = self.redis.get(self.key)

            # We found an expired lock and nobody raced us to replacing it
            if current_value and float(current_value) < time.time() and \
                self.redis.getset(self.key, expires) == current_value:
                    return

            timeout -= 1
            time.sleep(1)

        raise LockTimeout("Timeout whilst waiting for lock")

    def __exit__(self, exc_type, exc_value, traceback):
        self.redis.delete(self.key)


class LockTimeout(BaseException):
    pass
