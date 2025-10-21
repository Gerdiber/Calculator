import argparse  # 用于解析命令行的参数
import random  # 用于随机生成
import fractions  # 用于运算表达式结果
import re # 用于正则表达式去除题号


def make_num(max_num):
    """生成数字：自然数或分数"""
    if random.random() < 0.3:  # 30%概率生成分数
        d = random.randint(2, max_num - 1)
        n = random.randint(1, d - 1)
        if random.random() < 0.3 and max_num > 5:  # 30%概率生成带分数
            w = random.randint(1, min(3, max_num // d))
            return f"{w}'{n}/{d}"
        return f"{n}/{d}"
    return str(random.randint(0, max_num - 1))


def calc(expr):
    """计算表达式"""
    # 将表达式格式化,部分运算符替换为算法识别的运算符
    expr = expr.replace('×', '*').replace('÷', '/').replace('−','-')
    try:
        return eval(expr, {"__builtins__": None}, {"fractions": fractions.Fraction})
    except:
        # 出现异常返回None
        return None


def format_num(value):
    """格式化数字"""
    # 处理浮点数
    if isinstance(value, float):
        value = fractions.Fraction(value).limit_denominator()
    # 整数直接返回
    if isinstance(value, int):
        return str(value)
    # 处理分数
    if isinstance(value, fractions.Fraction):
        # 为0返回'0'
        if value.numerator == 0:
            return "0"
        # 分子小于分母(值小于1)
        if value.numerator < value.denominator:
            return f"{value.numerator}/{value.denominator}"
        # 分子大于等于分母(值大于1)--化作带分数
        w = value.numerator // value.denominator  # 计算整数
        r = value.numerator % value.denominator  # 计算剩余的分子
        return str(w) if r == 0 else f"{w}'{r}/{value.denominator}"

    return str(value)


class exprNode:
    """表达式生成树节点"""
    def __init__(self, value, left=None, right=None):
        self.value = value # 值,可为数字也可为运算符
        self.left = left # 左子树
        self.right = right # 右子树
        self.result = None # 当前树的运算结果

def check_expr(root):
    """检查表达式合法性"""
    if root == None: # 空树/空节点 则直接返回true
        return True
    LC = check_expr(root.left) # 左子树检查结果
    RC = check_expr(root.right) # 右子树检查结果
    if root.value in ['+', '−', '×', '÷']: # 节点为运算符
        temp_str = f"{root.left.result}{root.value}{root.right.result}"
        temp_result = calc(temp_str) #计算当前子表达式
        if temp_result == None: # 有错误则重新生成
            return False
        if root.value == '−': # 减法情况
            if temp_result < 0: # 结果小于0
                root.left, root.right = root.right, root.left # 左右子树互换
                temp_result = temp_result * -1 # 结果取相反数
        elif root.value == '÷': # 除法情况
            if calc(root.right.result) == 0: # 除数为0
                return False
            if isinstance(temp_result, int) or (isinstance(temp_result, fractions.Fraction)
                                                and temp_result.denominator == 1): # 结果为整数
                return False
        root.result = format_num(temp_result)
    else: # 节点为数字
        root.result = root.value # 运算结果即为节点值
    return True and LC and RC # 左右子树与当前树均合法


def make_expr_str(root):
    """生成表达式的字符串"""
    advance={ # 运算符优先级定义
        '+': 1,
        '−': 1,
        '×': 2,
        '÷': 2
    }
    if root.left.value in ['+', '−', '×', '÷']:
        left_str = f"{root.left.left.value} {root.left.value} {root.left.right.value}"
        if advance[root.left.value] < advance[root.value]:
            left_str = f"({left_str})"
    else:
        left_str = root.left.value
    if root.right.value in ['+', '−', '×', '÷']:
        if root.value == '−' and root.right.value == '−':
            root.right.value = '+'
        right_str = f"{root.right.left.value} {root.right.value} {root.right.right.value}"
        if advance[root.right.value] < advance[root.value]:
            right_str = f"({right_str})"
    else:
        right_str = root.right.value
    return f"{left_str} {root.value} {right_str}"


def make_problem(max_num, count):
    """生成题目"""
    problems = []  # 题目数组
    answers = []  # 答案数组
    seen = set()  # 合法题目集合
    ops = ['+', '−', '×', '÷']  # 待选用运算符

    while len(problems) < count:
        # 决定运算符数量
        op_count = random.randint(1, 3) # 运算符数量
        nums = [make_num(max_num) for _ in range(op_count + 1)] # 运算数字生成
        op_list = [random.choice(ops) for _ in range(op_count)] # 运算符生成
        #生成树根节点
        root = exprNode(op_list[0])
        #根据运算符数量生成
        if op_count == 1: # 单运算符
            root.left = exprNode(nums[0])
            root.right = exprNode(nums[1])
        elif op_count == 2: # 2运算符
            LR = random.randint(0, 1) # 决定运算符在左/右子树
            if LR == 0:
                root.left = exprNode(op_list[1], exprNode(nums[0]), exprNode(nums[1]))
                root.right = exprNode(nums[2])
            else:
                root.right = exprNode(op_list[1], exprNode(nums[0]), exprNode(nums[1]))
                root.left = exprNode(nums[2])
        else: # 3运算符
            root.left = exprNode(op_list[1], exprNode(nums[0]), exprNode(nums[1]))
            root.right = exprNode(op_list[2], exprNode(nums[2]), exprNode(nums[3]))
        # 检查表达式合法性
        if check_expr(root) is False:
            continue
        # 生成字符串并生成答案
        expr = make_expr_str(root)
        answer = calc(expr)
        problems.append(f"{expr} = ")
        answers.append(format_num(answer))

    return problems, answers