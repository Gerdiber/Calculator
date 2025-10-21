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

def check_answers(ex_file, ans_file):
    """批改答案"""
    pattern = r'^\d+\.\s*'
    with open(ex_file, 'r', encoding='utf-8') as f:
        ex_list = [line.strip() for line in f]  # 题目列表

    with open(ans_file, 'r', encoding='utf-8') as f:
        ans_list = [line.strip() for line in f]  # 答案列表

    right = []  # 正确数组
    wrong = []  # 错误数组

    for i, (ex, ans) in enumerate(zip(ex_list, ans_list), 1):
        expr = re.sub(pattern,'', ex.replace('=', ''))
        ans = re.sub(pattern,'', ans)
        correct_ans = format_num(calc(expr))  # 计算正确答案
        if ans == correct_ans:  # 正确
            right.append(i)  # 将题目编号加入正确数组中
        else:  # 错误
            wrong.append(i)  # 将题目编号加入错误数组中

    return right, wrong


def main():
    parser = argparse.ArgumentParser(description='四则运算题目生成器')
    parser.add_argument('-n', type=int, help='题目数量')
    parser.add_argument('-r', type=int, help='数字范围')
    parser.add_argument('-e', type=str, help='题目文件')
    parser.add_argument('-a', type=str, help='答案文件')

    args = parser.parse_args()

    if args.e and args.a:
        # 批改模式
        right, wrong = check_answers(args.e, args.a)
        with open('Grade.txt', 'w', encoding='utf-8') as f:
            f.write(f"Correct: {len(right)} ({', '.join(map(str, right))})\n")
            f.write(f"Wrong: {len(wrong)} ({', '.join(map(str, wrong))})\n")
        print("批改完成！")

    elif args.r and args.n:
        # 生成模式
        problems, answers = make_problem(args.r, args.n)

        with open('Exercises.txt', 'w', encoding='utf-8') as f:
            for i, p in enumerate(problems):
                f.write(f"{i+1}. {p}\n")

        with open('Answers.txt', 'w', encoding='utf-8') as f:
            for i, a in enumerate(answers):
                f.write(f"{i+1}. {a}\n")

        print(f"生成 {args.n} 道题目完成！")

    else:
        # 异常则提示
        print("用法:")
        print("  生成: python calculator.py -n 数量 -r 范围")
        print("  批改: python calculator.py -e 题目文件 -a 答案文件")


if __name__ == "__main__":
    main()