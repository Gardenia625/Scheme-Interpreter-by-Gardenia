from parser import *
from primitives import *
# 以下两行是为了在 WIN10 上正确显示颜色
from colorama import init as colorama_init
colorama_init()

class Frame:
    def __init__(self, parent):
        self.parent = parent
        self.bindings = {}
    def lookup(self, key):
        """在环境中查找 var 的值"""
        if key in self.bindings:
            return self.bindings[key]
        elif self.parent:
            return self.parent.lookup(key)
        else:
            raise SchemeError("变量 {} 未定义".format(key))
    def define(self, key, val): 
        """将 key 绑定到 val 上"""
        self.bindings[key] = val
    def create_new_frame(self, keys, vals): 
        """建立一个 self 的子环境"""
        frame = Frame(self)
        while isinstance(keys, Pair):
            frame.define(keys.a, vals.a)
            keys, vals = keys.b, vals.b
        return frame
    def __str__(self):
        return str(self.bindings)

class Lambda:
    def __init__(self, formals, body, env):
        self.formals = formals
        self.body = body
        self.env = env
    def __str__(self):
        return "(lambda {} {})".format(self.formals, self.body)
    
# =============================================================================
# 核心部分
# =============================================================================

def s_eval(exp, env):
    """求值"""
    if exp is nil or isinstance(exp, (int, float)): # 常量
        return exp
    elif isinstance(exp, str):
        if exp[0] != '"': # 变量
            return env.lookup(exp)
        elif exp[-1] == '"': # 字符串
            return exp[1:-1]
        else:
            raise SchemeError("{} 缺少双引号".format(exp))
    elif isinstance(exp, Pair):
        first, rest = exp.a, exp.b
        if first in special_forms:
            return special_forms[first](rest, env)
        else:
            func = s_eval(first, env)
            args = rest.map(lambda x: s_eval(x, env))
            return s_apply(func, args, env)
    else:
        raise SchemeError("无法对 {} 求值".format(exp))
        
def s_apply(func, args, env):
    """应用函数"""
    if isinstance(func, Primitive): # 应用内置函数
        para = []
        while args:
            para.append(args.a)
            args = args.b
        if func.use_env: # eval 等函数需要用到当前环境
            para.append(env)
        return func.f(*para)
    elif isinstance(func, Lambda): # 应用自定义函数, 即 lambda 表达式
        frame = func.env.create_new_frame(func.formals, args)
        return s_begin(func.body, frame)
    else:
        raise SchemeError("无法调用 {}".format(func))
        
# =============================================================================
# 特殊形式
# =============================================================================

def s_begin(vals, env): # 逐个运行 begin 后的表达式
    while vals:
        result = s_eval(vals.a, env)
        vals = vals.b
    return result

def s_lambda(vals, env): # 定义 lambda 表达式
    formals, body = vals.a, vals.b
    return Lambda(formals, body, env)

def s_define(vals, env): # 定义变量, 不返回值
    if isinstance(vals[0], Pair): # 处理特殊语法 (define (f x) (* x 2))
        formals, body = vals[0].b, vals.b
        lam = s_lambda(Pair(formals, body), env)
        env.define(vals[0][0], lam)
    else: # (define x 2)
        env.define(vals[0], s_eval(vals[1], env))
    return NoNo
    
def s_quote(vals, env): # quote 阻止其后的表达式被计算
    return vals

def s_and(vals, env):
    result = True
    while isinstance(vals, Pair):
        result = s_eval(vals.a, env)
        if result is False:
            return False
        vals = vals.b
    return result

def s_or(vals, env):
    result = False
    while isinstance(vals, Pair):
        result = s_eval(vals.a, env)
        if result is not False:
            return result
        vals = vals.b
    return False

def s_if(vals, env):
    if s_eval(vals[0], env) is not False:
        return s_eval(vals[1], env)
    elif len(vals) == 3:
        return s_eval(vals[2], env)
    else: # 若没有 else 条款, 返回未定义值
        return NoNo

def s_cond(vals, env):
    while isinstance(vals, Pair):
        if vals[0][0] == "else" or s_eval(vals[0][0], env) is not False:
            if vals[0].b is nil:
                return s_eval(vals[0][0], env)
            else:
                return s_begin(vals[0].b, env)
        vals = vals.b

def s_let(vals, env):
    binds, body = vals.a, vals.b
    frame = env.create_new_frame(nil, nil)
    while isinstance(binds, Pair):
        frame.define(binds[0][0], s_eval(binds[0][1], env))
        binds = binds.b
    return s_begin(body, frame)
    
    
special_forms = {"begin": s_begin,
                 "lambda": s_lambda,
                 "define": s_define,
                 "quote": s_quote,
                 "and": s_and,
                 "or": s_or,
                 "if": s_if,
                 "cond": s_cond,
                 "let": s_let}

# =============================================================================
# 交互式解释器
# =============================================================================

env_global = Frame(None)
for key, val in s_primitives:
    env_global.define(key, val)
env_global.define("eval", Primitive(s_eval, True))

RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
C_END = "\033[0m"

while 1:
    try:
        empty_input = 0
        atoms = lexer(input(GREEN + "scheme>>> "  + C_END))
        parentheses = atoms.count("(") - atoms.count(")")
        # 如果 "(" 多于 ")" 则等待用户继续输入
        while parentheses > 0:
            new_atoms = lexer(input(GREEN + "      ... "  + C_END))
            # 连续两次空输入会强制运行
            if not new_atoms:
                empty_input += 1
                if empty_input == 2:
                    break
            else:
                empty_input = 0
            parentheses += new_atoms.count("(") - new_atoms.count(")")
            atoms += new_atoms
        exp = parser(atoms)
        while isinstance(exp, Pair):
            result = s_eval(exp.a, env_global)
            exp = exp.b
            if result is not NoNo:
                print(BLUE + str(result) + C_END)
    except SchemeError as e:
        print(RED + "错误: " + str(e) + C_END)