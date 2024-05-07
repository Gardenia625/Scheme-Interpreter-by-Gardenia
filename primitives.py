import operator
from functools import reduce
from parser import nil, Pair

class NoNo:
    """NoNo 作为返回值时不会被打印"""
NoNo = NoNo()

class Primitive:
    def __init__(self, f, use_env = False):
        self.f = f
        self.use_env = use_env
    def __str__(self):
        return self.name

def primitive(name):
    """将函数转换为 Primitive 类型, 并填入 s_primitives"""
    def make_primitive(f):
        pr = Primitive(f)
        s_primitives.append((name, pr))
        return f
    return make_primitive

s_primitives = []

@primitive("+")
def s_add(*vals):
    return reduce(operator.add, vals, 0)

@primitive("-")
def s_sub(*vals):
    if len(vals) == 1:
        return - vals[0]
    else:
        return reduce(operator.sub, vals[1:], vals[0])
    
@primitive("*")
def s_mul(*vals):
    return reduce(operator.mul, vals, 1)

@primitive("/")
def s_div(*vals):
    if len(vals) == 1:
        return 1 / vals[0]
    else:
        return reduce(operator.truediv, vals[1:], vals[0])
    
@primitive("cons")
def s_cons(a, b):
    return Pair(a, b)

@primitive("car")
def s_car(p):
    return p.a

@primitive("cdr")
def s_cdr(p):
    return p.b

@primitive("list")
def s_list(first, *rest):
    if rest:
        return Pair(first, s_list(*rest))
    else:
        return Pair(first, nil)

@primitive("newline")
def s_newline():
    print()
    return NoNo

@primitive("display")
def s_display(s):
    print(str(s), end="")
    return NoNo

@primitive("print")
def s_print(s):
    print(str(s))
    return NoNo

@primitive("=")
def s_eq(a, b):
    return a == b

@primitive("<")
def s_le(a, b):
    return a < b

@primitive(">")
def s_ge(a, b):
    return a > b

@primitive("<=")
def s_leq(a, b):
    return a <= b

@primitive(">=")
def s_geq(a, b):
    return a >= b