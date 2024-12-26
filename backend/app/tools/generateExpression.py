import random
import re
from fractions import Fraction

def parse_expression(expression):
    """解析表达式，返回操作数列表和运算符列表"""
    numbers = [float(num) if '.' in num else int(num) for num in re.findall(r'[\d.]+', expression)]
    operators = re.findall(r'[+\-*/]', expression)
    return numbers, operators

def generate_random_integer(max_digits):
    """生成一个指定位数的随机整数"""
    min_val = 10 ** (max_digits - 1)
    max_val = 10 ** max_digits - 1
    return random.randint(min_val, max_val)

def generate_random_fraction(max_digits):
    """生成一个简单的分数，分子和分母的位数不超过 max_digits"""
    numerator = generate_random_integer(max_digits - 1)
    denominator = generate_random_integer(max_digits)
    while denominator <= numerator:  # 确保分母大于分子
        denominator = generate_random_integer(max_digits)
    return f"{numerator}/{denominator}"

def generate_random_decimal_in_range(min_value, max_value, max_digits):
    """生成一个指定范围内的小数，且小数位数与最大位数相符"""
    max_value = round(max_value, 2)
    min_value = round(min_value, 2)
    decimal_places = 2
    max_value = min(max_value, 10 ** max_digits - 0.01)
    return round(random.uniform(min_value, max_value), decimal_places)

def ensure_operators_used(original_operators, new_operators):
    """确保所有原始运算符至少使用一次"""
    operator_set = set(original_operators)
    for op in operator_set:
        if op not in new_operators:
            index = random.randint(0, len(new_operators) - 1)
            new_operators[index] = op
    return new_operators

def randomly_add_parentheses(expression_parts, operators):
    """
    在包含至少一个乘除和一个加减运算符，且至少有三个操作数的表达式中随机添加括号。
    :param expression_parts: 表达式分割后的数字和运算符列表
    :param operators: 原始运算符列表
    :return: 带括号的新表达式
    """
    # 确保存在加减和乘除操作符
    if len(operators) < 1 or not (any(op in "+-" for op in operators) and any(op in "*/" for op in operators)):
        return ''.join(expression_parts)

    # 寻找符合条件的位置来加括号（仅限加减法加括号）
    add_sub_indices = [i for i, op in enumerate(operators) if op in "+-"]

    # 选取一个加减运算符的索引来加括号
    if not add_sub_indices:
        return ''.join(expression_parts)

    # 随机选取一个加减操作的位置
    add_idx = random.choice(add_sub_indices)

    # 确保括号内只有两个操作数
    left_start = add_idx * 2
    right_end = add_idx * 2 + 2
    expression_parts[left_start] = f"({expression_parts[left_start]}"
    expression_parts[right_end] = f"{expression_parts[right_end]})"

    return ''.join(expression_parts)

def generate_new_expression(numbers, operators):
    """
    根据原始表达式的结构生成新的表达式，并随机添加括号。
    :param numbers: 原始表达式中的数字列表
    :param operators: 原始表达式中的运算符列表
    :return: 新生成的表达式字符串
    """
    max_digits = max(len(str(abs(int(num)))) for num in numbers if isinstance(num, (int, float)))
    new_numbers = []

    for num in numbers:
        if isinstance(num, float):
            new_numbers.append(str(generate_random_decimal_in_range(0.1, 9999.99, max_digits)))
        elif isinstance(num, int):
            new_numbers.append(str(generate_random_integer(max_digits)))
        elif isinstance(num, str) and '/' in num:
            new_numbers.append(str(generate_random_fraction(max_digits)))
        else:
            raise ValueError("未识别的数字类型")

    new_operators = [random.choice(operators) for _ in operators]
    new_operators = ensure_operators_used(operators, new_operators)

    expression_parts = []
    for i in range(len(new_operators)):
        expression_parts.append(new_numbers[i])
        expression_parts.append(new_operators[i])
    expression_parts.append(new_numbers[-1])

    new_expression = randomly_add_parentheses(expression_parts, new_operators)
    return new_expression

def evaluate_expression(expression):
    """计算表达式的值，支持分数和小数"""
    expression = expression.replace('×', '*').replace('÷', '/')
    try:
        expression = re.sub(r'(\d+)/(\d+)', lambda x: str(Fraction(int(x.group(1)), int(x.group(2)))), expression)
        result = eval(expression)
        return result
    except Exception as e:
        print(f"表达式计算错误: {e}")
        return None

def GenerateExpressionAndAnswer(expr):
    """根据示例表达式生成新的表达式并计算答案"""
    expr = expr.replace('×', '*').replace('÷', '/')
    result = evaluate_expression(expr)
    numbers, operators = parse_expression(expr)
    new_expression = generate_new_expression(numbers, operators)
    new_result = evaluate_expression(new_expression)
    return expr, result, new_expression, new_result

# 示例调用
examples = [
    "6 + 4",
    "-6 + 4",
    "5 - 2",
    "123 + 45",
    "156 - 34",
    "12 * 3",
    "24 / 3",
    "12 + 3 * 4",
    "1/2 + 1/4",
    "12345 + 6789",
    "15678 - 3456",
    "123 * 45",
    "1234 / 12",
    "12 + 3 * 4 - 5 / 2",
    "1/2 + 1/3",
    "0.5 + 0.25",
    "1.2 + 0.1",
    "12.75 + 3.25",
]

# results = {}
# for example in examples:
#     original_expr, original_result, new_expr, new_result = GenerateExpressionAndAnswer(example)
#     results[original_expr] = (original_result, new_expr, new_result)
#     print(f"原始表达式: {original_expr}")
#     print(f"原始答案: {original_result}")
#     print(f"新生成的表达式: {new_expr}")
#     print(f"新生成的答案: {new_result}")
#     print()
#
# print("结果字典:")
# for expr, (original_result, new_expr, new_result) in results.items():
#     print(f"{expr} = {original_result} -> {new_expr} = {new_result}")


def get_expression(original_expression="",number_of_questions=10):
    if original_expression == "":
        return False
    number_of_questions = int(number_of_questions)
    results = []

    for _ in range(number_of_questions):
        original_expr, original_result, new_expr, new_result = GenerateExpressionAndAnswer(original_expression)

        new_expr = new_expr + ' = '

        expr = new_expr.replace('*', ' × ').replace('/', ' ÷ ').replace('+',' + ').replace('-',' - ') # 转换表达式
        results.append([expr, round(new_result, 2)])
        # print(f"原始表达式: {original_expr}")
        # print(f"原始答案: {original_result}")
        # print(f"新生成的表达式: {new_expr}")
        # print(f"新生成的答案: {new_result}")
        # print()

    return results

