# coding: utf-8
import multiprocessing
import typing

from sandbox.benchmark.multiprocessing.lib.executor import Executor
from sandbox.benchmark.multiprocessing.lib.shared import SharedDataInterface


class ManagerSharedData(SharedDataInterface):
    def __init__(self, manager: multiprocessing.Manager):
        self.manager = manager
        self.data = {}

    def get(self, key):
        return self.data[key]

    def create(self, key, value, ctype):
        # TODO not working for something else than list ...
        self.data[key] = self.manager.list(value)

    def set(self, key, position, value):
        # TODO not working for something else than list ...
        self.data[key][position] = value

    def commit(self, key=None):
        pass


class ManagerExecutor(Executor):
    def __init__(
            self,
            number: int,
            job: typing.Callable[[int, int], int],
    ) -> None:
        super().__init__(number, job)
        self.manager = multiprocessing.Manager()

    def _get_shared_data(self) -> SharedDataInterface:
        return ManagerSharedData(self.manager)

