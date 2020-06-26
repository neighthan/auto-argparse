from typing import Optional, Sequence

from auto_argparse import parse_args_and_run


def func(
    x: int,
    things: Optional[Sequence[int]] = None,
    y: str = "test",
    z: bool = False,
    maybe: Optional[float] = 5,
    maybe_not: Optional[str] = None,
):
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
