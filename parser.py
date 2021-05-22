import re
import math
from lark import Lark, InlineTransformer, Token

grammar = Lark(
    r"""
    ?start  : assign* comp?
    ?assign: NAME "=" comp
    ?comp  : expr "<" expr  -> lt
        | expr "<=" expr -> le
        | expr ">" expr  -> gt
        | expr ">=" expr -> ge
        | expr "!=" expr -> ne
        | expr "==" expr -> eq
        | expr
    ?term  : term "*" pow   -> mul
        | term "/" pow   -> div
        | pow
    ?expr  : expr "-" term  -> sub
        | expr "+" term  -> add
        | term
    ?pow   : atom "^" pow   -> exp
        | atom
    ?atom  : NUMBER                        -> number
        | NAME "(" expr ")"             -> func
        | NAME "(" expr ("," expr)* ")" -> func
        | NAME                          -> var
        | "(" expr ")"
    NAME   : /[-+]?[A-Za-z0-9_]+/
    NUMBER : /-?(?:0|[1-9]\d*)(?:\.\d+)?(?:[eE][+-]?\d+)?/
    %ignore /\s+/
    %ignore /\#.*/
    """
)
class CalcTransformer(InlineTransformer):
    from operator import add, sub, mul, truediv as div, pow as exp, gt, ge, lt, le, ne, eq

    def __init__(self):
        super().__init__()
        self.variables = {k: v for k, v in vars(math).items() if not k.startswith("_")}
        self.variables.update(max=max, min=min, abs=abs)
        self.vars = {}

    def number(self, token):
        try:
            return int(token)
        except ValueError:
            return float(token)

    def func(self, name, *args):
        name = str(name)
        fn = self.variables[name.split('-')[-1]]
        try:
            if name[0] == '-':
                return -fn(*args)
            else:
                fn = self.variables[name]
                return fn(*args)
        except:
            return "Invalid!"

    def var(self, token):
        try:
            if token in self.variables:
                return self.variables[token]
            elif token[0] == "-" and token[1:] in self.variables:
                return -self.variables[token[1:]]
            else:
                return self.vars[token]
        except KeyError:
            return "Invalid: " + str(token)
    
    def start(self, *args):
        return args[-1]

    def assign(self, name, value):
        self.vars[name] = value
        print("###", self.vars[name])
        return self.vars[name]