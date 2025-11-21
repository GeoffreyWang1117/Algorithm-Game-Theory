"""
练习运行器和验证系统
"""

import ast
import importlib.util
import re
import sys
import traceback
from pathlib import Path


class Color:
    """终端颜色"""
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'


class ExerciseRunner:
    """练习运行器"""

    def __init__(self):
        self.test_results = []

    def run(self, exercise_path):
        """运行练习并验证"""
        exercise_path = Path(exercise_path)

        if not exercise_path.exists():
            print(f"{Color.RED}错误: 找不到文件 {exercise_path}{Color.END}")
            return False

        # 读取练习文件内容
        with open(exercise_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 检查是否还有 TODO
        if self._has_todo(content):
            print(f"{Color.YELLOW}⚠ 提示: 代码中还有 TODO 标记，请完成所有 TODO{Color.END}\n")
            self._show_todos(content)
            return False

        # 打印练习描述
        self._print_description(content)

        # 动态加载模块
        try:
            spec = importlib.util.spec_from_file_location("exercise_module", exercise_path)
            module = importlib.util.module_from_spec(spec)
            sys.modules["exercise_module"] = module
            spec.loader.exec_module(module)
        except Exception as e:
            print(f"{Color.RED}✗ 运行错误:{Color.END}")
            print(f"{Color.RED}{traceback.format_exc()}{Color.END}")
            return False

        # 运行测试
        if hasattr(module, 'test'):
            print(f"\n{Color.CYAN}运行测试...{Color.END}\n")
            try:
                result = module.test()
                if result:
                    print(f"{Color.GREEN}✓ 所有测试通过！{Color.END}")
                    return True
                else:
                    print(f"{Color.RED}✗ 测试失败{Color.END}")
                    return False
            except AssertionError as e:
                print(f"{Color.RED}✗ 断言失败: {str(e)}{Color.END}")
                return False
            except Exception as e:
                print(f"{Color.RED}✗ 测试错误:{Color.END}")
                print(f"{Color.RED}{traceback.format_exc()}{Color.END}")
                return False
        else:
            print(f"{Color.YELLOW}⚠ 警告: 未找到 test() 函数{Color.END}")
            return False

    def _has_todo(self, content):
        """检查是否还有 TODO"""
        # 匹配 TODO, todo, 或 # TODO: 等形式
        todo_pattern = re.compile(r'#\s*TODO|#\s*todo|pass\s*#.*TODO', re.IGNORECASE)
        return bool(todo_pattern.search(content))

    def _show_todos(self, content):
        """显示所有 TODO 位置"""
        lines = content.split('\n')
        print(f"{Color.YELLOW}待完成的 TODO:{Color.END}\n")
        for i, line in enumerate(lines, 1):
            if 'TODO' in line or 'todo' in line:
                print(f"  第 {i} 行: {line.strip()}")
        print()

    def _print_description(self, content):
        """打印练习描述（从文档字符串中提取）"""
        try:
            tree = ast.parse(content)
            docstring = ast.get_docstring(tree)
            if docstring:
                print(f"{Color.CYAN}{Color.BOLD}练习说明:{Color.END}")
                print(f"{Color.CYAN}{docstring}{Color.END}\n")
        except:
            pass

    def show_hint(self, exercise_path):
        """显示练习提示"""
        exercise_path = Path(exercise_path)

        if not exercise_path.exists():
            print(f"{Color.RED}错误: 找不到文件 {exercise_path}{Color.END}")
            return

        with open(exercise_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 查找 HINT 注释
        hint_pattern = re.compile(r'#\s*HINT:\s*(.+?)(?=#\s*HINT:|$)', re.DOTALL | re.IGNORECASE)
        hints = hint_pattern.findall(content)

        if hints:
            print(f"\n{Color.YELLOW}{Color.BOLD}💡 提示:{Color.END}\n")
            for hint in hints:
                print(f"{Color.YELLOW}{hint.strip()}{Color.END}\n")
        else:
            print(f"{Color.YELLOW}此练习没有提供额外提示{Color.END}")


def validate_function(func, test_cases, function_name="function"):
    """
    验证函数的测试用例

    Args:
        func: 要测试的函数
        test_cases: 测试用例列表，每个元素是 (input_args, expected_output) 或 (input_args, expected_output, description)
        function_name: 函数名称（用于显示）

    Returns:
        bool: 所有测试是否通过
    """
    all_passed = True

    for i, test_case in enumerate(test_cases, 1):
        if len(test_case) == 2:
            inputs, expected = test_case
            description = None
        else:
            inputs, expected, description = test_case

        try:
            # 支持单个参数和多个参数
            if isinstance(inputs, tuple):
                result = func(*inputs)
            else:
                result = func(inputs)

            # 比较结果
            if callable(expected):
                # 如果 expected 是一个函数，用它来验证结果
                passed = expected(result)
            else:
                passed = result == expected or (
                    hasattr(result, '__iter__') and hasattr(expected, '__iter__') and
                    list(result) == list(expected)
                )

            if passed:
                status = f"{Color.GREEN}✓{Color.END}"
            else:
                status = f"{Color.RED}✗{Color.END}"
                all_passed = False

            desc = f" - {description}" if description else ""
            print(f"  测试 {i}: {status}{desc}")

            if not passed:
                print(f"    输入: {inputs}")
                print(f"    期望: {expected}")
                print(f"    实际: {result}")

        except Exception as e:
            print(f"  测试 {i}: {Color.RED}✗{Color.END} - 运行错误")
            print(f"    {Color.RED}{str(e)}{Color.END}")
            all_passed = False

    return all_passed
