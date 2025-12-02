"""
项目1: 计算器

功能:
- 基本四则运算（加、减、乘、除）
- 高级运算（幂运算、平方根、百分比）
- 错误处理
- 历史记录
"""

import math


class Calculator:
    """计算器类"""
    
    def __init__(self):
        """初始化计算器"""
        self.history = []  # 历史记录
    
    def add(self, a, b):
        """加法"""
        result = a + b
        self._add_to_history(f"{a} + {b} = {result}")
        return result
    
    def subtract(self, a, b):
        """减法"""
        result = a - b
        self._add_to_history(f"{a} - {b} = {result}")
        return result
    
    def multiply(self, a, b):
        """乘法"""
        result = a * b
        self._add_to_history(f"{a} × {b} = {result}")
        return result
    
    def divide(self, a, b):
        """除法"""
        if b == 0:
            raise ValueError("除数不能为零")
        result = a / b
        self._add_to_history(f"{a} ÷ {b} = {result}")
        return result
    
    def power(self, base, exponent):
        """幂运算"""
        result = base ** exponent
        self._add_to_history(f"{base} ^ {exponent} = {result}")
        return result
    
    def square_root(self, number):
        """平方根"""
        if number < 0:
            raise ValueError("不能计算负数的平方根")
        result = math.sqrt(number)
        self._add_to_history(f"√{number} = {result}")
        return result
    
    def percentage(self, number, percent):
        """百分比计算"""
        result = number * (percent / 100)
        self._add_to_history(f"{number} 的 {percent}% = {result}")
        return result
    
    def _add_to_history(self, record):
        """添加到历史记录"""
        self.history.append(record)
    
    def show_history(self):
        """显示历史记录"""
        if not self.history:
            print("暂无历史记录")
            return
        
        print("\n" + "=" * 40)
        print("历史记录:")
        print("=" * 40)
        for i, record in enumerate(self.history, 1):
            print(f"{i}. {record}")
        print("=" * 40)
    
    def clear_history(self):
        """清空历史记录"""
        self.history = []
        print("历史记录已清空")


def get_number(prompt):
    """获取用户输入的数字"""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("错误: 请输入有效的数字")


def print_menu():
    """打印菜单"""
    print("\n" + "=" * 40)
    print("计算器菜单")
    print("=" * 40)
    print("1. 加法 (+)")
    print("2. 减法 (-)")
    print("3. 乘法 (×)")
    print("4. 除法 (÷)")
    print("5. 幂运算 (^)")
    print("6. 平方根 (√)")
    print("7. 百分比 (%)")
    print("8. 查看历史记录")
    print("9. 清空历史记录")
    print("0. 退出")
    print("=" * 40)


def main():
    """主函数"""
    calc = Calculator()
    
    print("欢迎使用计算器！")
    
    while True:
        print_menu()
        choice = input("请选择操作 (0-9): ").strip()
        
        try:
            if choice == '0':
                print("感谢使用，再见！")
                break
            
            elif choice == '1':
                # 加法
                a = get_number("请输入第一个数: ")
                b = get_number("请输入第二个数: ")
                result = calc.add(a, b)
                print(f"结果: {a} + {b} = {result}")
            
            elif choice == '2':
                # 减法
                a = get_number("请输入被减数: ")
                b = get_number("请输入减数: ")
                result = calc.subtract(a, b)
                print(f"结果: {a} - {b} = {result}")
            
            elif choice == '3':
                # 乘法
                a = get_number("请输入第一个数: ")
                b = get_number("请输入第二个数: ")
                result = calc.multiply(a, b)
                print(f"结果: {a} × {b} = {result}")
            
            elif choice == '4':
                # 除法
                a = get_number("请输入被除数: ")
                b = get_number("请输入除数: ")
                result = calc.divide(a, b)
                print(f"结果: {a} ÷ {b} = {result}")
            
            elif choice == '5':
                # 幂运算
                base = get_number("请输入底数: ")
                exponent = get_number("请输入指数: ")
                result = calc.power(base, exponent)
                print(f"结果: {base} ^ {exponent} = {result}")
            
            elif choice == '6':
                # 平方根
                number = get_number("请输入数字: ")
                result = calc.square_root(number)
                print(f"结果: √{number} = {result}")
            
            elif choice == '7':
                # 百分比
                number = get_number("请输入数字: ")
                percent = get_number("请输入百分比: ")
                result = calc.percentage(number, percent)
                print(f"结果: {number} 的 {percent}% = {result}")
            
            elif choice == '8':
                # 查看历史记录
                calc.show_history()
            
            elif choice == '9':
                # 清空历史记录
                calc.clear_history()
            
            else:
                print("错误: 无效的选择，请输入 0-9")
        
        except ValueError as e:
            print(f"错误: {e}")
        except Exception as e:
            print(f"发生错误: {e}")


if __name__ == '__main__':
    main()
