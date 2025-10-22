import unittest
from unittest.mock import patch
import os
import tempfile
import fractions
import calculator
from calculator import make_num, calc, format_num, check_expr, exprNode, make_problem, check_answers


class TestCalculator(unittest.TestCase):

    def setUp(self):
        """测试前的准备工作"""
        self.temp_dir = tempfile.mkdtemp()
    def tearDown(self):
        """测试后的清理工作"""
        import shutil
        shutil.rmtree(self.temp_dir)


    def test_make_num(self):
        """测试数字生成函数"""
        # 测试多次生成，确保不会崩溃
        for _ in range(100):
            num = make_num(10)
            self.assertIsNotNone(num)
            self.assertIsInstance(num, str)


    def test_calc(self):
        """测试表达式计算函数"""
        # 测试基本运算
        self.assertEqual(calc("3+4"), 7)
        self.assertEqual(calc("3-1"), 2)
        self.assertEqual(calc("5×7"), 35)
        self.assertEqual(calc("6÷2"), 3)
        # 测试分数运算
        self.assertEqual(calc("1/2+1/2"), 1)
        self.assertEqual(calc("1/2×2"), 1)
        # 测试带分数
        self.assertEqual(calc("1'1/2"), fractions.Fraction(3, 2))
        # 测试无效表达式
        self.assertIsNone(calc("1/0"))
        self.assertIsNone(calc("1+"))


    def test_format_num(self):
        """测试数字格式化函数"""
        # 测试整数
        self.assertEqual(format_num(5), "5")
        self.assertEqual(format_num(0), "0")
        # 测试真分数
        self.assertEqual(format_num(fractions.Fraction(1, 2)), "1/2")
        # 测试假分数转换为带分数
        self.assertEqual(format_num(fractions.Fraction(5, 2)), "2'1/2")
        # 测试等于1的分数
        self.assertEqual(format_num(fractions.Fraction(2, 2)), "1")


    def test_check_expr(self):
        """测试表达式检查函数"""
        # 测试有效的表达式
        root = exprNode('+', exprNode('1'), exprNode('2'))
        self.assertTrue(check_expr(root))
        self.assertEqual(root.result, "3")
        # 测试无效的表达式（除零）
        root = exprNode('÷', exprNode('1'), exprNode('0'))
        self.assertFalse(check_expr(root))


    def test_make_problem_small(self):
        """测试生成少量题目"""
        problems, answers = make_problem(10, 5)
        self.assertEqual(len(problems), 5)
        self.assertEqual(len(answers), 5)
        # 检查每个问题都有答案
        for i in range(5):
            self.assertTrue(problems[i].endswith("= "))
            self.assertIsNotNone(answers[i])


    def test_make_problem_large(self):
        """测试生成大量题目"""
        problems, answers = make_problem(10, 100)
        self.assertEqual(len(problems), 100)
        self.assertEqual(len(answers), 100)


    def test_check_answers_correct(self):
        """测试批改正确答案"""
        # 创建测试文件
        ex_file = os.path.join(self.temp_dir, "test_ex.txt")
        ans_file = os.path.join(self.temp_dir, "test_ans.txt")
        with open(ex_file, 'w', encoding='utf-8') as f:
            f.write("1. 1 + 1 = \n")
            f.write("2. 2 × 2 = \n")
        with open(ans_file, 'w', encoding='utf-8') as f:
            f.write("1. 2\n")
            f.write("2. 4\n")
        right, wrong = check_answers(ex_file, ans_file)
        self.assertEqual(len(right), 2)
        self.assertEqual(len(wrong), 0)
        self.assertEqual(right, [1, 2])


    def test_check_answers_wrong(self):
        """测试批改错误答案"""
        # 创建测试文件
        ex_file = os.path.join(self.temp_dir, "test_ex.txt")
        ans_file = os.path.join(self.temp_dir, "test_ans.txt")
        with open(ex_file, 'w', encoding='utf-8') as f:
            f.write("1. 1 + 1 = \n")
            f.write("2. 2 × 2 = \n")
        with open(ans_file, 'w', encoding='utf-8') as f:
            f.write("1. 3\n")  # 错误答案
            f.write("2. 5\n")  # 错误答案
        right, wrong = check_answers(ex_file, ans_file)
        self.assertEqual(len(right), 0)
        self.assertEqual(len(wrong), 2)
        self.assertEqual(wrong, [1, 2])


    def test_check_answers_mixed(self):
        """测试批改混合答案"""
        # 创建测试文件
        ex_file = os.path.join(self.temp_dir, "test_ex.txt")
        ans_file = os.path.join(self.temp_dir, "test_ans.txt")
        with open(ex_file, 'w', encoding='utf-8') as f:
            f.write("1. 1 + 1 = \n")
            f.write("2. 2 × 2 = \n")
            f.write("3. 3 - 1 = \n")
        with open(ans_file, 'w', encoding='utf-8') as f:
            f.write("1. 2\n")  # 正确答案
            f.write("2. 5\n")  # 错误答案
            f.write("3. 2\n")  # 正确答案
        right, wrong = check_answers(ex_file, ans_file)
        self.assertEqual(len(right), 2)
        self.assertEqual(len(wrong), 1)
        self.assertEqual(right, [1, 3])
        self.assertEqual(wrong, [2])


    def test_integration(self):
        """测试完整流程"""
        # 生成题目
        problems, answers = make_problem(10, 10)
        # 保存题目和答案
        ex_file = os.path.join(self.temp_dir, "exercises.txt")
        ans_file = os.path.join(self.temp_dir, "answers.txt")
        with open(ex_file, 'w', encoding='utf-8') as f:
            for i, p in enumerate(problems):
                f.write(f"{i + 1}. {p}\n")
        with open(ans_file, 'w', encoding='utf-8') as f:
            for i, a in enumerate(answers):
                f.write(f"{i + 1}. {a}\n")
        # 批改答案
        right, wrong = check_answers(ex_file, ans_file)
        # 所有答案应该都是正确的
        self.assertEqual(len(wrong), 0)
        self.assertEqual(len(right), 10)


class TestCommandLine(unittest.TestCase):

    @patch('sys.argv', ['calculator.py', '-n', '10', '-r', '10'])
    def test_generate_mode(self):
        # 测试生成模式
        # 由于main函数会使用sys.argv，我们通过patch模拟命令行参数
        # 这里我们检查是否成功解析了参数，并且进入了生成模式
        args = calculator.parser.parse_args()
        self.assertEqual(args.n, 10)
        self.assertEqual(args.r, 10)
        self.assertIsNone(args.e)
        self.assertIsNone(args.a)

    @patch('sys.argv', ['calculator.py', '-e', 'exercises.txt', '-a', 'answers.txt'])
    def test_grade_mode(self):
        # 测试批改模式
        args = calculator.parser.parse_args()
        self.assertIsNone(args.n)
        self.assertIsNone(args.r)
        self.assertEqual(args.e, 'exercises.txt')
        self.assertEqual(args.a, 'answers.txt')


if __name__ == '__main__':
    unittest.main(verbosity=2)