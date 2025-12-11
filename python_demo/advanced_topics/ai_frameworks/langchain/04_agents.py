"""
LangChain 智能代理详解

本文件介绍 LangChain 中的智能代理系统：
1. Agent 基础概念
2. 工具 (Tools) 的使用
3. 不同类型的 Agent
4. 自定义工具和代理
5. 代理的实际应用

学习目标：
- 理解 Agent 的工作原理
- 掌握工具的创建和使用
- 学会构建智能代理系统
- 了解代理的应用场景
"""

import os
import json
import requests
from datetime import datetime
from typing import Optional, Type

from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.agents import (
    Tool, 
    AgentExecutor, 
    LLMSingleActionAgent,
    AgentOutputParser,
    initialize_agent,
    AgentType
)
from langchain.prompts import StringPromptTemplate
from langchain.tools import BaseTool
from langchain.schema import AgentAction, AgentFinish
from langchain.callbacks.manager import CallbackManagerForToolRun
import re

def demo_basic_tools():
    """演示基础工具使用"""
    print("=== 基础工具演示 ===")
    
    # 定义简单的工具函数
    def get_current_time(query: str) -> str:
        """获取当前时间"""
        now = datetime.now()
        return f"当前时间是: {now.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def calculate(expression: str) -> str:
        """简单计算器"""
        try:
            # 安全的数学表达式计算
            allowed_chars = set('0123456789+-*/.() ')
            if not all(c in allowed_chars for c in expression):
                return "错误：包含不允许的字符"
            
            result = eval(expression)
            return f"计算结果: {expression} = {result}"
        except Exception as e:
            return f"计算错误: {str(e)}"
    
    def get_weather(city: str) -> str:
        """模拟天气查询"""
        # 这里是模拟数据，实际应用中会调用真实的天气API
        weather_data = {
            "北京": "晴天，温度25°C",
            "上海": "多云，温度22°C", 
            "广州": "雨天，温度28°C",
            "深圳": "晴天，温度30°C"
        }
        return weather_data.get(city, f"抱歉，暂无{city}的天气信息")
    
    # 创建工具列表
    tools = [
        Tool(
            name="时间查询",
            func=get_current_time,
            description="获取当前的日期和时间"
        ),
        Tool(
            name="计算器",
            func=calculate,
            description="执行数学计算，输入数学表达式如：2+3*4"
        ),
        Tool(
            name="天气查询",
            func=get_weather,
            description="查询指定城市的天气情况，输入城市名称"
        )
    ]
    
    # 展示工具信息
    print("可用工具:")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
    
    # 测试工具
    print("\n工具测试:")
    print(tools[0].run(""))  # 时间查询
    print(tools[1].run("10 + 5 * 2"))  # 计算器
    print(tools[2].run("北京"))  # 天气查询
    print()

def demo_custom_tool():
    """演示自定义工具"""
    print("=== 自定义工具演示 ===")
    
    class TextAnalysisTool(BaseTool):
        """自定义文本分析工具"""
        name = "文本分析"
        description = "分析文本的基本统计信息，包括字数、句数等"
        
        def _run(
            self, 
            text: str, 
            run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> str:
            """执行文本分析"""
            if not text.strip():
                return "请提供要分析的文本"
            
            # 基本统计
            char_count = len(text)
            word_count = len(text.split())
            sentence_count = len([s for s in text.split('.') if s.strip()])
            
            # 简单的关键词提取（基于词频）
            words = text.lower().split()
            word_freq = {}
            for word in words:
                word = word.strip('.,!?;:"()[]')
                if len(word) > 2:  # 忽略太短的词
                    word_freq[word] = word_freq.get(word, 0) + 1
            
            # 获取最频繁的词
            top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:3]
            
            analysis = {
                "字符数": char_count,
                "词数": word_count,
                "句数": sentence_count,
                "高频词": [f"{word}({count}次)" for word, count in top_words]
            }
            
            return json.dumps(analysis, ensure_ascii=False, indent=2)
        
        async def _arun(
            self, 
            text: str, 
            run_manager: Optional[CallbackManagerForToolRun] = None
        ) -> str:
            """异步运行（这里简单调用同步版本）"""
            return self._run(text, run_manager)
    
    # 使用自定义工具
    text_tool = TextAnalysisTool()
    
    test_text = """
    人工智能是计算机科学的一个分支，它企图了解智能的实质，
    并生产出一种新的能以人类智能相似的方式做出反应的智能机器。
    该领域的研究包括机器人、语言识别、图像识别、自然语言处理和专家系统等。
    """
    
    result = text_tool.run(test_text.strip())
    print("文本分析结果:")
    print(result)
    print()

def demo_agent_with_tools():
    """演示带工具的代理"""
    print("=== 带工具的代理演示 ===")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("需要 API 密钥才能运行代理演示")
        return
    
    # 创建 LLM
    llm = OpenAI(temperature=0)
    
    # 定义工具
    def search_knowledge(query: str) -> str:
        """模拟知识搜索"""
        knowledge_base = {
            "python": "Python是一种高级编程语言，由Guido van Rossum创建，于1991年首次发布。",
            "机器学习": "机器学习是人工智能的一个分支，通过算法让计算机从数据中学习模式。",
            "深度学习": "深度学习是机器学习的子集，使用神经网络来模拟人脑的学习过程。",
            "langchain": "LangChain是一个用于构建基于大语言模型应用的框架。"
        }
        
        # 简单的关键词匹配
        for key, value in knowledge_base.items():
            if key.lower() in query.lower():
                return value
        
        return f"抱歉，没有找到关于'{query}'的相关信息。"
    
    def get_random_fact() -> str:
        """获取随机事实"""
        facts = [
            "蜂鸟是唯一能够向后飞行的鸟类。",
            "章鱼有三个心脏和蓝色的血液。",
            "香蕉实际上是浆果，而草莓不是。",
            "一只蓝鲸的心脏重达400磅。"
        ]
        import random
        return random.choice(facts)
    
    # 创建工具列表
    tools = [
        Tool(
            name="知识搜索",
            func=search_knowledge,
            description="搜索编程和技术相关的知识，输入关键词"
        ),
        Tool(
            name="随机事实",
            func=lambda x: get_random_fact(),
            description="获取一个有趣的随机事实"
        ),
        Tool(
            name="计算器",
            func=lambda expr: str(eval(expr)) if all(c in '0123456789+-*/.() ' for c in expr) else "无效表达式",
            description="执行数学计算"
        )
    ]
    
    # 初始化代理
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        max_iterations=3
    )
    
    # 测试代理
    test_queries = [
        "什么是Python？",
        "计算 15 * 8 + 12",
        "告诉我一个有趣的事实"
    ]
    
    for query in test_queries:
        print(f"\n用户问题: {query}")
        try:
            response = agent.run(query)
            print(f"代理回答: {response}")
        except Exception as e:
            print(f"处理出错: {e}")
        print("-" * 50)

def demo_custom_agent():
    """演示自定义代理"""
    print("=== 自定义代理演示 ===")
    
    # 自定义提示模板
    template = """
    你是一个智能助手，可以使用以下工具来回答问题：

    {tools}

    使用以下格式：

    问题：用户的输入问题
    思考：我需要做什么？
    行动：要使用的工具名称，必须是 [{tool_names}] 中的一个
    行动输入：工具的输入
    观察：工具的输出结果
    ... (这个思考/行动/行动输入/观察的过程可以重复N次)
    思考：我现在知道最终答案了
    最终答案：对原始输入问题的最终答案

    开始！

    问题：{input}
    思考：{agent_scratchpad}
    """
    
    class CustomPromptTemplate(StringPromptTemplate):
        template: str
        tools: list
        
        def format(self, **kwargs) -> str:
            # 获取中间步骤（agent_scratchpad）
            intermediate_steps = kwargs.pop("intermediate_steps")
            thoughts = ""
            for action, observation in intermediate_steps:
                thoughts += action.log
                thoughts += f"\n观察：{observation}\n思考："
            
            # 设置agent_scratchpad变量
            kwargs["agent_scratchpad"] = thoughts
            
            # 创建工具列表
            kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
            kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
            
            return self.template.format(**kwargs)
    
    class CustomOutputParser(AgentOutputParser):
        def parse(self, llm_output: str) -> AgentAction | AgentFinish:
            # 检查是否包含最终答案
            if "最终答案：" in llm_output:
                return AgentFinish(
                    return_values={"output": llm_output.split("最终答案：")[-1].strip()},
                    log=llm_output,
                )
            
            # 解析行动
            regex = r"行动：(.*?)\n行动输入：(.*)"
            match = re.search(regex, llm_output, re.DOTALL)
            if not match:
                raise ValueError(f"无法解析LLM输出：`{llm_output}`")
            
            action = match.group(1).strip()
            action_input = match.group(2)
            
            return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)
    
    # 这里只演示自定义代理的结构，不实际运行
    print("自定义代理组件:")
    print("1. 自定义提示模板 - 定义代理的思考格式")
    print("2. 自定义输出解析器 - 解析LLM的输出")
    print("3. 工具集合 - 代理可以使用的工具")
    print("4. LLM - 驱动代理思考的语言模型")
    print()
    
    # 展示提示模板示例
    tools = [
        Tool(name="搜索", func=lambda x: x, description="搜索信息"),
        Tool(name="计算", func=lambda x: x, description="数学计算")
    ]
    
    prompt = CustomPromptTemplate(
        template=template,
        tools=tools,
        input_variables=["input", "intermediate_steps"]
    )
    
    example_prompt = prompt.format(
        input="什么是2+2？",
        intermediate_steps=[]
    )
    
    print("提示模板示例:")
    print(example_prompt)

def demo_agent_memory():
    """演示带记忆的代理"""
    print("=== 带记忆的代理演示 ===")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("需要 API 密钥才能运行记忆代理演示")
        return
    
    from langchain.memory import ConversationBufferMemory
    
    # 创建记忆
    memory = ConversationBufferMemory(memory_key="chat_history")
    
    # 简单工具
    def personal_info_tool(query: str) -> str:
        """个人信息工具"""
        info_db = {}  # 简单的信息存储
        
        if "记住" in query:
            # 提取要记住的信息
            parts = query.split("记住")
            if len(parts) > 1:
                info = parts[1].strip()
                info_db["user_info"] = info
                return f"已记住：{info}"
        
        if "我是谁" in query or "我的信息" in query:
            return info_db.get("user_info", "我还不知道你的信息")
        
        return "请告诉我要记住什么信息，或询问你的信息"
    
    tools = [
        Tool(
            name="个人信息",
            func=personal_info_tool,
            description="记住和查询个人信息"
        )
    ]
    
    # 创建带记忆的代理
    llm = OpenAI(temperature=0)
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True
    )
    
    # 模拟对话
    conversations = [
        "记住我叫张三，是程序员",
        "我是谁？",
        "我的职业是什么？"
    ]
    
    for conv in conversations:
        print(f"\n用户: {conv}")
        try:
            response = agent.run(conv)
            print(f"代理: {response}")
        except Exception as e:
            print(f"处理出错: {e}")

def main():
    """主函数"""
    print("LangChain 智能代理学习")
    print("=" * 50)
    
    # 检查 API 密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  注意: 未检测到 OPENAI_API_KEY 环境变量")
        print("部分演示需要 API 密钥才能运行")
        print()
    
    # 运行演示
    demo_basic_tools()
    demo_custom_tool()
    demo_custom_agent()
    
    # 需要 API 的演示
    demo_agent_with_tools()
    demo_agent_memory()
    
    print("=" * 50)
    print("学习要点总结:")
    print("1. 工具(Tools)是代理与外部世界交互的接口")
    print("2. 代理(Agent)使用LLM来决定使用哪些工具")
    print("3. 可以创建自定义工具来扩展代理能力")
    print("4. 代理可以结合记忆实现上下文感知")
    print("5. 不同类型的代理适用于不同场景")
    print("6. 代理是构建复杂AI应用的重要组件")

if __name__ == "__main__":
    main()