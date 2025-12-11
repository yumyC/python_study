"""
LangChain 记忆机制详解

本文件介绍 LangChain 中的各种记忆类型：
1. ConversationBufferMemory - 对话缓冲记忆
2. ConversationSummaryMemory - 对话摘要记忆
3. ConversationBufferWindowMemory - 滑动窗口记忆
4. ConversationSummaryBufferMemory - 摘要缓冲记忆
5. 自定义记忆

学习目标：
- 理解不同记忆类型的特点和适用场景
- 掌握记忆在对话系统中的应用
- 学会选择合适的记忆策略
"""

import os
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
    ConversationBufferWindowMemory,
    ConversationSummaryBufferMemory,
    ConversationKGMemory
)
from langchain.chains import ConversationChain
from langchain.prompts import PromptTemplate
from langchain.schema import BaseMemory
from typing import Dict, List, Any

def demo_buffer_memory():
    """演示对话缓冲记忆"""
    print("=== 对话缓冲记忆演示 ===")
    
    # 创建记忆实例
    memory = ConversationBufferMemory()
    
    # 手动添加对话历史
    memory.save_context(
        {"input": "你好，我是小明"},
        {"output": "你好小明！很高兴认识你。有什么可以帮助你的吗？"}
    )
    
    memory.save_context(
        {"input": "我想学习Python编程"},
        {"output": "太好了！Python是一门很棒的编程语言。你想从哪里开始学习呢？"}
    )
    
    # 查看记忆内容
    print("记忆变量:")
    print(memory.load_memory_variables({}))
    print()
    
    # 在对话链中使用
    if os.getenv("OPENAI_API_KEY"):
        llm = OpenAI(temperature=0.7)
        conversation = ConversationChain(
            llm=llm,
            memory=memory,
            verbose=True
        )
        
        # 继续对话
        response = conversation.predict(input="我应该先学什么？")
        print(f"AI回复: {response}")
    else:
        print("需要 API 密钥才能运行对话链演示")
    print()

def demo_summary_memory():
    """演示对话摘要记忆"""
    print("=== 对话摘要记忆演示 ===")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("需要 API 密钥才能运行摘要记忆演示")
        print("摘要记忆会使用 LLM 来总结对话历史")
        return
    
    llm = OpenAI(temperature=0)
    
    # 创建摘要记忆
    memory = ConversationSummaryMemory(llm=llm)
    
    # 添加一些对话历史
    conversation_history = [
        ("用户", "我想开一家咖啡店"),
        ("AI", "开咖啡店是个不错的想法！你需要考虑位置、资金、设备等因素。"),
        ("用户", "我预算大概50万，想开在市中心"),
        ("AI", "50万预算在市中心开咖啡店需要仔细规划。建议先做市场调研。"),
        ("用户", "市场调研应该包括什么内容？"),
        ("AI", "市场调研应该包括：目标客户分析、竞争对手调查、选址分析、价格策略等。")
    ]
    
    # 逐步添加对话
    for i in range(0, len(conversation_history), 2):
        if i + 1 < len(conversation_history):
            user_msg = conversation_history[i][1]
            ai_msg = conversation_history[i + 1][1]
            memory.save_context({"input": user_msg}, {"output": ai_msg})
    
    # 查看摘要
    print("对话摘要:")
    summary = memory.load_memory_variables({})
    print(summary["history"])
    print()

def demo_window_memory():
    """演示滑动窗口记忆"""
    print("=== 滑动窗口记忆演示 ===")
    
    # 创建窗口记忆（只保留最近2轮对话）
    memory = ConversationBufferWindowMemory(k=2)
    
    # 添加多轮对话
    conversations = [
        ("第一轮", "你好"),
        ("第一轮回复", "你好！"),
        ("第二轮", "今天天气怎么样？"),
        ("第二轮回复", "今天天气很好！"),
        ("第三轮", "推荐一本书"),
        ("第三轮回复", "我推荐《Python编程》"),
        ("第四轮", "这本书适合初学者吗？"),
        ("第四轮回复", "是的，很适合初学者")
    ]
    
    for i in range(0, len(conversations), 2):
        if i + 1 < len(conversations):
            memory.save_context(
                {"input": conversations[i][1]},
                {"output": conversations[i + 1][1]}
            )
            
            print(f"添加第{i//2 + 1}轮对话后的记忆:")
            print(memory.load_memory_variables({}))
            print("-" * 30)
    print()

def demo_summary_buffer_memory():
    """演示摘要缓冲记忆"""
    print("=== 摘要缓冲记忆演示 ===")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("需要 API 密钥才能运行摘要缓冲记忆演示")
        return
    
    llm = OpenAI(temperature=0)
    
    # 创建摘要缓冲记忆（当token数超过100时进行摘要）
    memory = ConversationSummaryBufferMemory(
        llm=llm,
        max_token_limit=100,
        return_messages=True
    )
    
    # 添加长对话
    long_conversations = [
        "我正在计划一次欧洲旅行，想去法国、意大利和西班牙。",
        "欧洲三国游是很棒的选择！建议行程安排：巴黎3天、罗马3天、巴塞罗那2天。需要考虑签证、交通、住宿等。",
        "签证方面需要注意什么？我是中国护照。",
        "中国护照需要申请申根签证。建议选择停留时间最长的国家作为主申请国，准备好行程单、酒店预订、机票等材料。",
        "交通方面，城市间怎么移动比较好？",
        "推荐火车出行：巴黎到罗马可坐夜火车，罗马到巴塞罗那可以飞机或火车+轮船组合。提前预订会有优惠。",
        "住宿有什么推荐吗？预算中等。",
        "中等预算建议选择3-4星酒店或精品民宿。巴黎推荐住在1-4区，罗马推荐中央车站附近，巴塞罗那推荐哥特区。"
    ]
    
    for i in range(0, len(long_conversations), 2):
        if i + 1 < len(long_conversations):
            memory.save_context(
                {"input": long_conversations[i]},
                {"output": long_conversations[i + 1]}
            )
    
    # 查看记忆状态
    print("摘要缓冲记忆内容:")
    memory_vars = memory.load_memory_variables({})
    print(memory_vars)
    print()

def demo_custom_memory():
    """演示自定义记忆"""
    print("=== 自定义记忆演示 ===")
    
    class KeywordMemory(BaseMemory):
        """自定义关键词记忆：只记住包含特定关键词的对话"""
        
        def __init__(self, keywords: List[str]):
            self.keywords = keywords
            self.memory_data = []
        
        @property
        def memory_variables(self) -> List[str]:
            return ["keyword_history"]
        
        def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, str]:
            # 返回包含关键词的对话历史
            relevant_history = []
            for entry in self.memory_data:
                if any(keyword in entry["input"].lower() or keyword in entry["output"].lower() 
                       for keyword in self.keywords):
                    relevant_history.append(f"用户: {entry['input']}\nAI: {entry['output']}")
            
            return {"keyword_history": "\n".join(relevant_history)}
        
        def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
            # 保存对话到记忆
            self.memory_data.append({
                "input": inputs["input"],
                "output": outputs["output"]
            })
        
        def clear(self) -> None:
            self.memory_data = []
    
    # 使用自定义记忆
    keywords = ["python", "编程", "代码"]
    custom_memory = KeywordMemory(keywords)
    
    # 添加各种对话
    test_conversations = [
        ("今天天气很好", "是的，适合出门"),
        ("我想学习Python编程", "Python是很好的选择"),
        ("推荐一家餐厅", "推荐XX餐厅，菜品不错"),
        ("如何写Python代码", "从基础语法开始学习"),
        ("明天有什么计划", "可以安排一些户外活动")
    ]
    
    for user_input, ai_output in test_conversations:
        custom_memory.save_context(
            {"input": user_input},
            {"output": ai_output}
        )
    
    # 查看关键词相关的记忆
    print("关键词记忆内容:")
    keyword_memory = custom_memory.load_memory_variables({})
    print(keyword_memory["keyword_history"])
    print()

def demo_memory_in_conversation():
    """演示记忆在实际对话中的应用"""
    print("=== 记忆在对话中的应用演示 ===")
    
    if not os.getenv("OPENAI_API_KEY"):
        print("需要 API 密钥才能运行对话演示")
        return
    
    llm = OpenAI(temperature=0.7)
    
    # 创建带记忆的对话链
    memory = ConversationBufferWindowMemory(k=3)  # 保留最近3轮对话
    
    conversation = ConversationChain(
        llm=llm,
        memory=memory,
        verbose=True
    )
    
    # 模拟多轮对话
    questions = [
        "我叫张三，是一名软件工程师",
        "我想学习机器学习",
        "你还记得我的名字吗？",
        "我的职业是什么？"
    ]
    
    print("开始多轮对话:")
    for i, question in enumerate(questions, 1):
        print(f"\n第{i}轮对话:")
        print(f"用户: {question}")
        response = conversation.predict(input=question)
        print(f"AI: {response}")
    print()

def demo_memory_comparison():
    """演示不同记忆类型的对比"""
    print("=== 记忆类型对比 ===")
    
    # 准备测试数据
    test_conversations = [
        ("我是学生", "很高兴认识你！"),
        ("我在学习AI", "AI是很有前景的领域"),
        ("推荐学习资源", "推荐《机器学习》这本书"),
        ("这本书难吗", "对初学者来说有一定难度"),
        ("有简单的吗", "可以先看《Python入门》")
    ]
    
    # 不同类型的记忆
    memories = {
        "缓冲记忆": ConversationBufferMemory(),
        "窗口记忆(k=2)": ConversationBufferWindowMemory(k=2),
    }
    
    # 添加对话到各种记忆
    for name, memory in memories.items():
        for user_msg, ai_msg in test_conversations:
            memory.save_context({"input": user_msg}, {"output": ai_msg})
        
        print(f"{name}的内容:")
        content = memory.load_memory_variables({})
        print(content["history"])
        print("-" * 40)
    print()

def main():
    """主函数"""
    print("LangChain 记忆机制学习")
    print("=" * 50)
    
    # 检查 API 密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  注意: 未检测到 OPENAI_API_KEY 环境变量")
        print("部分演示需要 API 密钥才能运行")
        print()
    
    # 运行演示
    demo_buffer_memory()
    demo_window_memory()
    demo_custom_memory()
    demo_memory_comparison()
    
    # 需要 API 的演示
    demo_summary_memory()
    demo_summary_buffer_memory()
    demo_memory_in_conversation()
    
    print("=" * 50)
    print("学习要点总结:")
    print("1. ConversationBufferMemory: 保存完整对话历史")
    print("2. ConversationSummaryMemory: 使用LLM总结历史")
    print("3. ConversationBufferWindowMemory: 滑动窗口保留最近对话")
    print("4. ConversationSummaryBufferMemory: 结合摘要和缓冲")
    print("5. 自定义记忆: 实现特定的记忆策略")
    print("6. 选择记忆类型要考虑：成本、性能、准确性")

if __name__ == "__main__":
    main()