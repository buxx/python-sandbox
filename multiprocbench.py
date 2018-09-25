# coding: utf-8
import logging
import multiprocessing
import random
import sys
import enum

from sandbox.benchmark.multiprocessing.manager import ManagerExecutor
from sandbox.benchmark.multiprocessing.sharedmem import SharedmemExecutor
from sandbox.lg import lg

assert sys.version_info >= (3, 5), "Script wrote for Python 3.5+"


__DEFAULT__ = -1
CHOICES = [0, 1]
CPU_CORE_COUNT = multiprocessing.cpu_count()


class Mode(enum.Enum):
    manager = 'manager'
    sharedmem = 'sharedmem'


def job(start: int, n: int) -> int:
    """
    Add random integer between 0 and 1 to given start number and do it n times
    :param start: start number
    :param n: count of iteration
    :return: computed result
    """
    v = start
    for i in range(n):
        v += random.choice(CHOICES)

    # Reduce value
    while v > 1000000:
        v = v/2

    return int(v)


def main(mode: Mode, number: int, cycles: int, data_weight: int) -> None:
    if mode == Mode.manager:
        executor = ManagerExecutor(number=number, job=job)
    elif mode == Mode.sharedmem:
        executor = SharedmemExecutor(number=number, job=job)
    else:
        raise NotImplementedError()

    r = executor.compute(cycles=cycles, data_weight=data_weight)
    lg.info('Result (may be sliced): {}'.format(r))


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
             ' sharedmem: use multiprocessing.Value|Array'
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

    args = parser.parse_args()

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
    )
