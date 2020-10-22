import shlex
from typing import Dict, Optional, Sequence

from auto_argparse import make_parser, parse_args_and_run


def func(
    x: int,
    things: Optional[Sequence[int]] = None,
    y: str = "test",
    z: bool = False,
    maybe: Optional[float] = 5,
    maybe_not: Optional[str] = None,
    any_dict: Optional[Dict[str, int]] = None,
):
    """
    A very useful function.

    It does many things.
    :param x: the first param
    :param things: variable length!
    :param y: the last param
    """
    print(locals())


def test_func():
    parser = make_parser(func)
    inp = shlex.split("-x 1 -ad '{1: 2}'")
    args = vars(parser.parse_args(inp))
    assert args["x"] == 1
    assert args["any_dict"] == {1: 2}


if __name__ == "__main__":
    parse_args_and_run(func)
