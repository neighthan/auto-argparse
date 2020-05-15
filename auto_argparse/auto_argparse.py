import inspect
import re
from argparse import ArgumentParser
from typing import Any, Callable


# TODO: for bool params, do action="store_true"?
def make_parser(func: Callable, add_short_args: bool = True) -> ArgumentParser:
    """
    Automatically configure an argparse parser for `func`.

    To get automatic
    * help strings: write a docstring in the same format as this one (in particular, use
      ":param param_name: help string here").
    * types: use type annotations (List[type] will use nargs="+")
    * defaults: just use defaults
    * required params: this is just the parameters with no default values

    All command line arguments are configured to be "keyword only".

    :param func:
    :param add_short_args: if True, "-<short_name>" is used in addition to
      "--<param_name>". The short names are created by taking the first character of
      each _-delimited substring (e.g. "my_arg" -> "ma"). If multiple short names would
      be the same, none are used.
    """
    docstring = func.__doc__ or ""
    match = re.search(r"(.*?)(?=\n\s*:|$)", docstring, re.DOTALL)
    description = re.sub(r"\n\s*", " ", match.group(1)).strip() if match else ""
    parser = ArgumentParser(description=description)

    signature = inspect.signature(func)

    if add_short_args:
        names = signature.parameters.keys()
        short_names = ["".join(s[0] for s in name.split("_")) for name in names]
        if len(set(short_names)) != len(short_names):  # name conflicts
            add_short_args = False

    for i, param in enumerate(signature.parameters.values()):
        match = re.search(
            fr":param {param.name}:(.+?)(?=\n\s*:|$)", docstring, re.DOTALL
        )
        help_str = re.sub(r"\n\s*", " ", match.group(1)).strip() if match else ""
        kwargs = {"help": help_str}

        if getattr(param.annotation, "_name", None) == "List":  # e.g. List[int]
            kwargs["type"] = param.annotation.__args__[0]
            kwargs["nargs"] = "+"
        else:
            if param.annotation is not inspect._empty:
                kwargs["type"] = param.annotation

        if param.default is not inspect._empty:
            kwargs["default"] = param.default
        else:
            kwargs["required"] = True
        if add_short_args:
            parser.add_argument(f"-{short_names[i]}", f"--{param.name}", **kwargs)
        else:
            parser.add_argument(f"--{param.name}", **kwargs)
    return parser


def parse_args_and_run(func: Callable) -> Any:
    """Create a parser for `func` then execute func with the parsed arguments."""
    parser = make_parser(func)
    args = parser.parse_args()
    return func(**vars(args))
