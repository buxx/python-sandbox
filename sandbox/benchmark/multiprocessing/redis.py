# coding: utf-8
import json

import redis

from sandbox.benchmark.multiprocessing.lib.executor import Executor
from sandbox.benchmark.multiprocessing.lib.shared import SharedDataInterface


class RedisSharedData(SharedDataInterface):
    def __init__(self):
        self.r = redis.StrictRedis(host='localhost', port=6379, db=0)
        self.to_commit = {}

    def get(self, key):
        return json.loads(self.r.get(key).decode())

    def create(self, key, value, ctype):
        self.to_commit[key] = value

    def set(self, key, position, value):
        self.to_commit[key][position] = value

    def commit(self, key=None):
        if key:
            self.r.set(key, self.to_commit[key])
        else:
            for key, value in self.to_commit.items():
                self.r.set(key, value)


class RedisExecutor(Executor):
    def _get_shared_data(self) -> SharedDataInterface:
        return RedisSharedData()
