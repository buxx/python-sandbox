# coding: utf-8
import multiprocessing
import typing
from multiprocessing import Event

from sandbox.benchmark.multiprocessing.lib.shared import SharedDataInterface
from sandbox.benchmark.multiprocessing.lib.work import work


class ManagerSharedData(SharedDataInterface):
    def __init__(self, data):
        self.data = data

    def get(self, key):
        return self.data[key]

    def set(self, key, value):
        self.data[key] = value


class ManagerExecutor(object):
    def __init__(
            self,
            number: int,
            job: typing.Callable[[int, int], int],
    ) -> None:
        self.number = number
        self.job = job

    def compute(self, cycles: int):
        with multiprocessing.Manager() as manager:
            data = manager.dict()
            processes = []  # type: typing.List[multiprocessing.Process]
            start_work_events = []  # type: typing.List[multiprocessing.Event]
            finished_work_events = []  # type: typing.List[multiprocessing.Event]
            exit_event = Event()

            for job_id in range(self.number):
                data[job_id] = 0

            shared_data = ManagerSharedData(data)
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

            for cycle_id in range(cycles):
                for start_work_event in start_work_events:
                    start_work_event.set()

                for finished_work_event in finished_work_events:
                    finished_work_event.wait()
                    finished_work_event.clear()

            exit_event.set()
            for start_work_event in start_work_events:
                start_work_event.set()

            for process in processes:
                process.join()

            print(data)
