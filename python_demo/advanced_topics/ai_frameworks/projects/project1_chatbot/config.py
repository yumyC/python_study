"""
聊天机器人配置文件

包含机器人角色、系统设置和环境配置
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 应用配置
APP_CONFIG = {
    "title": os.getenv("APP_TITLE", "智能聊天机器人"),
    "page_icon": "🤖",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# 模型配置
MODEL_CONFIG = {
    "default_model": "gpt-3.5-turbo",
    "temperature": 0.7,
    "max_tokens": 500,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}

# 记忆配置
MEMORY_CONFIG = {
    "default_length": 10,
    "max_length": 50,
    "buffer_size": 2000
}

# 机器人角色配置
PERSONAS = {
    "assistant": {
        "name": "智能助手",
        "description": "专业、有帮助的AI助手",
        "system_prompt": """你是一个专业、有帮助的AI助手。你的特点是：
1. 回答准确、详细且有用
2. 语言正式但友好
3. 会主动提供相关建议
4. 承认不知道的事情
5. 遵循道德和安全准则

请用中文回答，保持专业和有帮助的态度。""",
        "temperature": 0.3,
        "emoji": "🤖"
    },
    
    "friend": {
        "name": "友好伙伴",
        "description": "轻松、友好的聊天伙伴",
        "system_prompt": """你是一个友好、随和的聊天伙伴。你的特点是：
1. 语言轻松自然，像朋友一样
2. 有幽默感，会开适当的玩笑
3. 关心用户的感受
4. 分享有趣的观点和经历
5. 保持积极乐观的态度

请用中文回答，像朋友一样轻松地聊天。""",
        "temperature": 0.8,
        "emoji": "😊"
    },
    
    "expert": {
        "name": "专业专家",
        "description": "某个领域的专业专家",
        "system_prompt": """你是一个专业领域的专家。你的特点是：
1. 拥有深厚的专业知识
2. 回答精确、权威
3. 提供详细的技术解释
4. 引用相关的理论和实践
5. 给出专业建议和最佳实践

请根据问题的领域展现相应的专业知识，用中文详细回答。""",
        "temperature": 0.2,
        "emoji": "🎓"
    },
    
    "creative": {
        "name": "创意大师",
        "description": "富有创意和想象力的助手",
        "system_prompt": """你是一个富有创意和想象力的助手。你的特点是：
1. 思维发散，充满创意
2. 提供独特的视角和想法
3. 善于头脑风暴和创意思考
4. 用生动的比喻和故事
5. 鼓励创新和探索

请用中文回答，展现你的创造力和想象力。""",
        "temperature": 0.9,
        "emoji": "🎨"
    },
    
    "teacher": {
        "name": "耐心老师",
        "description": "耐心的教学助手",
        "system_prompt": """你是一个耐心的老师。你的特点是：
1. 善于解释复杂概念
2. 循序渐进地教学
3. 使用简单易懂的例子
4. 鼓励学生提问
5. 检查学生的理解程度

请用中文回答，像老师一样耐心地解释和教学。""",
        "temperature": 0.4,
        "emoji": "👨‍🏫"
    }
}

# 对话设置选项
CONVERSATION_SETTINGS = {
    "temperature": {
        "min": 0.0,
        "max": 1.0,
        "default": 0.7,
        "step": 0.1,
        "help": "控制回复的创造性。值越高越有创意，值越低越保守。"
    },
    "max_tokens": {
        "min": 50,
        "max": 1000,
        "default": 500,
        "step": 50,
        "help": "回复的最大长度（以token为单位）。"
    },
    "memory_length": {
        "min": 1,
        "max": 20,
        "default": 10,
        "step": 1,
        "help": "记住的对话轮数。值越大记忆越长，但消耗更多资源。"
    }
}

# 文件路径配置
PATHS = {
    "data_dir": "data",
    "conversations_dir": "data/conversations",
    "personas_dir": "data/personas",
    "logs_dir": "logs"
}

# API 配置
API_CONFIG = {
    "openai_api_key": os.getenv("OPENAI_API_KEY"),
    "openai_api_base": os.getenv("OPENAI_API_BASE"),
    "timeout": 30,
    "max_retries": 3
}

# 界面配置
UI_CONFIG = {
    "sidebar_width": 300,
    "chat_height": 400,
    "message_avatar": {
        "user": "👤",
        "assistant": "🤖"
    },
    "colors": {
        "primary": "#FF6B6B",
        "secondary": "#4ECDC4",
        "success": "#45B7D1",
        "warning": "#FFA07A",
        "error": "#FF6B6B"
    }
}

# 功能开关
FEATURES = {
    "enable_memory": True,
    "enable_export": True,
    "enable_voice": False,  # 语音功能（未实现）
    "enable_file_upload": False,  # 文件上传功能（未实现）
    "enable_web_search": False,  # 网络搜索功能（未实现）
    "enable_analytics": True,  # 使用分析
    "enable_feedback": True  # 用户反馈
}

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/chatbot.log",
    "max_size": 10 * 1024 * 1024,  # 10MB
    "backup_count": 5
}

# 安全配置
SECURITY_CONFIG = {
    "max_message_length": 2000,
    "rate_limit": {
        "requests_per_minute": 30,
        "requests_per_hour": 500
    },
    "content_filter": {
        "enable": True,
        "blocked_words": [],  # 可以添加需要过滤的词汇
        "max_toxicity_score": 0.8
    }
}

def get_persona_config(persona_name: str) -> Dict[str, Any]:
    """获取指定角色的配置"""
    return PERSONAS.get(persona_name, PERSONAS["assistant"])

def get_model_config(persona_name: str = None) -> Dict[str, Any]:
    """获取模型配置，可以根据角色调整"""
    config = MODEL_CONFIG.copy()
    
    if persona_name and persona_name in PERSONAS:
        persona_config = PERSONAS[persona_name]
        if "temperature" in persona_config:
            config["temperature"] = persona_config["temperature"]
    
    return config

def validate_config() -> bool:
    """验证配置的有效性"""
    # 检查必要的环境变量
    if not API_CONFIG["openai_api_key"]:
        print("警告: 未设置 OPENAI_API_KEY 环境变量")
        return False
    
    # 检查目录是否存在，不存在则创建
    import os
    for path in PATHS.values():
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
    
    return True

def get_available_personas() -> Dict[str, str]:
    """获取可用的角色列表"""
    return {
        key: f"{config['emoji']} {config['name']}"
        for key, config in PERSONAS.items()
    }

# 导出主要配置
__all__ = [
    "APP_CONFIG",
    "MODEL_CONFIG", 
    "MEMORY_CONFIG",
    "PERSONAS",
    "CONVERSATION_SETTINGS",
    "PATHS",
    "API_CONFIG",
    "UI_CONFIG",
    "FEATURES",
    "LOGGING_CONFIG",
    "SECURITY_CONFIG",
    "get_persona_config",
    "get_model_config",
    "validate_config",
    "get_available_personas"
]