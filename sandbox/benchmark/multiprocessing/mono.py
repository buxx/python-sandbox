# coding: utf-8
import typing

import time

from sandbox.benchmark.multiprocessing.lib.executor import Executor
from sandbox.benchmark.multiprocessing.lib.shared import SharedDataInterface
from sandbox.benchmark.multiprocessing.lib.work import work_mono
from sandbox.lg import lg


class MonoSharedData(SharedDataInterface):
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data[key]

    def create(self, key, value, ctype):
        # TODO not working for something else than list ...
        self.data[key] = value

    def set(self, key, position, value):
        # TODO not working for something else than list ...
        self.data[key][position] = value

    def commit(self, key=None):
        pass


class MonoExecutor(Executor):
    def _get_shared_data(self) -> SharedDataInterface:
        return MonoSharedData()

    def compute(self, cycles: int, data_weight: int, print_cps: bool = False):
        shared_data = self._get_shared_data()

        now = time.time()
        lg.info('Prepare init data')
        for job_id in range(self.number):
            lg.debug('Prepare init data for job {} with weight {}'.format(job_id, data_weight))
            job_data = [0] * data_weight  # type: typing.List[int]
            shared_data.create(job_id, job_data, 'i')
            for i in range(data_weight):
                shared_data.set(job_id, i, 1)
        lg.info('Prepare init data finshed: {}'.format(time.time() - now))

        before_start_time = time.time()
        for cycle_id in range(cycles):
            cycle_start_time = time.time()

            for job_id in range(self.number):
                for number in range(self.number):
                    work_mono(job_id, self.job, shared_data)

            lg.info('Cycle {} finished: {}'.format(cycle_id, time.time() - cycle_start_time))

        elapsed = time.time() - before_start_time
        cps = cycles / elapsed
        lg.info('All cycles finished: {} ({}cps)'.format(elapsed, cps))

        return_value = {}
        for job_id in range(self.number):
            job_data = shared_data.get(job_id)
            if 10 <= len(job_data):
                job_data_demo = list(job_data)[0:10]
            else:
                job_data_demo = list(job_data)
            return_value[job_id] = job_data_demo

        if print_cps:
            print(cps)

        return return_value
