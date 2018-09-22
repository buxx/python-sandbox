# coding: utf-8
import typing
from multiprocessing import Event

from benchmark.multiprocessing.lib.shared import SharedDataInterface


def work(
        job_id: int,
        target: typing.Callable[[int, int], int],
        shared_data: SharedDataInterface,
        start_work_event: Event,
        finished_work_event: Event,
        exit_event: Event,
) -> None:
    v = shared_data.get(job_id)
    # TODO: logger (static in project)

    while True:
        # print('job_{}: Wait start work event'.format(job_id))
        start_work_event.wait()
        start_work_event.clear()
        # print('job_{}: Start job received'.format(job_id))

        if exit_event.is_set():
            return

        # print('job_{}: Start to work'.format(job_id))
        v += target(v, 1000)  # TODO: in parameter
        shared_data.set(job_id, v)
        if job_id == 0:
            print(v)
        # print('job_{}: Jon finished, send finished work event'.format(job_id))
        finished_work_event.set()
