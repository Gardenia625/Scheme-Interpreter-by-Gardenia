import re

def lexer(exp):
    """将输入分割为 atoms"""
    exp = re.sub("\(", " ( ", exp)
    exp = re.sub("\)", " ) ", exp)
    exp = re.sub("'", " quote ", exp)
    atoms = exp.lower().split() # Scheme 不区分大小写
    return atoms

def parser(atoms):
    """生成语法树, 返回一个嵌套列表"""  
    def tokenize(x):
        """将 atom 转换为 scheme 中的类型"""
        if x == "nil":
            return nil
        elif x == "#t": # Bool 值
            return True
        elif x == "#f":
            return False
        elif x[0].isdigit(): # 数值
            try:
                return int(x)   
            except:
                try:
                    return float(x)
                except:
                    raise SchemeError("变量名不能以数字开头")
        else: # 变量
            return x
        
    def quote():
        nonlocal i
        if i == n:
            raise SchemeError("不能引用空")
        cur = atoms[i]
        i += 1
        if cur in ["quote", ")"]:
            raise SchemeError("不能引用空")
        if cur == "(":
            return Pair("quote", s_parser())
        else:
            return Pair("quote", tokenize(cur))
            
    def s_parser():
        nonlocal i
        if i == n:
            raise SchemeError("缺少 ')'")
        cur = atoms[i]
        i += 1
        if cur == "(":
            return Pair(s_parser(), s_parser())
        elif cur == ")":
            return nil
        elif cur == "quote":
            return Pair(quote(), s_parser())
        else:
            return Pair(tokenize(cur), s_parser())
        
    atoms += [")"]
    i, n = 0, len(atoms)
    result = s_parser()
    if i < n:
        raise SchemeError("缺少 '('")
    return result

class nil:
    def __repr__(self): # nil 等价于空列表
        return "nil"
    def __str__(self):
        return "()"
    def __len__(self): # nil 的真值为假
        return 0
    def map(self, f):
        return self
nil = nil() # 隐藏 nil 类

class Pair:
    """Scheme 中的 Pair 类型"""
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __repr__(self): # 在 python 中的等价表示
        return "Pair({}, {})".format(repr(self.a), repr(self.b))
    def __str__(self): # 在 scheme 中的等价表示
        s = "(" + str(self.a)
        nxt = self.b
        while isinstance(nxt, Pair):
            s += " " + str(nxt.a)
            nxt = nxt.b
        if nxt is not nil:
            s += " . " + str(nxt)
        return s + ")"
    def __len__(self):
        result = 0
        while isinstance(self, Pair):
            result += 1
            self = self.b
        return result
    def __getitem__(self, k):
        while k > 0:
            k -= 1
            self = self.b
        return self.a
    def map(self, f):
        return Pair(f(self.a), self.b.map(f))
        
class SchemeError(Exception):
    """预设的报错, 不终止运行"""