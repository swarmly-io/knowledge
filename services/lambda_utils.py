from __future__ import annotations
import json

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
    
def remove_empty_lines(lines):
    for l in lines:
        if not not l:
            yield l

def parse_function(func: Callable[..., Any], fn_name = None) -> Function:

    # Get the function arguments
    args = func.__code__.co_varnames[:func.__code__.co_argcount]

    # Get the function body
    source = list(remove_empty_lines(inspect.getsource(func).split('\n')))
    if len(source) > 1 and func.__name__ != '<lambda>':
        lines = source[1:]
        return_line = next((line for line in lines if line.strip().startswith('return')), None)
        if return_line:
            return_value = return_line.strip().replace('return', '').strip()
        name = func.__name__
    else:
        sep = source[0].replace('==', '|').split('lambda')[0].strip()
        if '=' in sep:
            fn_seperator = '='
        elif ':' in sep:
            fn_seperator = ':'
        else:
            fn_seperator = ''
        
        if fn_seperator == '=':
            name, body = source[0].split(':')            
            return_value = body.strip()
            name = name.strip().split("=")[0].strip()
        elif fn_seperator == ':':
            name, body = source[0].split('lambda')
            name = name.split(':')[0].split('=')[0].replace('{', '').replace('}', '').strip().replace('\'', '')
            body = body.split(':')[1].replace('{', '').replace('}', '').strip()
            return_value = body.strip()
        else:
            name = fn_name or 'lambda'
            _, body = source[0].split('lambda')
            body = body.split(':')[1].replace('{', '').replace('}', '').strip()
            return_value = body.strip()
    
    return Function(name=name, func=Func(args=list(args), body=return_value))

def function_to_yaml(func: Function):
    # Convert the YAML data to a string
    return yaml.dump(func.dict(), Dumper=yaml.Dumper)

def function_to_json(func: Function):
    # Convert the YAML data to a string
    return json.dumps(func.dict())

if __name__ == "__main__":
    def only_trade(x, y):
        return x['name'] == y['name']

    test = lambda x, y: x['name'] == y['name']

    test1 = { 'x': 
        lambda x, y: x['name'] == y['name'] }

    parsed = parse_function(only_trade)
    print(function_to_yaml(parsed))
    assert function_to_json(parsed) == '{"func": {"args": ["x", "y"], "body": "x[\'name\'] == y[\'name\']"}, "name": "only_trade"}'
    
    parsed = parse_function(test)
    print(function_to_yaml(parsed))
    assert function_to_json(parsed) == '{"func": {"args": ["x", "y"], "body": "x[\'name\'] == y[\'name\']"}, "name": "test"}'
    
    parsed = parse_function(test1['x'])
    print(function_to_yaml(parsed))
    assert function_to_json(parsed) == '{"func": {"args": ["x", "y"], "body": "x[\'name\'] == y[\'name\']"}, "name": "lambda"}'