"""
LangChain 基础概念和组件

本文件介绍 LangChain 的核心概念，包括：
1. LLM (Large Language Model) - 大语言模型
2. Prompt Templates - 提示模板
3. Chains - 链式调用
4. 基础使用示例

学习目标：
- 理解 LangChain 的基本架构
- 掌握核心组件的使用方法
- 能够构建简单的 AI 应用

注意：运行此代码需要设置 OPENAI_API_KEY 环境变量
"""

import os
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate
from langchain.chains import LLMChain
from langchain.schema import HumanMessage, SystemMessage

# 设置 API 密钥（请替换为你的实际密钥）
# os.environ["OPENAI_API_KEY"] = "your-api-key-here"

def demo_basic_llm():
    """演示基础 LLM 使用"""
    print("=== 基础 LLM 演示 ===")
    
    # 创建 LLM 实例
    llm = OpenAI(
        temperature=0.7,  # 控制输出的随机性，0-1之间
        max_tokens=100    # 最大输出长度
    )
    
    # 直接调用
    prompt = "请用一句话解释什么是人工智能"
    response = llm(prompt)
    print(f"问题: {prompt}")
    print(f"回答: {response.strip()}")
    print()

def demo_chat_model():
    """演示聊天模型使用"""
    print("=== 聊天模型演示 ===")
    
    # 创建聊天模型实例
    chat = ChatOpenAI(
        temperature=0.5,
        model_name="gpt-3.5-turbo"
    )
    
    # 构建消息列表
    messages = [
        SystemMessage(content="你是一个友善的AI助手，专门帮助用户学习编程。"),
        HumanMessage(content="请解释Python中的装饰器是什么？")
    ]
    
    response = chat(messages)
    print("系统角色: 友善的AI助手")
    print("用户问题: 请解释Python中的装饰器是什么？")
    print(f"AI回答: {response.content}")
    print()

def demo_prompt_template():
    """演示提示模板使用"""
    print("=== 提示模板演示 ===")
    
    # 创建提示模板
    template = """
    你是一个{role}，请用{style}的方式回答以下问题：
    
    问题：{question}
    
    请确保回答：
    1. 准确且有用
    2. 符合{role}的身份
    3. 使用{style}的语言风格
    """
    
    prompt = PromptTemplate(
        input_variables=["role", "style", "question"],
        template=template
    )
    
    # 格式化提示
    formatted_prompt = prompt.format(
        role="Python编程专家",
        style="简洁明了",
        question="如何优化Python代码的性能？"
    )
    
    print("提示模板:")
    print(formatted_prompt)
    print()

def demo_llm_chain():
    """演示 LLM 链使用"""
    print("=== LLM 链演示 ===")
    
    # 创建 LLM
    llm = OpenAI(temperature=0.6)
    
    # 创建提示模板
    prompt = PromptTemplate(
        input_variables=["topic", "audience"],
        template="请为{audience}解释{topic}，要求通俗易懂，不超过100字。"
    )
    
    # 创建链
    chain = LLMChain(llm=llm, prompt=prompt)
    
    # 运行链
    result = chain.run(
        topic="机器学习",
        audience="初学者"
    )
    
    print("链式调用结果:")
    print(f"主题: 机器学习")
    print(f"受众: 初学者")
    print(f"解释: {result.strip()}")
    print()

def demo_multiple_chains():
    """演示多个链的组合使用"""
    print("=== 多链组合演示 ===")
    
    llm = OpenAI(temperature=0.7)
    
    # 第一个链：生成创意
    idea_prompt = PromptTemplate(
        input_variables=["domain"],
        template="为{domain}领域想一个创新的应用想法，一句话描述。"
    )
    idea_chain = LLMChain(llm=llm, prompt=idea_prompt)
    
    # 第二个链：分析可行性
    analysis_prompt = PromptTemplate(
        input_variables=["idea"],
        template="分析这个想法的可行性：{idea}\n请从技术、市场、资源三个角度简要分析。"
    )
    analysis_chain = LLMChain(llm=llm, prompt=analysis_prompt)
    
    # 执行链式调用
    domain = "教育科技"
    idea = idea_chain.run(domain=domain)
    analysis = analysis_chain.run(idea=idea)
    
    print(f"领域: {domain}")
    print(f"创意: {idea.strip()}")
    print(f"可行性分析: {analysis.strip()}")
    print()

def demo_chat_prompt_template():
    """演示聊天提示模板"""
    print("=== 聊天提示模板演示 ===")
    
    # 创建聊天提示模板
    chat_prompt = ChatPromptTemplate.from_messages([
        ("system", "你是一个{expertise}专家，擅长{skill}。"),
        ("human", "请帮我{task}：{content}")
    ])
    
    # 格式化消息
    messages = chat_prompt.format_messages(
        expertise="数据科学",
        skill="数据分析和可视化",
        task="分析",
        content="用户行为数据，找出关键洞察"
    )
    
    print("聊天消息模板:")
    for message in messages:
        print(f"{message.__class__.__name__}: {message.content}")
    print()

def demo_error_handling():
    """演示错误处理"""
    print("=== 错误处理演示 ===")
    
    try:
        # 模拟没有设置 API 密钥的情况
        if not os.getenv("OPENAI_API_KEY"):
            print("警告: 未设置 OPENAI_API_KEY 环境变量")
            print("请设置后再运行实际的 LLM 调用")
            return
        
        llm = OpenAI(temperature=0.5)
        result = llm("测试连接")
        print(f"连接成功: {result.strip()}")
        
    except Exception as e:
        print(f"发生错误: {type(e).__name__}: {e}")
        print("请检查:")
        print("1. API 密钥是否正确设置")
        print("2. 网络连接是否正常")
        print("3. API 配额是否充足")
    print()

def main():
    """主函数：运行所有演示"""
    print("LangChain 基础概念学习")
    print("=" * 50)
    
    # 检查 API 密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  注意: 未检测到 OPENAI_API_KEY 环境变量")
        print("请设置你的 OpenAI API 密钥后再运行实际调用")
        print("设置方法: export OPENAI_API_KEY='your-key-here'")
        print()
    
    # 运行演示（不需要 API 的部分）
    demo_prompt_template()
    demo_chat_prompt_template()
    demo_error_handling()
    
    # 如果有 API 密钥，运行需要 API 的演示
    if os.getenv("OPENAI_API_KEY"):
        demo_basic_llm()
        demo_chat_model()
        demo_llm_chain()
        demo_multiple_chains()
    else:
        print("跳过需要 API 密钥的演示...")
    
    print("=" * 50)
    print("学习要点总结:")
    print("1. LLM 是 LangChain 的核心组件")
    print("2. PromptTemplate 帮助构建结构化提示")
    print("3. LLMChain 将 LLM 和提示模板组合")
    print("4. 可以通过链式调用构建复杂应用")
    print("5. 错误处理对生产应用很重要")

if __name__ == "__main__":
    main()