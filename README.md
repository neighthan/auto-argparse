# auto-argparse

[![PyPI version](https://badge.fury.io/py/auto-argparse.svg)](https://badge.fury.io/py/auto-argparse)

## Install

For the current release:

```bash
pip install auto-argparse
```

For the latest version from GitHub:

```bash
pip install git+https://github.com/neighthan/auto-argparse
```

## Usage

Replace something like

```python
from argparse import ArgumentParser
from typing import List

def func(x: int, things: List[int], y: str="test"):
    """
    A very useful function.

    It does many things.
    :param x: the first param
    :param things: variable length!
    :param y: the last param
    """

def parse_args():
    description = "A very useful function.\n\nIt does many things."
    parser = ArgumentParser(description=description)
    # have to replicate all of `func`s arguments here, including their types, defaults,
    # and help strings. And make sure to update this if you ever change `func`!
    parser.add_argument("-x", "--x", type=int, required=True, help="the first param")
    parser.add_argument(
      "-t", "--things", nargs="+", type=int, required=True, help="variable length!"
    )
    parser.add_argument("-y", "--y", type=str, help="the last param")
    return parser.parse_args()

if __name__ == "__main__":
    func(**vars(parse_args()))
```

with

```python
from typing import List
from auto_argparse import parse_args_and_run

def func(x: int, things: List[int], y: str="test"):
    """
    A very useful function.

    It does many things.
    :param x: the first param
    :param things: variable length!
    :param y: the last param
    """

if __name__ == "__main__":
    parse_args_and_run(func)
```

See the docstring for [`auto_argparse.make_parser`] for more details.

## Supported Types

The following types should be fully supported, but any annotation `T` should work if `T(cli_string)` gives the desired value, where `cli_string` is the string entered at the command line.
* `int`
* `float`
* `str`
* `bool`
* `List[T]`, `Sequence[T]` where `T` is any of (`int`, `float`, `str`) or as described in the paragraph above
* `Optional[T]` where `T` could additionally be `List` or `Sequence`. Note that there's no way to explicitly enter a `None` value from the command-line though it can be the default value.

## Alternatives

* [`defopt`] is a more mature library which has the same aims as `auto-argparse` but with a slightly different implementation (e.g. `auto-argparse` adds short names, makes all arguments keyword-only, and puts the part of the doc string for each argument into its help string)

[`auto_argparse.make_parser`]: auto_argparse/auto_argparse.py
[`defopt`]: https://github.com/anntzer/defopt
