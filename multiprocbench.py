# coding: utf-8
import logging
import multiprocessing
import subprocess
import sys
import enum

import matplotlib.pyplot as plt

from sandbox.benchmark.multiprocessing.manager import ManagerExecutor
from sandbox.benchmark.multiprocessing.mono import MonoExecutor
from sandbox.benchmark.multiprocessing.sharedmem import SharedmemExecutor
from sandbox.benchmark.multiprocessing.redis import RedisExecutor
from sandbox.lg import lg

assert sys.version_info >= (3, 5), "Script wrote for Python 3.5+"


__DEFAULT__ = -1
CHOICES = [0, 1]
CPU_CORE_COUNT = multiprocessing.cpu_count()


class Mode(enum.Enum):
    mono = 'mono'
    manager = 'manager'
    sharedmem = 'sharedmem'
    redis = 'redis'


def job(start: int, n: int) -> int:
    """
    Add random integer between 0 and 1 to given start number and do it n times
    :param start: start number
    :param n: count of iteration
    :return: computed result
    """
    v = start
    for i in range(n):
        v += 1

    # Reduce value
    while v > 1000000:
        v = v/2

    return int(v)


def main(mode: Mode, number: int, cycles: int, data_weight: int, print_cps: bool = False) -> None:
    if mode == Mode.manager:
        executor = ManagerExecutor(number=number, job=job)
    elif mode == Mode.sharedmem:
        executor = SharedmemExecutor(number=number, job=job)
    elif mode == Mode.mono:
        executor = MonoExecutor(number=number, job=job)
    elif mode == Mode.redis:
        executor = RedisExecutor(number=number, job=job)
    else:
        raise NotImplementedError()

    r = executor.compute(cycles=cycles, data_weight=data_weight, print_cps=print_cps)

    print_value = {}
    for job_id, job_data in r.items():
        if 10 <= len(job_data):
            job_data_demo = list(job_data)[0:10]
        else:
            job_data_demo = list(job_data)
        print_value[job_id] = job_data_demo

    lg.info('Result (may be sliced): {}'.format(print_value))

    for job_id, job_data in r.items():
        lg.info('Final result {}: {}'.format(job_id, sum(job_data)))


def generate_plot_viz(args):
    modes = [args.mode.value] + list(map(lambda i: i.strip(), args.plot_modes.split(',')))
    weights = [args.weight] + list(map(int, map(lambda i: i.strip(), args.plot_weights.split(','))))

    for mode in modes:
        mode_results = ([], [])
        for i, weight in enumerate(weights):
            command = '{} multiprocbench.py {} {} {} --print-only-cps'.format(
                sys.executable,
                mode,
                args.cycles,
                weight,
            )
            result = float(subprocess.check_output(command.split(' ')).strip().decode())
            mode_results[0].append(weight)
            mode_results[1].append(result)

        plt.plot(mode_results[0], mode_results[1], label=mode, marker='o')

    plt.legend(loc='upper left')
    plt.show()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='Make some benchmark with parralelism '
                    'about iterative computing',
    )
    parser.add_argument(
        'mode',
        type=Mode,
        choices=list(Mode),
        help='Choose mode of parralelism:'
             ' manager: use multiprocessing.Manager.'
             ' sharedmem: use multiprocessing.Value|Array.'
             ' mono: no use multiprocessing.'
             ' redis: use redis database.'
    )
    parser.add_argument(
        'cycles',
        type=int,
        help='Number of computing cycles'
    )
    parser.add_argument(
        'weight',
        type=int,
        help='Size of data must be shared between processes'
    )
    parser.add_argument(
        '--number',
        '-n',
        type=int,
        default=__DEFAULT__,
        help='Number of parrallel experience to make. Default value: number of cpu cores'
    )
    parser.add_argument(
        '-v',
        action='store_true',
        help='Print info logs',
    )
    parser.add_argument(
        '-vv',
        action='store_true',
        help='Print debug logs',
    )
    parser.add_argument(
        '--plot-weights',
        type=str,
        help='list of weight for plot viz (ex: 10,50,100,500)',
    )
    parser.add_argument(
        '--plot-modes',
        type=str,
        help='list of additional modes for plot viz (ex: manager,xxxxx)',
    )
    parser.add_argument(
        '--print-only-cps',
        action='store_true',
        help='Print only Cycle Per Seconds',
    )

    args = parser.parse_args()

    if args.plot_weights:
        generate_plot_viz(args)
        exit(0)

    if not args.print_only_cps:
        if args.v:
            logger = logging.getLogger()
            logger.setLevel(logging.INFO)

        if args.vv:
            logger = logging.getLogger()
            logger.setLevel(logging.DEBUG)

    main(
        mode=args.mode,
        number=args.number if args.number != __DEFAULT__ else CPU_CORE_COUNT,
        cycles=args.cycles,
        data_weight=args.weight,
        print_cps=args.print_only_cps,
    )
