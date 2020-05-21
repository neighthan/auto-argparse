# auto-argparse

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

See the docstring for `auto_argparse.make_parser` for more details.

## Alternatives

* [`defopt`] is a more mature library which has the same aims as `auto-argparse` but with a slightly different implementation (e.g. `auto-argparse` adds short names, makes all arguments keyword-only, and puts the part of the doc string for each argument into its help string)

[`defopt`]: https://github.com/anntzer/defopt
