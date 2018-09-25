# coding: utf-8
import typing
from multiprocessing import Event

from sandbox.benchmark.multiprocessing.lib.shared import SharedDataInterface
from sandbox.lg import lg


def work(
        job_id: int,
        target: typing.Callable[[int, int], int],
        shared_data: SharedDataInterface,
        start_work_event: Event,
        finished_work_event: Event,
        exit_event: Event,
) -> None:
    values = shared_data.get(job_id)
    data_weight = len(values)

    while True:
        lg.debug('job_{}: Wait start work event'.format(job_id))
        start_work_event.wait()
        start_work_event.clear()
        lg.debug('job_{}: Start job received'.format(job_id))

        if exit_event.is_set():
            lg.debug('job_{}: Exit requested, exiting'.format(job_id))
            return

        lg.debug('job_{}: Start to work'.format(job_id))

        for i, value in enumerate(values):
            new_value = target(value, 100)  # TODO: in parameter: it is cpu working
            shared_data.set(job_id, i, new_value)

        lg.debug('job_{}: Job finished, send finished work event'.format(
            job_id,
        ))
        finished_work_event.set()
