# coding: utf-8
import multiprocessing
import random
import time
import typing
from multiprocessing import Event

from sandbox.benchmark.multiprocessing.lib.shared import SharedDataInterface
from sandbox.benchmark.multiprocessing.lib.work import work
from sandbox.lg import lg


class Executor(object):
    def __init__(
            self,
            number: int,
            job: typing.Callable[[int, int], int],
    ) -> None:
        self.number = number
        self.job = job

    def compute(self, cycles: int, data_weight: int, print_cps: bool = False):
        processes = []  # type: typing.List[multiprocessing.Process]
        start_work_events = []  # type: typing.List[multiprocessing.Event]
        finished_work_events = []  # type: typing.List[multiprocessing.Event]
        exit_event = Event()
        shared_data = self._get_shared_data()

        now = time.time()
        lg.info('Prepare init data')
        for job_id in range(self.number):
            lg.debug('Prepare init data for job {} with weight {}'.format(job_id, data_weight))
            job_data = [0] * data_weight  # type: typing.List[int]
            shared_data.create(job_id, job_data, 'i')
            for i in range(data_weight):
                shared_data.set(job_id, i, random.choice([0, 1]))

        shared_data.commit()
        lg.info('Prepare init data finshed: {}'.format(time.time() - now))

        for job_id in range(self.number):
            finished_work_event = multiprocessing.Event()
            finished_work_events.append(finished_work_event)

            start_work_event = multiprocessing.Event()
            start_work_events.append(start_work_event)

            processes.append(multiprocessing.Process(
                target=work,
                args=(job_id, self.job, shared_data, start_work_event, finished_work_event, exit_event),
            ))

        for process in processes:
            process.start()

        before_start_time = time.time()
        for cycle_id in range(cycles):
            cycle_start_time = time.time()

            for start_work_event in start_work_events:
                start_work_event.set()

            for finished_work_event in finished_work_events:
                finished_work_event.wait()
                finished_work_event.clear()

            lg.info('Cycle {} finished: {}'.format(cycle_id, time.time() - cycle_start_time))

        elapsed = time.time() - before_start_time
        cps = cycles / elapsed
        lg.info('All cycles finished: {} ({}cps)'.format(elapsed, cps))
        exit_event.set()
        for start_work_event in start_work_events:
            start_work_event.set()

        for process in processes:
            process.join()

        return_value = {}
        for job_id in range(self.number):
            return_value[job_id] = list(shared_data.get(job_id))

        if print_cps:
            print(cps)

        return return_value

    def _get_shared_data(self) -> SharedDataInterface:
        raise NotImplementedError()
