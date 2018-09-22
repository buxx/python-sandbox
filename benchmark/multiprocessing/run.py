# coding: utf-8
import multiprocessing
import random
import sys
import enum

from benchmark.multiprocessing.lib.manager import ManagerExecutor

assert sys.version_info >= (3, 6), "Script wrote for Python 3.6+"


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

    # TODO: number grow up to faster: divide him to be inferior of 1000000
    return v


def main(mode: Mode, number: int, cycles: int) -> None:
    if mode == Mode.manager:
        executor = ManagerExecutor(number=number, job=job)
    elif mode == Mode.sharedmem:
        executor = SharedMemExecutor(number=number, job=job)
    else:
        raise NotImplementedError()

    result = executor.compute(cycles=cycles)


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
        '--number',
        '-n',
        type=int,
        default=__DEFAULT__,
        help='Number of parrallel experience to make. Default value: number of cpu cores'
    )

    args = parser.parse_args()
    main(
        mode=args.mode,
        number=args.number if args.number != __DEFAULT__ else CPU_CORE_COUNT,
        cycles=args.cycles,
    )
