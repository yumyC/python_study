"""
LangChain 链式调用详解

本文件深入介绍 LangChain 中的各种链类型：
1. LLMChain - 基础链
2. SequentialChain - 顺序链
3. RouterChain - 路由链
4. TransformChain - 转换链
5. 自定义链

学习目标：
- 掌握不同类型链的使用场景
- 学会构建复杂的链式工作流
- 理解链的组合和嵌套
"""

import os
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import (
    LLMChain, 
    SequentialChain, 
    SimpleSequentialChain,
    RouterChain,
    MultiPromptChain,
    TransformChain
)
from langchain.chains.router import MultiRouteChain
from langchain.chains.router.llm_router import LLMRouterChain, RouterOutputParser
from langchain.chains.router.multi_prompt_prompt import MULTI_PROMPT_ROUTER_TEMPLATE

def demo_simple_sequential_chain():
    """演示简单顺序链"""
    print("=== 简单顺序链演示 ===")
    
    llm = OpenAI(temperature=0.7)
    
    # 第一个链：生成故事大纲
    outline_prompt = PromptTemplate(
        input_variables=["theme"],
        template="为主题'{theme}'写一个简短的故事大纲，不超过50字。"
    )
    outline_chain = LLMChain(llm=llm, prompt=outline_prompt)
    
    # 第二个链：扩展故事
    story_prompt = PromptTemplate(
        input_variables=["outline"],
        template="基于这个大纲写一个完整的短故事：{outline}"
    )
    story_chain = LLMChain(llm=llm, prompt=story_prompt)
    
    # 创建简单顺序链
    overall_chain = SimpleSequentialChain(
        chains=[outline_chain, story_chain],
        verbose=True  # 显示中间步骤
    )
    
    if os.getenv("OPENAI_API_KEY"):
        result = overall_chain.run("友谊")
        print(f"最终故事:\n{result}")
    else:
        print("需要 API 密钥才能运行此演示")
    print()

def demo_sequential_chain():
    """演示复杂顺序链"""
    print("=== 复杂顺序链演示 ===")
    
    llm = OpenAI(temperature=0.6)
    
    # 第一个链：分析产品需求
    analysis_prompt = PromptTemplate(
        input_variables=["product_idea"],
        template="分析这个产品想法：{product_idea}\n输出目标用户群体（一句话）。"
    )
    analysis_chain = LLMChain(
        llm=llm, 
        prompt=analysis_prompt, 
        output_key="target_users"
    )
    
    # 第二个链：设计功能
    features_prompt = PromptTemplate(
        input_variables=["product_idea", "target_users"],
        template="""
        产品想法：{product_idea}
        目标用户：{target_users}
        
        列出3个核心功能（每个功能一行）。
        """
    )
    features_chain = LLMChain(
        llm=llm, 
        prompt=features_prompt, 
        output_key="features"
    )
    
    # 第三个链：制定营销策略
    marketing_prompt = PromptTemplate(
        input_variables=["product_idea", "target_users", "features"],
        template="""
        产品：{product_idea}
        用户：{target_users}
        功能：{features}
        
        制定一个简单的营销策略（2-3句话）。
        """
    )
    marketing_chain = LLMChain(
        llm=llm, 
        prompt=marketing_prompt, 
        output_key="marketing_strategy"
    )
    
    # 创建顺序链
    overall_chain = SequentialChain(
        chains=[analysis_chain, features_chain, marketing_chain],
        input_variables=["product_idea"],
        output_variables=["target_users", "features", "marketing_strategy"],
        verbose=True
    )
    
    if os.getenv("OPENAI_API_KEY"):
        result = overall_chain({
            "product_idea": "一个帮助程序员学习新技术的AI助手应用"
        })
        
        print("产品分析结果:")
        print(f"目标用户: {result['target_users']}")
        print(f"核心功能: {result['features']}")
        print(f"营销策略: {result['marketing_strategy']}")
    else:
        print("需要 API 密钥才能运行此演示")
    print()

def demo_router_chain():
    """演示路由链"""
    print("=== 路由链演示 ===")
    
    llm = OpenAI(temperature=0.5)
    
    # 定义不同的专业领域提示
    physics_template = """
    你是一个物理学专家。请回答以下物理问题：
    {input}
    
    请用科学准确的语言回答。
    """
    
    math_template = """
    你是一个数学专家。请解答以下数学问题：
    {input}
    
    请提供详细的解题步骤。
    """
    
    programming_template = """
    你是一个编程专家。请回答以下编程问题：
    {input}
    
    请提供代码示例和解释。
    """
    
    # 创建提示信息
    prompt_infos = [
        {
            "name": "physics",
            "description": "适合回答物理学相关问题",
            "prompt_template": physics_template
        },
        {
            "name": "math", 
            "description": "适合回答数学相关问题",
            "prompt_template": math_template
        },
        {
            "name": "programming",
            "description": "适合回答编程相关问题", 
            "prompt_template": programming_template
        }
    ]
    
    # 创建目标链
    destination_chains = {}
    for p_info in prompt_infos:
        name = p_info["name"]
        prompt_template = p_info["prompt_template"]
        prompt = PromptTemplate(template=prompt_template, input_variables=["input"])
        chain = LLMChain(llm=llm, prompt=prompt)
        destination_chains[name] = chain
    
    # 默认链
    default_prompt = PromptTemplate(
        template="请回答以下问题：{input}",
        input_variables=["input"]
    )
    default_chain = LLMChain(llm=llm, prompt=default_prompt)
    
    # 创建多提示链
    chain = MultiPromptChain(
        router_chain=LLMRouterChain.from_llm(llm, MULTI_PROMPT_ROUTER_TEMPLATE, prompt_infos),
        destination_chains=destination_chains,
        default_chain=default_chain,
        verbose=True
    )
    
    # 测试不同类型的问题
    test_questions = [
        "什么是牛顿第二定律？",
        "如何计算圆的面积？",
        "Python中如何创建一个类？",
        "今天天气怎么样？"  # 这个会路由到默认链
    ]
    
    if os.getenv("OPENAI_API_KEY"):
        for question in test_questions:
            print(f"问题: {question}")
            try:
                result = chain.run(question)
                print(f"回答: {result.strip()}")
            except Exception as e:
                print(f"处理出错: {e}")
            print("-" * 40)
    else:
        print("需要 API 密钥才能运行此演示")
    print()

def demo_transform_chain():
    """演示转换链"""
    print("=== 转换链演示 ===")
    
    def transform_func(inputs: dict) -> dict:
        """文本预处理函数"""
        text = inputs["text"]
        
        # 清理文本
        cleaned_text = text.strip().lower()
        
        # 统计信息
        word_count = len(cleaned_text.split())
        char_count = len(cleaned_text)
        
        return {
            "cleaned_text": cleaned_text,
            "word_count": word_count,
            "char_count": char_count,
            "summary": f"文本包含 {word_count} 个单词，{char_count} 个字符"
        }
    
    # 创建转换链
    transform_chain = TransformChain(
        input_variables=["text"],
        output_variables=["cleaned_text", "word_count", "char_count", "summary"],
        transform=transform_func
    )
    
    # 测试转换链
    test_text = "  Hello World! This is a TEST of the Transform Chain.  "
    result = transform_chain.run(text=test_text)
    
    print(f"原始文本: '{test_text}'")
    print(f"处理结果: {result}")
    print()

def demo_custom_chain():
    """演示自定义链"""
    print("=== 自定义链演示 ===")
    
    from langchain.chains.base import Chain
    from typing import Dict, List
    
    class TextAnalysisChain(Chain):
        """自定义文本分析链"""
        
        @property
        def input_keys(self) -> List[str]:
            return ["text"]
        
        @property
        def output_keys(self) -> List[str]:
            return ["analysis"]
        
        def _call(self, inputs: Dict[str, str]) -> Dict[str, str]:
            text = inputs["text"]
            
            # 执行文本分析
            words = text.split()
            sentences = text.split('.')
            
            # 简单的情感分析（基于关键词）
            positive_words = ["好", "棒", "优秀", "amazing", "great", "excellent"]
            negative_words = ["坏", "差", "糟糕", "bad", "terrible", "awful"]
            
            positive_count = sum(1 for word in words if word.lower() in positive_words)
            negative_count = sum(1 for word in words if word.lower() in negative_words)
            
            if positive_count > negative_count:
                sentiment = "积极"
            elif negative_count > positive_count:
                sentiment = "消极"
            else:
                sentiment = "中性"
            
            analysis = {
                "word_count": len(words),
                "sentence_count": len([s for s in sentences if s.strip()]),
                "sentiment": sentiment,
                "positive_words": positive_count,
                "negative_words": negative_count
            }
            
            return {"analysis": str(analysis)}
    
    # 使用自定义链
    custom_chain = TextAnalysisChain()
    
    test_texts = [
        "这是一个很棒的产品，我觉得非常优秀！",
        "This is a terrible experience. Very bad service.",
        "今天天气不错，适合出门散步。"
    ]
    
    for text in test_texts:
        result = custom_chain.run(text=text)
        print(f"文本: {text}")
        print(f"分析: {result}")
        print("-" * 40)
    print()

def demo_chain_composition():
    """演示链的组合使用"""
    print("=== 链组合演示 ===")
    
    # 组合转换链和自定义链
    def preprocess_text(inputs: dict) -> dict:
        text = inputs["raw_text"]
        # 简单的预处理
        processed = text.strip().replace('\n', ' ')
        return {"text": processed}
    
    preprocess_chain = TransformChain(
        input_variables=["raw_text"],
        output_variables=["text"],
        transform=preprocess_text
    )
    
    # 如果有自定义链，可以组合使用
    # 这里演示概念
    print("链组合的概念:")
    print("1. 预处理链 -> 清理文本")
    print("2. 分析链 -> 提取特征")
    print("3. LLM链 -> 生成总结")
    print("4. 后处理链 -> 格式化输出")
    
    raw_text = "  这是一段需要处理的文本。\n包含换行符和多余空格。  "
    processed = preprocess_chain.run(raw_text=raw_text)
    print(f"原始文本: '{raw_text}'")
    print(f"处理后: '{processed}'")
    print()

def main():
    """主函数"""
    print("LangChain 链式调用学习")
    print("=" * 50)
    
    # 检查 API 密钥
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  注意: 未检测到 OPENAI_API_KEY 环境变量")
        print("部分演示需要 API 密钥才能运行")
        print()
    
    # 运行演示
    demo_transform_chain()
    demo_custom_chain()
    demo_chain_composition()
    
    # 需要 API 的演示
    demo_simple_sequential_chain()
    demo_sequential_chain()
    demo_router_chain()
    
    print("=" * 50)
    print("学习要点总结:")
    print("1. SimpleSequentialChain: 简单的顺序执行")
    print("2. SequentialChain: 复杂的多输入输出顺序链")
    print("3. RouterChain: 根据输入选择不同的处理路径")
    print("4. TransformChain: 数据转换和预处理")
    print("5. 自定义链: 实现特定的业务逻辑")
    print("6. 链组合: 构建复杂的工作流")

if __name__ == "__main__":
    main()