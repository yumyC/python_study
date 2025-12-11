"""
聊天机器人工具函数

包含各种辅助功能和工具函数
"""

import os
import json
import time
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
import streamlit as st

def create_directories():
    """创建必要的目录结构"""
    from config import PATHS
    
    for path in PATHS.values():
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            print(f"创建目录: {path}")

def generate_session_id() -> str:
    """生成唯一的会话ID"""
    timestamp = str(int(time.time()))
    random_str = str(hash(timestamp))[-6:]
    return f"session_{timestamp}_{random_str}"

def format_timestamp(timestamp: Optional[float] = None) -> str:
    """格式化时间戳"""
    if timestamp is None:
        timestamp = time.time()
    
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def save_conversation(session_id: str, conversation: List[Dict[str, Any]]) -> bool:
    """保存对话历史到文件"""
    try:
        from config import PATHS
        
        filename = f"{session_id}.json"
        filepath = os.path.join(PATHS["conversations_dir"], filename)
        
        conversation_data = {
            "session_id": session_id,
            "created_at": time.time(),
            "updated_at": time.time(),
            "messages": conversation
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conversation_data, f, ensure_ascii=False, indent=2)
        
        return True
    
    except Exception as e:
        print(f"保存对话失败: {e}")
        return False

def load_conversation(session_id: str) -> Optional[List[Dict[str, Any]]]:
    """从文件加载对话历史"""
    try:
        from config import PATHS
        
        filename = f"{session_id}.json"
        filepath = os.path.join(PATHS["conversations_dir"], filename)
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            conversation_data = json.load(f)
        
        return conversation_data.get("messages", [])
    
    except Exception as e:
        print(f"加载对话失败: {e}")
        return None

def export_conversation_to_text(conversation: List[Dict[str, Any]]) -> str:
    """将对话导出为文本格式"""
    lines = []
    lines.append("=" * 50)
    lines.append("聊天记录")
    lines.append(f"导出时间: {format_timestamp()}")
    lines.append("=" * 50)
    lines.append("")
    
    for i, message in enumerate(conversation, 1):
        role = message.get("role", "unknown")
        content = message.get("content", "")
        timestamp = message.get("timestamp")
        
        role_name = "用户" if role == "user" else "助手"
        time_str = format_timestamp(timestamp) if timestamp else "未知时间"
        
        lines.append(f"{i}. {role_name} ({time_str}):")
        lines.append(content)
        lines.append("")
    
    lines.append("=" * 50)
    lines.append("导出完成")
    
    return "\n".join(lines)

def calculate_token_count(text: str) -> int:
    """估算文本的token数量（简单估算）"""
    # 简单估算：中文字符按1.5个token计算，英文单词按1个token计算
    chinese_chars = sum(1 for char in text if '\u4e00' <= char <= '\u9fff')
    english_words = len([word for word in text.split() if word.isalpha()])
    other_chars = len(text) - chinese_chars - sum(len(word) for word in text.split() if word.isalpha())
    
    estimated_tokens = int(chinese_chars * 1.5 + english_words + other_chars * 0.5)
    return max(estimated_tokens, 1)

def truncate_conversation_by_tokens(conversation: List[Dict[str, Any]], 
                                  max_tokens: int) -> List[Dict[str, Any]]:
    """根据token数量截断对话历史"""
    if not conversation:
        return []
    
    total_tokens = 0
    truncated_conversation = []
    
    # 从最新的消息开始计算
    for message in reversed(conversation):
        content = message.get("content", "")
        message_tokens = calculate_token_count(content)
        
        if total_tokens + message_tokens <= max_tokens:
            truncated_conversation.insert(0, message)
            total_tokens += message_tokens
        else:
            break
    
    return truncated_conversation

def clean_text(text: str) -> str:
    """清理文本内容"""
    if not text:
        return ""
    
    # 移除多余的空白字符
    text = " ".join(text.split())
    
    # 移除特殊字符（保留基本标点）
    import re
    text = re.sub(r'[^\w\s\u4e00-\u9fff.,!?;:()""''—-]', '', text)
    
    return text.strip()

def validate_message(message: str) -> tuple[bool, str]:
    """验证消息内容"""
    from config import SECURITY_CONFIG
    
    if not message or not message.strip():
        return False, "消息不能为空"
    
    if len(message) > SECURITY_CONFIG["max_message_length"]:
        return False, f"消息长度不能超过 {SECURITY_CONFIG['max_message_length']} 字符"
    
    # 检查是否包含被禁止的词汇
    blocked_words = SECURITY_CONFIG["content_filter"]["blocked_words"]
    message_lower = message.lower()
    
    for word in blocked_words:
        if word.lower() in message_lower:
            return False, "消息包含不当内容"
    
    return True, "验证通过"

def get_conversation_stats(conversation: List[Dict[str, Any]]) -> Dict[str, Any]:
    """获取对话统计信息"""
    if not conversation:
        return {
            "total_messages": 0,
            "user_messages": 0,
            "assistant_messages": 0,
            "total_tokens": 0,
            "average_message_length": 0,
            "conversation_duration": 0
        }
    
    user_messages = [msg for msg in conversation if msg.get("role") == "user"]
    assistant_messages = [msg for msg in conversation if msg.get("role") == "assistant"]
    
    total_tokens = sum(calculate_token_count(msg.get("content", "")) for msg in conversation)
    total_chars = sum(len(msg.get("content", "")) for msg in conversation)
    
    # 计算对话持续时间
    timestamps = [msg.get("timestamp") for msg in conversation if msg.get("timestamp")]
    duration = 0
    if len(timestamps) >= 2:
        duration = max(timestamps) - min(timestamps)
    
    return {
        "total_messages": len(conversation),
        "user_messages": len(user_messages),
        "assistant_messages": len(assistant_messages),
        "total_tokens": total_tokens,
        "total_characters": total_chars,
        "average_message_length": total_chars / len(conversation) if conversation else 0,
        "conversation_duration": duration
    }

def format_duration(seconds: float) -> str:
    """格式化持续时间"""
    if seconds < 60:
        return f"{int(seconds)} 秒"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"{minutes} 分钟"
    else:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        return f"{hours} 小时 {minutes} 分钟"

def create_download_link(content: str, filename: str, link_text: str) -> str:
    """创建下载链接"""
    import base64
    
    # 将内容编码为base64
    b64_content = base64.b64encode(content.encode('utf-8')).decode()
    
    # 创建下载链接
    href = f'<a href="data:text/plain;base64,{b64_content}" download="{filename}">{link_text}</a>'
    
    return href

def display_message(role: str, content: str, timestamp: Optional[float] = None):
    """显示消息（Streamlit组件）"""
    from config import UI_CONFIG
    
    avatar = UI_CONFIG["message_avatar"].get(role, "❓")
    role_name = "用户" if role == "user" else "助手"
    
    # 创建消息容器
    with st.container():
        col1, col2 = st.columns([1, 10])
        
        with col1:
            st.write(avatar)
        
        with col2:
            st.write(f"**{role_name}**")
            st.write(content)
            
            if timestamp:
                st.caption(format_timestamp(timestamp))

def show_typing_indicator():
    """显示打字指示器"""
    with st.empty():
        for i in range(3):
            st.write("🤖 正在思考" + "." * (i + 1))
            time.sleep(0.5)

def rate_limit_check(session_id: str) -> bool:
    """检查速率限制"""
    from config import SECURITY_CONFIG
    
    # 这里可以实现更复杂的速率限制逻辑
    # 目前只是简单的检查
    
    current_time = time.time()
    
    # 从session state获取请求历史
    if "request_history" not in st.session_state:
        st.session_state.request_history = []
    
    # 清理过期的请求记录
    st.session_state.request_history = [
        req_time for req_time in st.session_state.request_history
        if current_time - req_time < 3600  # 保留1小时内的记录
    ]
    
    # 检查每分钟请求数
    recent_requests = [
        req_time for req_time in st.session_state.request_history
        if current_time - req_time < 60  # 1分钟内
    ]
    
    if len(recent_requests) >= SECURITY_CONFIG["rate_limit"]["requests_per_minute"]:
        return False
    
    # 检查每小时请求数
    if len(st.session_state.request_history) >= SECURITY_CONFIG["rate_limit"]["requests_per_hour"]:
        return False
    
    # 记录当前请求
    st.session_state.request_history.append(current_time)
    
    return True

def log_user_interaction(action: str, details: Dict[str, Any] = None):
    """记录用户交互（用于分析）"""
    from config import FEATURES, LOGGING_CONFIG
    
    if not FEATURES["enable_analytics"]:
        return
    
    log_entry = {
        "timestamp": time.time(),
        "action": action,
        "session_id": st.session_state.get("session_id", "unknown"),
        "details": details or {}
    }
    
    # 这里可以将日志发送到分析服务
    # 目前只是打印到控制台
    if LOGGING_CONFIG["level"] == "DEBUG":
        print(f"用户交互: {json.dumps(log_entry, ensure_ascii=False)}")

def get_system_info() -> Dict[str, Any]:
    """获取系统信息"""
    import platform
    import psutil
    
    return {
        "platform": platform.system(),
        "python_version": platform.python_version(),
        "cpu_count": psutil.cpu_count(),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
        "disk_usage": psutil.disk_usage('/').percent
    }

# 导出主要函数
__all__ = [
    "create_directories",
    "generate_session_id",
    "format_timestamp",
    "save_conversation",
    "load_conversation",
    "export_conversation_to_text",
    "calculate_token_count",
    "truncate_conversation_by_tokens",
    "clean_text",
    "validate_message",
    "get_conversation_stats",
    "format_duration",
    "create_download_link",
    "display_message",
    "show_typing_indicator",
    "rate_limit_check",
    "log_user_interaction",
    "get_system_info"
]