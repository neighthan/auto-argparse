import inspect
import json
import re
from argparse import ArgumentParser, ArgumentTypeError
from collections.abc import Sequence
from typing import Any, Callable, Dict, TypeVar, Union

T = TypeVar("T")


def make_parser(
    func: Callable, add_short_args: bool = True, validate_dict_types: bool = False
) -> ArgumentParser:
    """
    Automatically configure an argparse parser for `func`.

    To get automatic
    * help strings: write a docstring in the same format as this one (in particular, use
      ":param param_name: help string here").
    * types: use type annotations. The only supported types from `typing` are listed below.
      * `List[type]` and `Sequence[type]` will use `nargs="+", type=type`.
      * `Optional[type]` converts inputs using `type`; a `None` is only possible if this
        is the default value.
      * `Dict[key_type, val_type]` uses `json.loads` or, if the input doesn't parse as
        JSON and it's available, `yaml.safe_load` to parse the input. If the parsed
        value is not a dictionary, an `ArgumentTypeError` is thrown. Tips:
          * quote the dictionary argument on the command line
          * JSON: use double-quotes around all strings (`-p '{"key": "val"}'`)
          * JSON: keys must be strings
          * YAML: put spaces between keys and values (`-p "{key: val}"` NOT `-p "{key:val}"`)
      * `bool` uses `str2bool`; values have to be entered like `--debug True`
    * defaults: just use defaults
    * required params: this is just the parameters with no default values

    All command line arguments are configured to be "keyword only".

    Except for the exceptions noted above, the type annotation will be used directly as
    the type for the parser. This means it must be a callable which accepts a single
    string as input and returns the desired Python object.

    :param func:
    :param add_short_args: if True, "-<short_name>" is used in addition to
      "--<param_name>". The short names are created by taking the first character of
      each _-delimited substring (e.g. "my_arg" -> "ma"). If multiple short names would
      be the same, none are used.
    :param validate_dict_types: if True, `ArgumentTypeError` is thrown if any dictionary
      keys / values aren't of the proper type.
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
        kwargs = {}
        anno = param.annotation
        origin = getattr(anno, "__origin__", None)
        if origin in (list, Sequence):  # e.g. List[int]
            kwargs["type"] = anno.__args__[0]
            kwargs["nargs"] = "+"
        elif origin == Union:  # Optional[T] is converted to Union[T, None]
            if len(anno.__args__) == 2 and anno.__args__[1] == type(None):
                anno = anno.__args__[0]
                origin = getattr(anno, "__origin__", None)
                if origin in (list, Sequence):
                    kwargs["nargs"] = "+"
                    kwargs["type"] = anno.__args__[0]
                elif origin == dict:
                    key_type, val_type = anno.__args__
                    dict_type = make_dict_type(key_type, val_type, validate_dict_types)
                    kwargs["type"] = dict_type
                elif anno == bool:
                    kwargs["type"] = str2bool
                else:
                    kwargs["type"] = anno
        elif origin == dict:
            key_type, val_type = anno.__args__
            dict_type = make_dict_type(key_type, val_type, validate_dict_types)
            kwargs["type"] = dict_type
        else:
            if anno is not param.empty:
                if anno == bool:
                    kwargs["type"] = str2bool
                else:
                    kwargs["type"] = anno

        if param.default is not param.empty:
            kwargs["default"] = param.default
        else:
            kwargs["required"] = True

        match = re.search(
            fr":param {param.name}:(.+?)(?=\n\s*:|$)", docstring, re.DOTALL
        )
        help_str = re.sub(r"\n\s*", " ", match.group(1)).strip() if match else ""
        annotation_str = inspect.formatannotation(anno)
        if "default" in kwargs:
            help_str += f" [{annotation_str}={kwargs['default']}]"
        else:
            help_str += f" [{annotation_str}]"
        kwargs["help"] = help_str

        if add_short_args:
            parser.add_argument(f"-{short_names[i]}", f"--{param.name}", **kwargs)
        else:
            parser.add_argument(f"--{param.name}", **kwargs)
    return parser


def parse_args_and_run(func: Callable[..., T]) -> T:
    """Create a parser for `func` then execute func with the parsed arguments."""
    parser = make_parser(func)
    args = parser.parse_args()
    return func(**vars(args))


def str2bool(v: str) -> bool:
    """Convert a string into a Boolean value."""
    v = v.lower().strip()
    if v == "true":
        return True
    if v == "false":
        return False
    raise ArgumentTypeError("Boolean value expected.")


def make_dict_type(key_type, val_type, validate_types: bool = False):
    """
    :rtype: Callable[[str], Dict[key_type, val_type]]
    """

    def dict_type(inp: str) -> Dict[key_type, val_type]:
        try:
            d = json.loads(inp)
        except json.JSONDecodeError:
            try:
                import yaml
            except ImportError:
                raise ArgumentTypeError()
            d = yaml.safe_load(inp)
        if not isinstance(d, dict):
            raise ArgumentTypeError("Input did not parse as a dictionary.")
        if validate_types:
            for k, v in d.items():
                if not isinstance(k, key_type):
                    raise ArgumentTypeError(
                        f"Key {k} is not of expected type {key_type}."
                    )
                if not isinstance(v, val_type):
                    raise ArgumentTypeError(
                        f"Value {v} is not of expected type {val_type}."
                    )
        return d

    return dict_type
