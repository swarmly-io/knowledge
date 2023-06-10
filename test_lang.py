from __future__ import annotations

import yaml
from typing import Any, Callable, List
import inspect
from pydantic import BaseModel


class Func(BaseModel):
    args: List[str]
    body: str

class Function(BaseModel):
    func: Func
    name: str

def function_to_yaml(func: Callable[..., Any]) -> str:

    # Get the function arguments
    args = func.__code__.co_varnames[:func.__code__.co_argcount]

    # Get the function body
    lines = inspect.getsource(func).split('\n')[1:]

    # Find the line with "return" statement
    return_line = next((line for line in lines if line.strip().startswith('return')), None)
    if return_line:
        return_value = return_line.strip().replace('return', '').strip()

    function = Function(name=func.__name__, func=Func(args=list(args), body=return_value))

    # Convert the YAML data to a string
    yaml_str = yaml.dump(function.dict(), Dumper=yaml.Dumper)

    return yaml_str


def only_trade(x, y):
    return x['name'] == y['name']

print(function_to_yaml(only_trade))