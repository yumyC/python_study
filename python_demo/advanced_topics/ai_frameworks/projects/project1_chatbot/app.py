"""
智能聊天机器人 Streamlit 应用

基于 LangChain 和 Streamlit 的智能聊天机器人界面
"""

import streamlit as st
import time
import json
from datetime import datetime
from typing import List, Dict, Any

# 导入项目模块
from config import (
    APP_CONFIG, 
    get_available_personas, 
    CONVERSATION_SETTINGS,
    FEATURES,
    validate_config
)
from utils import (
    create_directories,
    generate_session_id,
    save_conversation,
    load_conversation,
    export_conversation_to_text,
    get_conversation_stats,
    format_duration,
    rate_limit_check,
    log_user_interaction
)
from chatbot import create_chatbot, LANGCHAIN_AVAILABLE

# 页面配置
st.set_page_config(
    page_title=APP_CONFIG["title"],
    page_icon=APP_CONFIG["page_icon"],
    layout=APP_CONFIG["layout"],
    initial_sidebar_state=APP_CONFIG["initial_sidebar_state"]
)

def initialize_app():
    """初始化应用"""
    # 创建必要目录
    create_directories()
    
    # 验证配置
    if not validate_config():
        st.error("配置验证失败，请检查环境变量设置")
        st.stop()
    
    # 初始化 session state
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.session_id = generate_session_id()
        st.session_state.conversation = []
        st.session_state.chatbot = None
        st.session_state.current_persona = "assistant"
        
        # 记录应用启动
        log_user_interaction("app_start")

def setup_sidebar():
    """设置侧边栏"""
    with st.sidebar:
        st.title("🤖 聊天设置")
        
        # 角色选择
        st.subheader("机器人角色")
        personas = get_available_personas()
        
        selected_persona = st.selectbox(
            "选择角色",
            options=list(personas.keys()),
            format_func=lambda x: personas[x],
            index=list(personas.keys()).index(st.session_state.current_persona),
            key="persona_selector"
        )
        
        # 检查角色是否改变
        if selected_persona != st.session_state.current_persona:
            st.session_state.current_persona = selected_persona
            if st.session_state.chatbot:
                st.session_state.chatbot.change_persona(selected_persona)
            st.rerun()
        
        # 对话参数设置
        st.subheader("对话参数")
        
        temperature = st.slider(
            "创造性",
            min_value=CONVERSATION_SETTINGS["temperature"]["min"],
            max_value=CONVERSATION_SETTINGS["temperature"]["max"],
            value=CONVERSATION_SETTINGS["temperature"]["default"],
            step=CONVERSATION_SETTINGS["temperature"]["step"],
            help=CONVERSATION_SETTINGS["temperature"]["help"],
            key="temperature_slider"
        )
        
        max_tokens = st.slider(
            "回复长度",
            min_value=CONVERSATION_SETTINGS["max_tokens"]["min"],
            max_value=CONVERSATION_SETTINGS["max_tokens"]["max"],
            value=CONVERSATION_SETTINGS["max_tokens"]["default"],
            step=CONVERSATION_SETTINGS["max_tokens"]["step"],
            help=CONVERSATION_SETTINGS["max_tokens"]["help"],
            key="max_tokens_slider"
        )
        
        memory_length = st.slider(
            "记忆长度",
            min_value=CONVERSATION_SETTINGS["memory_length"]["min"],
            max_value=CONVERSATION_SETTINGS["memory_length"]["max"],
            value=CONVERSATION_SETTINGS["memory_length"]["default"],
            step=CONVERSATION_SETTINGS["memory_length"]["step"],
            help=CONVERSATION_SETTINGS["memory_length"]["help"],
            key="memory_length_slider"
        )
        
        # 更新聊天机器人设置
        if st.session_state.chatbot:
            st.session_state.chatbot.update_settings(
                temperature=temperature,
                max_tokens=max_tokens,
                memory_length=memory_length
            )
        
        st.divider()
        
        # 对话管理
        st.subheader("对话管理")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🗑️ 清空对话", use_container_width=True):
                clear_conversation()
        
        with col2:
            if st.button("💾 保存对话", use_container_width=True):
                save_current_conversation()
        
        # 导出对话
        if st.session_state.conversation and FEATURES["enable_export"]:
            st.subheader("导出对话")
            
            export_format = st.selectbox(
                "导出格式",
                ["文本", "JSON"],
                key="export_format"
            )
            
            if st.button("📥 导出", use_container_width=True):
                export_conversation(export_format)
        
        # 统计信息
        if st.session_state.conversation:
            st.subheader("对话统计")
            show_conversation_stats()

def clear_conversation():
    """清空对话"""
    st.session_state.conversation = []
    if st.session_state.chatbot:
        st.session_state.chatbot.clear_memory()
    
    log_user_interaction("conversation_cleared")
    st.success("对话已清空")
    st.rerun()

def save_current_conversation():
    """保存当前对话"""
    if not st.session_state.conversation:
        st.warning("没有对话内容可保存")
        return
    
    success = save_conversation(
        st.session_state.session_id,
        st.session_state.conversation
    )
    
    if success:
        log_user_interaction("conversation_saved")
        st.success("对话已保存")
    else:
        st.error("保存失败")

def export_conversation(format_type: str):
    """导出对话"""
    if not st.session_state.conversation:
        st.warning("没有对话内容可导出")
        return
    
    try:
        if format_type == "文本":
            content = export_conversation_to_text(st.session_state.conversation)
            filename = f"conversation_{st.session_state.session_id}.txt"
            mime_type = "text/plain"
        else:  # JSON
            content = json.dumps(st.session_state.conversation, ensure_ascii=False, indent=2)
            filename = f"conversation_{st.session_state.session_id}.json"
            mime_type = "application/json"
        
        st.download_button(
            label=f"下载 {format_type} 文件",
            data=content,
            file_name=filename,
            mime=mime_type,
            use_container_width=True
        )
        
        log_user_interaction("conversation_exported", {"format": format_type})
        
    except Exception as e:
        st.error(f"导出失败: {e}")

def show_conversation_stats():
    """显示对话统计"""
    stats = get_conversation_stats(st.session_state.conversation)
    
    st.metric("消息总数", stats["total_messages"])
    st.metric("用户消息", stats["user_messages"])
    st.metric("助手回复", stats["assistant_messages"])
    
    if stats["conversation_duration"] > 0:
        st.metric("对话时长", format_duration(stats["conversation_duration"]))
    
    if stats["total_characters"] > 0:
        st.metric("平均消息长度", f"{stats['average_message_length']:.0f} 字符")

def initialize_chatbot():
    """初始化聊天机器人"""
    if not LANGCHAIN_AVAILABLE:
        st.error("LangChain 未安装，请先安装依赖包")
        st.code("pip install langchain openai")
        st.stop()
    
    try:
        if st.session_state.chatbot is None:
            with st.spinner("正在初始化聊天机器人..."):
                st.session_state.chatbot = create_chatbot(
                    persona=st.session_state.current_persona,
                    memory_length=CONVERSATION_SETTINGS["memory_length"]["default"],
                    temperature=CONVERSATION_SETTINGS["temperature"]["default"],
                    max_tokens=CONVERSATION_SETTINGS["max_tokens"]["default"]
                )
            
            log_user_interaction("chatbot_initialized", {
                "persona": st.session_state.current_persona
            })
    
    except Exception as e:
        st.error(f"聊天机器人初始化失败: {e}")
        st.info("请检查 API 密钥配置或网络连接")

def display_conversation():
    """显示对话历史"""
    if not st.session_state.conversation:
        st.info("👋 欢迎使用智能聊天机器人！请在下方输入您的问题开始对话。")
        return
    
    # 创建对话容器
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.conversation:
            role = message["role"]
            content = message["content"]
            timestamp = message.get("timestamp")
            
            if role == "user":
                with st.chat_message("user", avatar="👤"):
                    st.write(content)
                    if timestamp:
                        st.caption(f"发送于 {datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')}")
            
            else:  # assistant
                with st.chat_message("assistant", avatar="🤖"):
                    st.write(content)
                    if timestamp:
                        st.caption(f"回复于 {datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')}")

def handle_user_input():
    """处理用户输入"""
    # 检查速率限制
    if not rate_limit_check(st.session_state.session_id):
        st.error("请求过于频繁，请稍后再试")
        return
    
    # 用户输入
    user_input = st.chat_input("请输入您的问题...")
    
    if user_input:
        # 添加用户消息到对话历史
        user_message = {
            "role": "user",
            "content": user_input,
            "timestamp": time.time()
        }
        st.session_state.conversation.append(user_message)
        
        # 显示用户消息
        with st.chat_message("user", avatar="👤"):
            st.write(user_input)
        
        # 生成助手回复
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner("正在思考..."):
                try:
                    response = st.session_state.chatbot.chat(user_input)
                    
                    # 添加助手回复到对话历史
                    assistant_message = {
                        "role": "assistant",
                        "content": response,
                        "timestamp": time.time()
                    }
                    st.session_state.conversation.append(assistant_message)
                    
                    # 显示回复
                    st.write(response)
                    
                    # 记录成功的对话
                    log_user_interaction("successful_chat", {
                        "user_message_length": len(user_input),
                        "assistant_response_length": len(response)
                    })
                
                except Exception as e:
                    error_message = f"抱歉，我遇到了一些问题: {str(e)}"
                    st.error(error_message)
                    
                    # 记录错误
                    log_user_interaction("chat_error", {"error": str(e)})
        
        # 自动保存对话
        if len(st.session_state.conversation) % 10 == 0:  # 每10条消息自动保存
            save_current_conversation()
        
        # 刷新页面以显示新消息
        st.rerun()

def show_help():
    """显示帮助信息"""
    with st.expander("📖 使用帮助"):
        st.markdown("""
        ### 如何使用聊天机器人
        
        1. **选择角色**: 在左侧边栏选择不同的机器人角色
        2. **调整参数**: 根据需要调整创造性、回复长度等参数
        3. **开始对话**: 在底部输入框中输入问题并发送
        4. **管理对话**: 使用侧边栏的功能保存、清空或导出对话
        
        ### 机器人角色说明
        
        - **🤖 智能助手**: 专业、有帮助的AI助手
        - **😊 友好伙伴**: 轻松、友好的聊天伙伴  
        - **🎓 专业专家**: 某个领域的专业专家
        - **🎨 创意大师**: 富有创意和想象力的助手
        - **👨‍🏫 耐心老师**: 耐心的教学助手
        
        ### 参数说明
        
        - **创造性**: 控制回复的随机性和创造性
        - **回复长度**: 限制回复的最大长度
        - **记忆长度**: 机器人记住的对话轮数
        
        ### 注意事项
        
        - 请确保已正确配置 OpenAI API 密钥
        - 避免发送过于频繁的请求
        - 对话内容会自动保存，可随时导出
        """)

def show_footer():
    """显示页脚信息"""
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.caption("🤖 智能聊天机器人")
    
    with col2:
        st.caption(f"会话ID: {st.session_state.session_id[:8]}...")
    
    with col3:
        if st.session_state.chatbot:
            stats = st.session_state.chatbot.get_stats()
            st.caption(f"消息数: {stats['total_messages']}")

def main():
    """主函数"""
    # 初始化应用
    initialize_app()
    
    # 页面标题
    st.title(APP_CONFIG["title"])
    st.markdown("基于 LangChain 的智能聊天机器人，支持多种角色和个性化设置")
    
    # 设置侧边栏
    setup_sidebar()
    
    # 初始化聊天机器人
    initialize_chatbot()
    
    # 显示帮助信息
    show_help()
    
    # 显示对话历史
    display_conversation()
    
    # 处理用户输入
    handle_user_input()
    
    # 显示页脚
    show_footer()
    
    # 用户反馈（如果启用）
    if FEATURES["enable_feedback"] and st.session_state.conversation:
        with st.expander("💬 反馈"):
            feedback = st.text_area("您对聊天机器人的使用体验如何？有什么建议吗？")
            if st.button("提交反馈"):
                if feedback.strip():
                    log_user_interaction("user_feedback", {"feedback": feedback})
                    st.success("感谢您的反馈！")
                else:
                    st.warning("请输入反馈内容")

if __name__ == "__main__":
    main()