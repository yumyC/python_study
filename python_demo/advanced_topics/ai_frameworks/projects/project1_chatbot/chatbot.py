"""
聊天机器人核心逻辑

实现基于 LangChain 的智能聊天机器人
"""

import os
import time
from typing import List, Dict, Any, Optional, Generator
import logging

# LangChain imports
try:
    from langchain.llms import OpenAI
    from langchain.chat_models import ChatOpenAI
    from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryBufferMemory
    from langchain.chains import ConversationChain
    from langchain.prompts import PromptTemplate
    from langchain.schema import BaseMessage, HumanMessage, AIMessage
    from langchain.callbacks.base import BaseCallbackHandler
    
    LANGCHAIN_AVAILABLE = True
except ImportError:
    print("LangChain 未安装，请运行: pip install langchain")
    LANGCHAIN_AVAILABLE = False

from config import (
    get_persona_config, 
    get_model_config, 
    API_CONFIG, 
    MEMORY_CONFIG,
    FEATURES
)
from utils import (
    calculate_token_count, 
    truncate_conversation_by_tokens,
    clean_text,
    validate_message,
    log_user_interaction
)

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StreamingCallbackHandler(BaseCallbackHandler):
    """流式输出回调处理器"""
    
    def __init__(self):
        self.tokens = []
        self.finished = False
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """处理新的token"""
        self.tokens.append(token)
    
    def on_llm_end(self, response, **kwargs) -> None:
        """LLM结束时调用"""
        self.finished = True
    
    def get_tokens(self) -> List[str]:
        """获取所有tokens"""
        return self.tokens.copy()
    
    def clear(self):
        """清空tokens"""
        self.tokens = []
        self.finished = False

class ChatBot:
    """智能聊天机器人"""
    
    def __init__(self, 
                 persona: str = "assistant",
                 memory_length: int = None,
                 temperature: float = None,
                 max_tokens: int = None):
        """
        初始化聊天机器人
        
        Args:
            persona: 机器人角色
            memory_length: 记忆长度
            temperature: 温度参数
            max_tokens: 最大token数
        """
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain 未安装，无法创建聊天机器人")
        
        self.persona = persona
        self.persona_config = get_persona_config(persona)
        self.model_config = get_model_config(persona)
        
        # 覆盖配置参数
        if memory_length is not None:
            self.memory_length = memory_length
        else:
            self.memory_length = MEMORY_CONFIG["default_length"]
        
        if temperature is not None:
            self.model_config["temperature"] = temperature
        
        if max_tokens is not None:
            self.model_config["max_tokens"] = max_tokens
        
        # 初始化组件
        self.llm = self._setup_llm()
        self.memory = self._setup_memory()
        self.conversation_chain = self._setup_conversation_chain()
        
        # 流式输出处理器
        self.streaming_handler = StreamingCallbackHandler()
        
        # 统计信息
        self.stats = {
            "total_messages": 0,
            "total_tokens": 0,
            "start_time": time.time()
        }
        
        logger.info(f"聊天机器人初始化完成 - 角色: {persona}, 记忆长度: {self.memory_length}")
    
    def _setup_llm(self):
        """设置语言模型"""
        try:
            if not API_CONFIG["openai_api_key"]:
                logger.warning("未设置 OpenAI API 密钥，使用模拟模式")
                return self._create_mock_llm()
            
            # 使用 ChatOpenAI 模型
            llm = ChatOpenAI(
                model_name=self.model_config["default_model"],
                temperature=self.model_config["temperature"],
                max_tokens=self.model_config["max_tokens"],
                openai_api_key=API_CONFIG["openai_api_key"],
                openai_api_base=API_CONFIG["openai_api_base"],
                request_timeout=API_CONFIG["timeout"],
                max_retries=API_CONFIG["max_retries"],
                streaming=True,  # 启用流式输出
                callbacks=[self.streaming_handler]
            )
            
            logger.info("OpenAI 模型初始化成功")
            return llm
            
        except Exception as e:
            logger.error(f"LLM 初始化失败: {e}")
            return self._create_mock_llm()
    
    def _create_mock_llm(self):
        """创建模拟LLM（用于演示）"""
        class MockLLM:
            def __init__(self, persona_config):
                self.persona_config = persona_config
            
            def __call__(self, prompt):
                # 简单的模拟回复
                if "你好" in prompt or "hello" in prompt.lower():
                    return f"你好！我是{self.persona_config['name']}，很高兴为您服务！"
                elif "再见" in prompt or "bye" in prompt.lower():
                    return "再见！期待下次与您交流！"
                else:
                    return f"作为{self.persona_config['name']}，我理解您的问题。这是一个模拟回复，因为没有配置真实的API密钥。"
        
        return MockLLM(self.persona_config)
    
    def _setup_memory(self):
        """设置对话记忆"""
        if not FEATURES["enable_memory"]:
            return None
        
        try:
            # 使用窗口缓冲记忆
            memory = ConversationBufferWindowMemory(
                k=self.memory_length,
                return_messages=True,
                memory_key="history"
            )
            
            logger.info(f"记忆系统初始化成功 - 长度: {self.memory_length}")
            return memory
            
        except Exception as e:
            logger.error(f"记忆系统初始化失败: {e}")
            return None
    
    def _setup_conversation_chain(self):
        """设置对话链"""
        try:
            # 创建提示模板
            prompt_template = PromptTemplate(
                input_variables=["history", "input"],
                template=f"""{self.persona_config['system_prompt']}

对话历史:
{{history}}

用户: {{input}}
助手:"""
            )
            
            # 创建对话链
            if self.memory:
                conversation = ConversationChain(
                    llm=self.llm,
                    memory=self.memory,
                    prompt=prompt_template,
                    verbose=False
                )
            else:
                # 无记忆模式
                conversation = ConversationChain(
                    llm=self.llm,
                    prompt=prompt_template,
                    verbose=False
                )
            
            logger.info("对话链初始化成功")
            return conversation
            
        except Exception as e:
            logger.error(f"对话链初始化失败: {e}")
            return None
    
    def chat(self, message: str) -> str:
        """
        处理用户消息并生成回复
        
        Args:
            message: 用户消息
            
        Returns:
            机器人回复
        """
        try:
            # 验证消息
            is_valid, error_msg = validate_message(message)
            if not is_valid:
                return f"抱歉，{error_msg}"
            
            # 清理消息
            cleaned_message = clean_text(message)
            
            # 记录用户交互
            log_user_interaction("user_message", {
                "message_length": len(cleaned_message),
                "persona": self.persona
            })
            
            # 生成回复
            if self.conversation_chain:
                response = self.conversation_chain.predict(input=cleaned_message)
            else:
                # 直接调用LLM
                response = self.llm(cleaned_message)
            
            # 清理回复
            cleaned_response = clean_text(response)
            
            # 更新统计信息
            self._update_stats(cleaned_message, cleaned_response)
            
            # 记录助手回复
            log_user_interaction("assistant_response", {
                "response_length": len(cleaned_response),
                "persona": self.persona
            })
            
            return cleaned_response
            
        except Exception as e:
            logger.error(f"聊天处理失败: {e}")
            return "抱歉，我遇到了一些技术问题，请稍后再试。"
    
    def chat_stream(self, message: str) -> Generator[str, None, None]:
        """
        流式聊天（逐步返回回复）
        
        Args:
            message: 用户消息
            
        Yields:
            回复的片段
        """
        try:
            # 验证消息
            is_valid, error_msg = validate_message(message)
            if not is_valid:
                yield f"抱歉，{error_msg}"
                return
            
            # 清理消息
            cleaned_message = clean_text(message)
            
            # 清空流式处理器
            self.streaming_handler.clear()
            
            # 开始生成回复
            if hasattr(self.llm, 'stream'):
                # 支持流式输出的模型
                for chunk in self.llm.stream(cleaned_message):
                    if chunk:
                        yield chunk
            else:
                # 不支持流式输出，模拟流式效果
                response = self.chat(cleaned_message)
                words = response.split()
                
                for i, word in enumerate(words):
                    yield word + (" " if i < len(words) - 1 else "")
                    time.sleep(0.05)  # 模拟打字效果
            
        except Exception as e:
            logger.error(f"流式聊天失败: {e}")
            yield "抱歉，我遇到了一些技术问题，请稍后再试。"
    
    def _update_stats(self, user_message: str, bot_response: str):
        """更新统计信息"""
        self.stats["total_messages"] += 1
        self.stats["total_tokens"] += calculate_token_count(user_message)
        self.stats["total_tokens"] += calculate_token_count(bot_response)
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """获取对话历史"""
        if not self.memory:
            return []
        
        try:
            # 从记忆中获取消息
            messages = self.memory.chat_memory.messages
            
            conversation = []
            for message in messages:
                if isinstance(message, HumanMessage):
                    conversation.append({
                        "role": "user",
                        "content": message.content,
                        "timestamp": time.time()
                    })
                elif isinstance(message, AIMessage):
                    conversation.append({
                        "role": "assistant", 
                        "content": message.content,
                        "timestamp": time.time()
                    })
            
            return conversation
            
        except Exception as e:
            logger.error(f"获取对话历史失败: {e}")
            return []
    
    def clear_memory(self):
        """清空对话记忆"""
        if self.memory:
            self.memory.clear()
            logger.info("对话记忆已清空")
    
    def change_persona(self, new_persona: str):
        """更换机器人角色"""
        try:
            self.persona = new_persona
            self.persona_config = get_persona_config(new_persona)
            
            # 重新设置对话链
            self.conversation_chain = self._setup_conversation_chain()
            
            logger.info(f"角色已更换为: {new_persona}")
            
        except Exception as e:
            logger.error(f"更换角色失败: {e}")
    
    def update_settings(self, **kwargs):
        """更新设置"""
        try:
            if "temperature" in kwargs:
                self.model_config["temperature"] = kwargs["temperature"]
            
            if "max_tokens" in kwargs:
                self.model_config["max_tokens"] = kwargs["max_tokens"]
            
            if "memory_length" in kwargs:
                self.memory_length = kwargs["memory_length"]
                # 重新设置记忆
                self.memory = self._setup_memory()
                self.conversation_chain = self._setup_conversation_chain()
            
            logger.info("设置已更新")
            
        except Exception as e:
            logger.error(f"更新设置失败: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        current_time = time.time()
        duration = current_time - self.stats["start_time"]
        
        return {
            **self.stats,
            "duration": duration,
            "messages_per_minute": self.stats["total_messages"] / (duration / 60) if duration > 0 else 0,
            "tokens_per_message": self.stats["total_tokens"] / self.stats["total_messages"] if self.stats["total_messages"] > 0 else 0
        }
    
    def export_conversation(self, format: str = "json") -> str:
        """导出对话记录"""
        conversation = self.get_conversation_history()
        
        if format == "json":
            import json
            return json.dumps(conversation, ensure_ascii=False, indent=2)
        
        elif format == "text":
            from utils import export_conversation_to_text
            return export_conversation_to_text(conversation)
        
        else:
            raise ValueError(f"不支持的导出格式: {format}")

# 工厂函数
def create_chatbot(persona: str = "assistant", **kwargs) -> ChatBot:
    """
    创建聊天机器人实例
    
    Args:
        persona: 机器人角色
        **kwargs: 其他配置参数
        
    Returns:
        ChatBot实例
    """
    return ChatBot(persona=persona, **kwargs)

# 导出主要类和函数
__all__ = [
    "ChatBot",
    "StreamingCallbackHandler", 
    "create_chatbot"
]