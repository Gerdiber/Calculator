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