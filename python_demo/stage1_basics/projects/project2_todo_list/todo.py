"""
项目2: 待办事项列表

功能:
- 添加任务
- 查看所有任务
- 标记任务完成
- 删除任务
- 任务持久化（保存到文件）
"""

import json
import os
from datetime import datetime


class Task:
    """任务类"""
    
    def __init__(self, title, description="", priority="中", completed=False, created_at=None):
        """初始化任务"""
        self.title = title
        self.description = description
        self.priority = priority  # 高、中、低
        self.completed = completed
        self.created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def mark_completed(self):
        """标记为已完成"""
        self.completed = True
    
    def to_dict(self):
        """转换为字典"""
        return {
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "completed": self.completed,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建任务"""
        return cls(
            title=data["title"],
            description=data.get("description", ""),
            priority=data.get("priority", "中"),
            completed=data.get("completed", False),
            created_at=data.get("created_at")
        )
    
    def __str__(self):
        """字符串表示"""
        status = "✓" if self.completed else "✗"
        return f"[{status}] {self.title} (优先级: {self.priority})"


class TodoList:
    """待办事项列表类"""
    
    def __init__(self, filename="tasks.json"):
        """初始化待办列表"""
        self.filename = filename
        self.tasks = []
        self.load_tasks()
    
    def add_task(self, title, description="", priority="中"):
        """添加任务"""
        task = Task(title, description, priority)
        self.tasks.append(task)
        self.save_tasks()
        print(f"✓ 任务已添加: {title}")
    
    def list_tasks(self, show_completed=True):
        """列出所有任务"""
        if not self.tasks:
            print("暂无任务")
            return
        
        print("\n" + "=" * 60)
        print("待办事项列表")
        print("=" * 60)
        
        for i, task in enumerate(self.tasks, 1):
            if not show_completed and task.completed:
                continue
            
            status = "✓ 已完成" if task.completed else "✗ 未完成"
            print(f"\n{i}. {task.title}")
            print(f"   状态: {status}")
            print(f"   优先级: {task.priority}")
            if task.description:
                print(f"   描述: {task.description}")
            print(f"   创建时间: {task.created_at}")
        
        print("=" * 60)
    
    def complete_task(self, index):
        """标记任务为已完成"""
        if 0 <= index < len(self.tasks):
            self.tasks[index].mark_completed()
            self.save_tasks()
            print(f"✓ 任务已完成: {self.tasks[index].title}")
        else:
            print("错误: 无效的任务编号")
    
    def delete_task(self, index):
        """删除任务"""
        if 0 <= index < len(self.tasks):
            task = self.tasks.pop(index)
            self.save_tasks()
            print(f"✓ 任务已删除: {task.title}")
        else:
            print("错误: 无效的任务编号")
    
    def get_statistics(self):
        """获取统计信息"""
        total = len(self.tasks)
        completed = sum(1 for task in self.tasks if task.completed)
        pending = total - completed
        
        print("\n" + "=" * 40)
        print("统计信息")
        print("=" * 40)
        print(f"总任务数: {total}")
        print(f"已完成: {completed}")
        print(f"未完成: {pending}")
        if total > 0:
            completion_rate = (completed / total) * 100
            print(f"完成率: {completion_rate:.1f}%")
        print("=" * 40)
    
    def save_tasks(self):
        """保存任务到文件"""
        try:
            data = [task.to_dict() for task in self.tasks]
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存失败: {e}")
    
    def load_tasks(self):
        """从文件加载任务"""
        if not os.path.exists(self.filename):
            return
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.tasks = [Task.from_dict(task_data) for task_data in data]
        except Exception as e:
            print(f"加载失败: {e}")
    
    def clear_completed(self):
        """清除已完成的任务"""
        original_count = len(self.tasks)
        self.tasks = [task for task in self.tasks if not task.completed]
        removed_count = original_count - len(self.tasks)
        self.save_tasks()
        print(f"✓ 已清除 {removed_count} 个已完成任务")


def print_menu():
    """打印菜单"""
    print("\n" + "=" * 40)
    print("待办事项管理系统")
    print("=" * 40)
    print("1. 添加任务")
    print("2. 查看所有任务")
    print("3. 查看未完成任务")
    print("4. 标记任务完成")
    print("5. 删除任务")
    print("6. 清除已完成任务")
    print("7. 查看统计信息")
    print("0. 退出")
    print("=" * 40)


def get_priority():
    """获取优先级"""
    print("选择优先级:")
    print("1. 高")
    print("2. 中")
    print("3. 低")
    choice = input("请选择 (1-3, 默认为中): ").strip()
    
    priority_map = {"1": "高", "2": "中", "3": "低"}
    return priority_map.get(choice, "中")


def main():
    """主函数"""
    todo_list = TodoList()
    
    print("欢迎使用待办事项管理系统！")
    
    while True:
        print_menu()
        choice = input("请选择操作 (0-7): ").strip()
        
        try:
            if choice == '0':
                print("感谢使用，再见！")
                break
            
            elif choice == '1':
                # 添加任务
                title = input("请输入任务标题: ").strip()
                if not title:
                    print("错误: 任务标题不能为空")
                    continue
                
                description = input("请输入任务描述 (可选): ").strip()
                priority = get_priority()
                
                todo_list.add_task(title, description, priority)
            
            elif choice == '2':
                # 查看所有任务
                todo_list.list_tasks()
            
            elif choice == '3':
                # 查看未完成任务
                todo_list.list_tasks(show_completed=False)
            
            elif choice == '4':
                # 标记任务完成
                todo_list.list_tasks(show_completed=False)
                if todo_list.tasks:
                    try:
                        index = int(input("请输入要完成的任务编号: ")) - 1
                        todo_list.complete_task(index)
                    except ValueError:
                        print("错误: 请输入有效的数字")
            
            elif choice == '5':
                # 删除任务
                todo_list.list_tasks()
                if todo_list.tasks:
                    try:
                        index = int(input("请输入要删除的任务编号: ")) - 1
                        confirm = input("确认删除? (y/n): ").strip().lower()
                        if confirm == 'y':
                            todo_list.delete_task(index)
                        else:
                            print("已取消删除")
                    except ValueError:
                        print("错误: 请输入有效的数字")
            
            elif choice == '6':
                # 清除已完成任务
                confirm = input("确认清除所有已完成任务? (y/n): ").strip().lower()
                if confirm == 'y':
                    todo_list.clear_completed()
                else:
                    print("已取消操作")
            
            elif choice == '7':
                # 查看统计信息
                todo_list.get_statistics()
            
            else:
                print("错误: 无效的选择，请输入 0-7")
        
        except Exception as e:
            print(f"发生错误: {e}")


if __name__ == '__main__':
    main()
