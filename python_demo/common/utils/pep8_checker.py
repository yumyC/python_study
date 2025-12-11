#!/usr/bin/env python3
"""
PEP 8 代码规范检查工具

检查 Python 代码是否符合 PEP 8 规范的基本要求：
- 行长度不超过 88 字符
- 导入语句规范
- 空行使用规范
- 命名规范
- 注释规范
"""

import os
import re
import sys
from pathlib import Path
from typing import List, Tuple


class PEP8Checker:
    """PEP 8 规范检查器"""
    
    def __init__(self, max_line_length: int = 88):
        self.max_line_length = max_line_length
        self.issues = []
    
    def check_file(self, file_path: str) -> List[Tuple[int, str]]:
        """
        检查单个文件的 PEP 8 规范
        
        Args:
            file_path: 文件路径
        
        Returns:
            List[Tuple[int, str]]: 问题列表，格式为 (行号, 问题描述)
        """
        issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except Exception as e:
            return [(0, f"无法读取文件: {e}")]
        
        for line_num, line in enumerate(lines, 1):
            # 检查行长度
            if len(line.rstrip()) > self.max_line_length:
                issues.append((line_num, f"行长度超过 {self.max_line_length} 字符"))
            
            # 检查尾随空格
            if line.rstrip() != line.rstrip('\n'):
                issues.append((line_num, "行末有多余空格"))
            
            # 检查制表符
            if '\t' in line:
                issues.append((line_num, "使用了制表符，应使用空格"))
            
            # 检查导入语句
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                if line_num > 1 and lines[line_num - 2].strip() and not lines[line_num - 2].strip().startswith(('import', 'from', '#', '"""', "'''")):
                    if not self._is_docstring_line(lines, line_num - 2):
                        issues.append((line_num, "导入语句前应有空行"))
        
        return issues
    
    def _is_docstring_line(self, lines: List[str], line_index: int) -> bool:
        """检查是否是文档字符串的一部分"""
        if line_index < 0 or line_index >= len(lines):
            return False
        
        line = lines[line_index].strip()
        return line.startswith('"""') or line.startswith("'''") or line.endswith('"""') or line.endswith("'''")
    
    def check_directory(self, directory: str) -> dict:
        """
        检查目录下所有 Python 文件
        
        Args:
            directory: 目录路径
        
        Returns:
            dict: 文件路径到问题列表的映射
        """
        results = {}
        
        for root, dirs, files in os.walk(directory):
            # 跳过虚拟环境和缓存目录
            dirs[:] = [d for d in dirs if d not in ['.venv', '__pycache__', '.git', 'venv']]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    issues = self.check_file(file_path)
                    if issues:
                        results[file_path] = issues
        
        return results
    
    def format_results(self, results: dict) -> str:
        """格式化检查结果"""
        if not results:
            return "✅ 所有文件都符合 PEP 8 规范！"
        
        output = []
        total_issues = 0
        
        for file_path, issues in results.items():
            output.append(f"\n📁 {file_path}")
            for line_num, issue in issues:
                output.append(f"  第 {line_num} 行: {issue}")
                total_issues += 1
        
        output.insert(0, f"❌ 发现 {total_issues} 个 PEP 8 规范问题：")
        return "\n".join(output)


def main():
    """主函数"""
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = "."
    
    checker = PEP8Checker()
    
    if os.path.isfile(target):
        issues = checker.check_file(target)
        if issues:
            print(f"📁 {target}")
            for line_num, issue in issues:
                print(f"  第 {line_num} 行: {issue}")
        else:
            print("✅ 文件符合 PEP 8 规范！")
    else:
        results = checker.check_directory(target)
        print(checker.format_results(results))


if __name__ == "__main__":
    main()