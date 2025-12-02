"""
项目3: 文件管理器

功能:
- 列出目录内容
- 创建文件和目录
- 删除文件和目录
- 复制和移动文件
- 查看文件信息
- 搜索文件
"""

import os
import shutil
from pathlib import Path
from datetime import datetime


class FileManager:
    """文件管理器类"""
    
    def __init__(self):
        """初始化文件管理器"""
        self.current_path = Path.cwd()
    
    def list_directory(self, path=None):
        """列出目录内容"""
        target_path = Path(path) if path else self.current_path
        
        if not target_path.exists():
            print(f"错误: 路径不存在: {target_path}")
            return
        
        if not target_path.is_dir():
            print(f"错误: 不是目录: {target_path}")
            return
        
        print("\n" + "=" * 70)
        print(f"目录: {target_path.absolute()}")
        print("=" * 70)
        print(f"{'类型':<8} {'名称':<30} {'大小':<15} {'修改时间':<20}")
        print("-" * 70)
        
        items = sorted(target_path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower()))
        
        for item in items:
            item_type = "[目录]" if item.is_dir() else "[文件]"
            name = item.name
            
            if item.is_file():
                size = self._format_size(item.stat().st_size)
            else:
                size = "-"
            
            mtime = datetime.fromtimestamp(item.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            
            print(f"{item_type:<8} {name:<30} {size:<15} {mtime:<20}")
        
        print("=" * 70)
    
    def create_file(self, filename, content=""):
        """创建文件"""
        file_path = self.current_path / filename
        
        if file_path.exists():
            print(f"错误: 文件已存在: {filename}")
            return
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✓ 文件已创建: {filename}")
        except Exception as e:
            print(f"创建文件失败: {e}")
    
    def create_directory(self, dirname):
        """创建目录"""
        dir_path = self.current_path / dirname
        
        if dir_path.exists():
            print(f"错误: 目录已存在: {dirname}")
            return
        
        try:
            dir_path.mkdir(parents=True)
            print(f"✓ 目录已创建: {dirname}")
        except Exception as e:
            print(f"创建目录失败: {e}")
    
    def delete_file(self, filename):
        """删除文件"""
        file_path = self.current_path / filename
        
        if not file_path.exists():
            print(f"错误: 文件不存在: {filename}")
            return
        
        if not file_path.is_file():
            print(f"错误: 不是文件: {filename}")
            return
        
        try:
            file_path.unlink()
            print(f"✓ 文件已删除: {filename}")
        except Exception as e:
            print(f"删除文件失败: {e}")
    
    def delete_directory(self, dirname):
        """删除目录"""
        dir_path = self.current_path / dirname
        
        if not dir_path.exists():
            print(f"错误: 目录不存在: {dirname}")
            return
        
        if not dir_path.is_dir():
            print(f"错误: 不是目录: {dirname}")
            return
        
        try:
            shutil.rmtree(dir_path)
            print(f"✓ 目录已删除: {dirname}")
        except Exception as e:
            print(f"删除目录失败: {e}")
    
    def copy_file(self, source, destination):
        """复制文件"""
        src_path = self.current_path / source
        dst_path = self.current_path / destination
        
        if not src_path.exists():
            print(f"错误: 源文件不存在: {source}")
            return
        
        if not src_path.is_file():
            print(f"错误: 不是文件: {source}")
            return
        
        try:
            shutil.copy2(src_path, dst_path)
            print(f"✓ 文件已复制: {source} -> {destination}")
        except Exception as e:
            print(f"复制文件失败: {e}")
    
    def move_file(self, source, destination):
        """移动文件"""
        src_path = self.current_path / source
        dst_path = self.current_path / destination
        
        if not src_path.exists():
            print(f"错误: 源文件不存在: {source}")
            return
        
        try:
            shutil.move(str(src_path), str(dst_path))
            print(f"✓ 文件已移动: {source} -> {destination}")
        except Exception as e:
            print(f"移动文件失败: {e}")
    
    def show_file_info(self, filename):
        """显示文件信息"""
        file_path = self.current_path / filename
        
        if not file_path.exists():
            print(f"错误: 文件不存在: {filename}")
            return
        
        stat = file_path.stat()
        
        print("\n" + "=" * 50)
        print("文件信息")
        print("=" * 50)
        print(f"名称: {file_path.name}")
        print(f"路径: {file_path.absolute()}")
        print(f"类型: {'目录' if file_path.is_dir() else '文件'}")
        
        if file_path.is_file():
            print(f"大小: {self._format_size(stat.st_size)}")
            print(f"扩展名: {file_path.suffix}")
        
        print(f"创建时间: {datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"修改时间: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"访问时间: {datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 50)
    
    def search_files(self, pattern):
        """搜索文件"""
        print(f"\n搜索 '{pattern}' ...")
        print("=" * 50)
        
        matches = list(self.current_path.rglob(f"*{pattern}*"))
        
        if not matches:
            print("未找到匹配的文件")
            return
        
        print(f"找到 {len(matches)} 个匹配项:")
        for match in matches:
            relative_path = match.relative_to(self.current_path)
            item_type = "[目录]" if match.is_dir() else "[文件]"
            print(f"  {item_type} {relative_path}")
        
        print("=" * 50)
    
    def read_file(self, filename):
        """读取文件内容"""
        file_path = self.current_path / filename
        
        if not file_path.exists():
            print(f"错误: 文件不存在: {filename}")
            return
        
        if not file_path.is_file():
            print(f"错误: 不是文件: {filename}")
            return
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print("\n" + "=" * 50)
            print(f"文件内容: {filename}")
            print("=" * 50)
            print(content)
            print("=" * 50)
        except UnicodeDecodeError:
            print("错误: 无法读取文件（可能是二进制文件）")
        except Exception as e:
            print(f"读取文件失败: {e}")
    
    def change_directory(self, path):
        """切换目录"""
        if path == "..":
            self.current_path = self.current_path.parent
            print(f"✓ 已切换到: {self.current_path}")
        else:
            new_path = self.current_path / path
            if new_path.exists() and new_path.is_dir():
                self.current_path = new_path
                print(f"✓ 已切换到: {self.current_path}")
            else:
                print(f"错误: 目录不存在: {path}")
    
    @staticmethod
    def _format_size(size):
        """格式化文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.2f} {unit}"
            size /= 1024.0
        return f"{size:.2f} PB"


def print_menu():
    """打印菜单"""
    print("\n" + "=" * 50)
    print("文件管理器")
    print("=" * 50)
    print("1. 列出目录内容")
    print("2. 创建文件")
    print("3. 创建目录")
    print("4. 删除文件")
    print("5. 删除目录")
    print("6. 复制文件")
    print("7. 移动文件")
    print("8. 查看文件信息")
    print("9. 搜索文件")
    print("10. 读取文件内容")
    print("11. 切换目录")
    print("0. 退出")
    print("=" * 50)


def main():
    """主函数"""
    fm = FileManager()
    
    print("欢迎使用文件管理器！")
    print(f"当前目录: {fm.current_path}")
    
    while True:
        print_menu()
        choice = input("请选择操作 (0-11): ").strip()
        
        try:
            if choice == '0':
                print("感谢使用，再见！")
                break
            
            elif choice == '1':
                # 列出目录内容
                fm.list_directory()
            
            elif choice == '2':
                # 创建文件
                filename = input("请输入文件名: ").strip()
                content = input("请输入文件内容 (可选): ").strip()
                fm.create_file(filename, content)
            
            elif choice == '3':
                # 创建目录
                dirname = input("请输入目录名: ").strip()
                fm.create_directory(dirname)
            
            elif choice == '4':
                # 删除文件
                filename = input("请输入要删除的文件名: ").strip()
                confirm = input(f"确认删除 '{filename}'? (y/n): ").strip().lower()
                if confirm == 'y':
                    fm.delete_file(filename)
                else:
                    print("已取消删除")
            
            elif choice == '5':
                # 删除目录
                dirname = input("请输入要删除的目录名: ").strip()
                confirm = input(f"确认删除目录 '{dirname}' 及其所有内容? (y/n): ").strip().lower()
                if confirm == 'y':
                    fm.delete_directory(dirname)
                else:
                    print("已取消删除")
            
            elif choice == '6':
                # 复制文件
                source = input("请输入源文件名: ").strip()
                destination = input("请输入目标文件名: ").strip()
                fm.copy_file(source, destination)
            
            elif choice == '7':
                # 移动文件
                source = input("请输入源文件名: ").strip()
                destination = input("请输入目标位置: ").strip()
                fm.move_file(source, destination)
            
            elif choice == '8':
                # 查看文件信息
                filename = input("请输入文件名: ").strip()
                fm.show_file_info(filename)
            
            elif choice == '9':
                # 搜索文件
                pattern = input("请输入搜索关键词: ").strip()
                fm.search_files(pattern)
            
            elif choice == '10':
                # 读取文件内容
                filename = input("请输入文件名: ").strip()
                fm.read_file(filename)
            
            elif choice == '11':
                # 切换目录
                path = input("请输入目录路径 (.. 返回上级): ").strip()
                fm.change_directory(path)
            
            else:
                print("错误: 无效的选择，请输入 0-11")
        
        except KeyboardInterrupt:
            print("\n操作已取消")
        except Exception as e:
            print(f"发生错误: {e}")


if __name__ == '__main__':
    main()
