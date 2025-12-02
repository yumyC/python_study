"""
Python 基础教程 04: 类和对象

本教程涵盖:
- 类的定义和实例化
- 属性和方法
- 构造函数和析构函数
- 继承
- 多态
- 封装
- 特殊方法（魔术方法）
"""

# ============================================================
# 1. 类的定义和实例化
# ============================================================

print("=" * 50)
print("类的定义和实例化:")
print("=" * 50)

# 定义一个简单的类
class Dog:
    """狗类"""
    
    def __init__(self, name, age):
        """构造函数"""
        self.name = name  # 实例属性
        self.age = age
    
    def bark(self):
        """狗叫方法"""
        print(f"{self.name} 说: 汪汪!")
    
    def get_info(self):
        """获取狗的信息"""
        return f"{self.name} 今年 {self.age} 岁"

# 创建实例（对象）
dog1 = Dog("旺财", 3)
dog2 = Dog("小黑", 5)

# 调用方法
dog1.bark()
dog2.bark()

# 访问属性
print(dog1.get_info())
print(dog2.get_info())

# ============================================================
# 2. 类属性和实例属性
# ============================================================

print("\n" + "=" * 50)
print("类属性和实例属性:")
print("=" * 50)

class Cat:
    """猫类"""
    
    # 类属性（所有实例共享）
    species = "猫科动物"
    count = 0
    
    def __init__(self, name, color):
        """构造函数"""
        # 实例属性（每个实例独有）
        self.name = name
        self.color = color
        Cat.count += 1  # 修改类属性
    
    def get_info(self):
        """获取猫的信息"""
        return f"{self.name} 是 {self.color} 色的{Cat.species}"

# 创建实例
cat1 = Cat("咪咪", "白")
cat2 = Cat("花花", "黑")

print(cat1.get_info())
print(cat2.get_info())
print(f"创建了 {Cat.count} 只猫")

# ============================================================
# 3. 方法类型
# ============================================================

print("\n" + "=" * 50)
print("方法类型:")
print("=" * 50)

class MyClass:
    """演示不同类型的方法"""
    
    class_variable = "类变量"
    
    def __init__(self, value):
        self.instance_variable = value
    
    # 实例方法（最常用）
    def instance_method(self):
        """实例方法，可以访问实例属性和类属性"""
        return f"实例方法: {self.instance_variable}, {MyClass.class_variable}"
    
    # 类方法
    @classmethod
    def class_method(cls):
        """类方法，只能访问类属性"""
        return f"类方法: {cls.class_variable}"
    
    # 静态方法
    @staticmethod
    def static_method():
        """静态方法，不能访问实例或类属性"""
        return "静态方法: 独立的工具函数"

# 使用不同类型的方法
obj = MyClass("实例值")
print(obj.instance_method())
print(MyClass.class_method())
print(MyClass.static_method())

# ============================================================
# 4. 继承
# ============================================================

print("\n" + "=" * 50)
print("继承:")
print("=" * 50)

# 父类（基类）
class Animal:
    """动物基类"""
    
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def speak(self):
        """动物叫声（将被子类重写）"""
        print(f"{self.name} 发出声音")
    
    def get_info(self):
        """获取动物信息"""
        return f"{self.name}, {self.age}岁"

# 子类继承父类
class Dog(Animal):
    """狗类，继承自 Animal"""
    
    def __init__(self, name, age, breed):
        # 调用父类构造函数
        super().__init__(name, age)
        self.breed = breed
    
    # 重写父类方法
    def speak(self):
        print(f"{self.name} 说: 汪汪!")
    
    # 新增方法
    def fetch(self):
        print(f"{self.name} 去捡球")

class Cat(Animal):
    """猫类，继承自 Animal"""
    
    def speak(self):
        print(f"{self.name} 说: 喵喵!")
    
    def climb(self):
        print(f"{self.name} 爬树")

# 使用继承
dog = Dog("旺财", 3, "金毛")
cat = Cat("咪咪", 2)

print(dog.get_info())
dog.speak()
dog.fetch()

print(cat.get_info())
cat.speak()
cat.climb()

# ============================================================
# 5. 多态
# ============================================================

print("\n" + "=" * 50)
print("多态:")
print("=" * 50)

# 多态：不同类的对象可以使用相同的接口
def make_animal_speak(animal):
    """让动物发声"""
    animal.speak()

animals = [
    Dog("旺财", 3, "金毛"),
    Cat("咪咪", 2),
    Dog("小黑", 5, "哈士奇")
]

print("所有动物发声:")
for animal in animals:
    make_animal_speak(animal)

# ============================================================
# 6. 封装
# ============================================================

print("\n" + "=" * 50)
print("封装:")
print("=" * 50)

class BankAccount:
    """银行账户类，演示封装"""
    
    def __init__(self, owner, balance=0):
        self.owner = owner
        self.__balance = balance  # 私有属性（名称改写）
    
    def deposit(self, amount):
        """存款"""
        if amount > 0:
            self.__balance += amount
            print(f"存入 {amount} 元，余额: {self.__balance} 元")
        else:
            print("存款金额必须大于0")
    
    def withdraw(self, amount):
        """取款"""
        if 0 < amount <= self.__balance:
            self.__balance -= amount
            print(f"取出 {amount} 元，余额: {self.__balance} 元")
        else:
            print("余额不足或金额无效")
    
    def get_balance(self):
        """获取余额"""
        return self.__balance
    
    # 使用 property 装饰器
    @property
    def balance(self):
        """余额属性（只读）"""
        return self.__balance

# 使用封装
account = BankAccount("张三", 1000)
account.deposit(500)
account.withdraw(300)
print(f"当前余额: {account.get_balance()} 元")
print(f"使用 property: {account.balance} 元")

# 无法直接访问私有属性
# print(account.__balance)  # 会报错

# ============================================================
# 7. 特殊方法（魔术方法）
# ============================================================

print("\n" + "=" * 50)
print("特殊方法:")
print("=" * 50)

class Book:
    """书籍类，演示特殊方法"""
    
    def __init__(self, title, author, pages):
        self.title = title
        self.author = author
        self.pages = pages
    
    def __str__(self):
        """字符串表示（用于 print）"""
        return f"《{self.title}》 by {self.author}"
    
    def __repr__(self):
        """官方字符串表示（用于调试）"""
        return f"Book('{self.title}', '{self.author}', {self.pages})"
    
    def __len__(self):
        """返回页数"""
        return self.pages
    
    def __eq__(self, other):
        """相等比较"""
        return self.title == other.title and self.author == other.author
    
    def __lt__(self, other):
        """小于比较（按页数）"""
        return self.pages < other.pages
    
    def __add__(self, other):
        """加法运算（合并页数）"""
        return self.pages + other.pages

# 使用特殊方法
book1 = Book("Python 编程", "张三", 300)
book2 = Book("数据结构", "李四", 250)
book3 = Book("Python 编程", "张三", 300)

print(f"__str__: {book1}")
print(f"__repr__: {repr(book1)}")
print(f"__len__: {len(book1)} 页")
print(f"__eq__: book1 == book3: {book1 == book3}")
print(f"__lt__: book2 < book1: {book2 < book1}")
print(f"__add__: book1 + book2 = {book1 + book2} 页")

# ============================================================
# 8. 属性装饰器
# ============================================================

print("\n" + "=" * 50)
print("属性装饰器:")
print("=" * 50)

class Temperature:
    """温度类，演示 property 装饰器"""
    
    def __init__(self, celsius=0):
        self._celsius = celsius
    
    @property
    def celsius(self):
        """获取摄氏温度"""
        return self._celsius
    
    @celsius.setter
    def celsius(self, value):
        """设置摄氏温度"""
        if value < -273.15:
            raise ValueError("温度不能低于绝对零度")
        self._celsius = value
    
    @property
    def fahrenheit(self):
        """获取华氏温度"""
        return self._celsius * 9/5 + 32
    
    @fahrenheit.setter
    def fahrenheit(self, value):
        """设置华氏温度"""
        self.celsius = (value - 32) * 5/9

# 使用属性装饰器
temp = Temperature(25)
print(f"摄氏温度: {temp.celsius}°C")
print(f"华氏温度: {temp.fahrenheit}°F")

temp.celsius = 30
print(f"修改后 - 摄氏: {temp.celsius}°C, 华氏: {temp.fahrenheit}°F")

temp.fahrenheit = 86
print(f"通过华氏设置 - 摄氏: {temp.celsius}°C, 华氏: {temp.fahrenheit}°F")

# ============================================================
# 9. 实际应用示例
# ============================================================

print("\n" + "=" * 50)
print("实际应用示例:")
print("=" * 50)

# 示例：学生管理系统
class Student:
    """学生类"""
    
    def __init__(self, student_id, name, age):
        self.student_id = student_id
        self.name = name
        self.age = age
        self.courses = []
    
    def enroll(self, course):
        """选课"""
        if course not in self.courses:
            self.courses.append(course)
            print(f"{self.name} 选修了 {course}")
    
    def drop(self, course):
        """退课"""
        if course in self.courses:
            self.courses.remove(course)
            print(f"{self.name} 退选了 {course}")
    
    def get_courses(self):
        """获取课程列表"""
        return self.courses
    
    def __str__(self):
        return f"学生: {self.name} (ID: {self.student_id})"

class Course:
    """课程类"""
    
    def __init__(self, course_id, name, credits):
        self.course_id = course_id
        self.name = name
        self.credits = credits
        self.students = []
    
    def add_student(self, student):
        """添加学生"""
        if student not in self.students:
            self.students.append(student)
            student.enroll(self.name)
    
    def get_student_count(self):
        """获取学生人数"""
        return len(self.students)
    
    def __str__(self):
        return f"课程: {self.name} ({self.credits}学分)"

# 使用学生管理系统
student1 = Student("S001", "张三", 20)
student2 = Student("S002", "李四", 21)

course1 = Course("C001", "Python 编程", 3)
course2 = Course("C002", "数据结构", 4)

print("\n选课操作:")
course1.add_student(student1)
course1.add_student(student2)
course2.add_student(student1)

print(f"\n{student1.name} 的课程: {student1.get_courses()}")
print(f"{course1.name} 的学生人数: {course1.get_student_count()}")

# ============================================================
# 总结
# ============================================================

print("\n" + "=" * 50)
print("总结:")
print("=" * 50)
print("""
面向对象编程要点:
1. 类定义: class ClassName:
2. 构造函数: __init__(self, ...)
3. 实例属性: self.attribute
4. 类属性: ClassName.attribute
5. 方法: def method(self, ...)
6. 继承: class Child(Parent):
7. 多态: 不同类实现相同接口
8. 封装: 使用 __ 前缀创建私有属性

特殊方法:
- __init__: 构造函数
- __str__: 字符串表示
- __repr__: 官方表示
- __len__: 长度
- __eq__: 相等比较
- __lt__: 小于比较
- __add__: 加法运算

装饰器:
- @property: 将方法转为属性
- @classmethod: 类方法
- @staticmethod: 静态方法

最佳实践:
- 使用有意义的类名（首字母大写）
- 一个类只负责一件事
- 使用继承实现代码复用
- 使用封装保护数据
- 添加文档字符串
""")
