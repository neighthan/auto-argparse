from typing import List

from auto_argparse import parse_args_and_run


def func(x: int, things: List[int], y: str = "test", z: bool = False):
    """
    A very useful function.

    It does many things.
    :param x: the first param
    :param things: variable length!
    :param y: the last param
    """
    print(locals())


if __name__ == "__main__":
    parse_args_and_run(func)
