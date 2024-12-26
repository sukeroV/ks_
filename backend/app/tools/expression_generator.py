import random
from typing import List, Dict, Tuple, Set
import logging

logger = logging.getLogger(__name__)

class ExpressionGenerator:
    """算术表达式生成器"""
    
    def __init__(self, selected_operators: List[str], operator_count: int, min_number: int, max_number: int):
        self.operator_map = {'+': '+', '-': '-', '×': '*', '÷': '/'}
        self.operators = [self.operator_map[op] for op in selected_operators]
        self.max_operators = operator_count
        self.min_number = min_number
        self.max_number = max_number
        self.used_expressions: Set[str] = set()

    def generate_expressions(self, count: int, bracket_count: int) -> List[Dict]:
        """生成指定数量的表达式"""
        if len(self.operators) == 1:
            if self.operators[0] == '*':
                return self._generate_multiplication_expressions(count)
            elif self.operators[0] == '+':
                return self._generate_addition_expressions(count)
            elif self.operators[0] == '-':
                return self._generate_subtraction_expressions(count)
            elif self.operators[0] == '/':
                return self._generate_division_expressions(count)
        
        return self._generate_mixed_expressions(count, bracket_count)

    def _generate_multiplication_expressions(self, count: int) -> List[Dict]:
        """生成乘法表达式"""
        possible_combinations = []
        for num1 in range(2, self.max_number + 1):  # 从2开始，避免1
            for num2 in range(2, self.max_number + 1):  # 从2开始，避免1
                if num1 != 1 and num2 != 1:  # 确保两个数都不是1
                    possible_combinations.append((num1, num2))
        
        if len(possible_combinations) < count:
            raise ValueError(
                f"Cannot generate {count} unique multiplication expressions without using 1.\n"
                f"Numbers range: {self.min_number} to {self.max_number}"
            )
        
        return self._generate_expressions_from_combinations(possible_combinations, count, '×', lambda x, y: x * y)

    def _generate_addition_expressions(self, count: int) -> List[Dict]:
        """生成加法表达式"""
        possible_combinations = []
        for num1 in range(self.min_number, self.max_number + 1):
            for num2 in range(self.min_number, self.max_number + 1):
                possible_combinations.append((num1, num2))
        
        return self._generate_expressions_from_combinations(possible_combinations, count, '+', lambda x, y: x + y)
# yyy
    def _generate_subtraction_expressions(self, count: int) -> List[Dict]:
        """生成减法表达式"""
        possible_combinations = []
        for num1 in range(self.min_number, self.max_number + 1):
            for num2 in range(self.min_number, self.max_number + 1):
                # 避免相同数字相减
                if num1 != num2:
                    possible_combinations.append((num1, num2))
        
        return self._generate_expressions_from_combinations(possible_combinations, count, '-', lambda x, y: x - y)

    def _generate_division_expressions(self, count: int) -> List[Dict]:
        """生成除法表达式"""
        possible_combinations = []
        for num1 in range(self.min_number, self.max_number + 1):
            for num2 in range(2, min(11, self.max_number + 1)):  # 除数从2开始，最大到10
                # 确保能整除，且除数不等于被除数
                if num1 % num2 == 0 and num1 != num2:
                    possible_combinations.append((num1, num2))
        
        return self._generate_expressions_from_combinations(possible_combinations, count, '÷', lambda x, y: x / y)

    def _generate_expressions_from_combinations(self, combinations: List[Tuple[int, int]], 
                                             count: int, operator: str, 
                                             operation: callable) -> List[Dict]:
        """从可能的组合中生成表达式"""
        logger.info(f"Found {len(combinations)} possible combinations for {operator}")
        
        if len(combinations) < count:
            raise ValueError(
                f"Cannot generate {count} unique {operator} expressions.\n"
                f"Numbers range: {self.min_number} to {self.max_number}\n"
                f"Found combinations: {len(combinations)}"
            )
        
        # 随机选择组合并生成表达式
        expressions = []
        selected_combinations = random.sample(combinations, count)
        
        for num1, num2 in selected_combinations:
            expr = f"{num1} {operator} {num2}"
            ans = operation(num1, num2)
            expressions.append({
                "expression_text": expr,
                "answer": ans,
                "has_brackets": False,
                "operator_count": 1
            })
            logger.info(f"Generated: {expr} = {ans}")
        
        return expressions

    def _is_bracket_meaningful(self, operators: List[str], numbers: List[int], start: int, end: int) -> bool:
        """判断括号是否有意义（是否会改变计算结果且结果有意义）"""
        # 计算括号内的结果
        def calculate_bracket_value(nums: List[int], ops: List[str]) -> float:
            if len(nums) == 1:
                return nums[0]
            result = nums[0]
            for i in range(len(ops)):
                if ops[i] == '+':
                    result += nums[i + 1]
                elif ops[i] == '-':
                    result -= nums[i + 1]
                elif ops[i] == '*':
                    result *= nums[i + 1]
                elif ops[i] == '/':
                    if nums[i + 1] == 0:
                        raise ValueError("Division by zero")
                    result /= nums[i + 1]
            return result
        
        try:
            # 计算括号内的结果
            bracket_nums = numbers[start:end + 1]
            bracket_ops = operators[start:end]
            bracket_result = calculate_bracket_value(bracket_nums, bracket_ops)
            
            # 检查括号内的结果是否为0、1或-1
            if abs(bracket_result) < 0.001 or abs(abs(bracket_result) - 1) < 0.001:
                return False
            
            # 构建带括号和不带括号的表达式
            with_bracket = []
            without_bracket = []
            
            # 构建两个表达式用于比较结果
            for i in range(len(operators)):
                if i == start:
                    with_bracket.append('(')
                with_bracket.append(str(numbers[i]))
                with_bracket.append(operators[i])
                without_bracket.append(str(numbers[i]))
                without_bracket.append(operators[i])
                if i == end:
                    with_bracket.append(')')
            
            with_bracket.append(str(numbers[-1]))
            without_bracket.append(str(numbers[-1]))
            
            # 计算两个表达式的结果
            expr1 = ' '.join(with_bracket)
            expr2 = ' '.join(without_bracket)
            
            result1 = eval(expr1)
            result2 = eval(expr2)
            
            # 如果结果不同，且括号内的结果不是0、1或-1，则括号有意义
            return result1 != result2
            
        except Exception as e:
            logger.error(f"Error evaluating expressions: {e}")
            return False

    def _find_valid_bracket_positions(self, operators: List[str], numbers: List[int]) -> List[Tuple[int, int]]:
        """找出所有有意义的括号位置"""
        valid_positions = []
        operator_count = len(operators)
        
        # 对于两个运算符的情况
        if operator_count == 2:
            # 只检查第一个运算符是加减，第二个是乘除的情况
            if (operators[0] in ['+', '-'] and operators[1] in ['*', '/']):
                if self._is_bracket_meaningful(operators, numbers, 0, 1):
                    valid_positions.append((0, 1))
        
        # 对于三个运算符的情况
        else:
            for start in range(operator_count):
                for end in range(start + 1, operator_count):
                    if self._is_bracket_meaningful(operators, numbers, start, end):
                        valid_positions.append((start, end))
        
        return valid_positions

    def _is_meaningful_operation(self, operator: str, number: int, prev_number: int = None, next_operator: str = None) -> bool:
        """判断运算是否有意义
        operator: 当前运算符
        number: 当前数字
        prev_number: 前一个数字
        next_operator: 下一个运算符（如果有）
        """
        if operator == '-':
            # 避免相同数字相减
            if prev_number == number:
                return False
            # 避免 "a + b - b" 或 "a × b - b" 这样的模式
            if next_operator is None and prev_number is not None:
                return number != prev_number
        elif operator in ['*', '/']:
            if operator == '/':
                # 除法特殊处理：不能是1，不能和被除数相同
                return number not in [0, 1] and (prev_number is None or number != prev_number)
            return number not in [0, 1]  # 乘法：不能是0和1
        return True

    def _generate_mixed_expressions(self, count: int, bracket_count: int) -> List[Dict]:
        """生成混合运算表达式"""
        expressions = []
        bracket_expressions = 0
        max_attempts = count * 20
        attempts = 0
        
        # 先生成需要括号的表达式
        while bracket_expressions < bracket_count and attempts < max_attempts:
            # 确保至少有2个运算符
            operator_count = 2
            
            # ��保有加减和乘除的组合
            mul_div = [op for op in self.operators if op in ['*', '/']]
            add_sub = [op for op in self.operators if op in ['+', '-']]
            
            if not (mul_div and add_sub):
                raise ValueError("Need both multiplication/division and addition/subtraction operators for brackets")
            
            # 强制使用"加减-乘除"的顺序
            selected_operators = [random.choice(add_sub), random.choice(mul_div)]
            
            # 生成数字
            numbers = []
            valid_numbers = True
            
            for i in range(3):  # 需要3个数字
                attempts_for_number = 0  # 移到循环内部
                while attempts_for_number < 10:
                    num = random.randint(self.min_number, self.max_number)
                    
                    # 检查当前数字是否有效
                    is_valid = True
                    
                    # 获取下一个运算符（如果有）
                    next_op = selected_operators[i] if i < len(selected_operators) else None
                    
                    # 检查当前数字作为前一个运算的结果
                    if i > 0:
                        prev_num = numbers[-1]  # 获取前一个数字
                        if not self._is_meaningful_operation(selected_operators[i-1], num, prev_num, next_op):
                            is_valid = False
                    
                    # 检查当前数字作为下一个运算的开始
                    if i < len(selected_operators) and selected_operators[i] in ['*', '/'] and num == 1:
                        is_valid = False
                    
                    # 如果是除法，确保能整除且不为1，且不等于被除数
                    if i > 0 and selected_operators[i-1] == '/':
                        divisors = [n for n in range(2, min(11, self.max_number + 1))
                                  if numbers[-1] % n == 0 and n != 1 and n != numbers[-1]]
                        if not divisors:
                            is_valid = False
                        elif is_valid:
                            num = random.choice(divisors)
                    
                    if is_valid:
                        numbers.append(num)
                        break
                    
                    attempts_for_number += 1
                
                if attempts_for_number >= 10:
                    valid_numbers = False
                    break
            
            if not valid_numbers:
                attempts += 1
                continue
            
            # 构建带括号的表达式
            expression_parts = ['(', str(numbers[0]), 
                              selected_operators[0].replace('*', '×').replace('/', '÷'),
                              str(numbers[1]), ')', 
                              selected_operators[1].replace('*', '×').replace('/', '÷'),
                              str(numbers[2])]
            
            expr_text = ' '.join(expression_parts)
            
            try:
                calc_expr = expr_text.replace('×', '*').replace('÷', '/')
                result = eval(calc_expr)
                
                if isinstance(result, (int, float)) and str(expr_text) not in self.used_expressions:
                    self.used_expressions.add(str(expr_text))
                    expressions.append({
                        "expression_text": expr_text,
                        "answer": result,
                        "has_brackets": True,
                        "operator_count": operator_count
                    })
                    bracket_expressions += 1
                    logger.info(f"Generated bracketed expression: {expr_text} = {result}")
                    continue
            except Exception as e:
                logger.error(f"Error generating bracketed expression: {e}")
            
            attempts += 1
        
        # 然后生成剩余的不带括号的表达式
        remaining_count = count - len(expressions)
        if remaining_count > 0:
            while len(expressions) < count and attempts < max_attempts:
                operator_count = random.randint(1, self.max_operators)
                selected_operators = random.sample(self.operators, operator_count)
                
                # 生成有意义的数字
                numbers = []
                valid_numbers = True
                
                for i in range(operator_count + 1):
                    attempts_for_number = 0
                    while attempts_for_number < 10:  # 限制每个数字的尝试次数
                        num = random.randint(self.min_number, self.max_number)
                        
                        # 检查当前数字是否有效
                        is_valid = True
                        
                        # 获取下一个运算符（如果有）
                        next_op = selected_operators[i] if i < operator_count else None
                        
                        # 检查当前数字作为前一个运算的结果
                        if i > 0:
                            prev_num = numbers[-1]  # 获取前一个数字
                            if not self._is_meaningful_operation(selected_operators[i-1], num, prev_num, next_op):
                                is_valid = False
                            
                            # 检查是否形成了 "a + b - b" 或 "a × b - b" 的模式
                            if i >= 2 and selected_operators[i-1] == '-':
                                if num == numbers[-1]:  # 如果当前数字等于前一个数字
                                    is_valid = False
                        
                        # 检查当前数字作为下一个运算的开始
                        if i < operator_count and selected_operators[i] in ['*', '/'] and num == 1:
                            is_valid = False
                        
                        # 如果是除法，确保能整除且不为1，且不等于被除数
                        if i > 0 and selected_operators[i-1] == '/':
                            divisors = [n for n in range(2, min(11, self.max_number + 1))
                                      if numbers[-1] % n == 0 and n != 1 and n != numbers[-1]]
                            if not divisors:
                                is_valid = False
                            elif is_valid:
                                num = random.choice(divisors)
                        
                        if is_valid:
                            numbers.append(num)
                            break
                        
                        attempts_for_number += 1
                    
                    if len(numbers) != i + 1:
                        valid_numbers = False
                        break
                
                if not valid_numbers:
                    attempts += 1
                    continue
                
                # 构建表达式
                expression_parts = []
                for i in range(operator_count):
                    expression_parts.append(str(numbers[i]))
                    expression_parts.append(selected_operators[i].replace('*', '×').replace('/', '÷'))
                expression_parts.append(str(numbers[-1]))
                
                expr_text = ' '.join(expression_parts)
                
                try:
                    calc_expr = expr_text.replace('×', '*').replace('÷', '/')
                    result = eval(calc_expr)
                    
                    if isinstance(result, (int, float)) and str(expr_text) not in self.used_expressions:
                        self.used_expressions.add(str(expr_text))
                        expressions.append({
                            "expression_text": expr_text,
                            "answer": result,
                            "has_brackets": False,
                            "operator_count": operator_count
                        })
                        logger.info(f"Generated expression without brackets: {expr_text} = {result}")
                except Exception as e:
                    logger.error(f"Error generating expression without brackets: {e}")
                
                attempts += 1
        
        if bracket_expressions < bracket_count:
            raise ValueError(f"Could not generate {bracket_count} expressions with brackets after {max_attempts} attempts")
        
        return expressions

if __name__ == "__main__":
    generator = ExpressionGenerator(['+', '-', '×', '÷'], 3, 1, 100)
    expressions = generator.generate_expressions(5, 3)
    print(expressions) 