"""
LlamaIndex 查询系统详解

本文件介绍 LlamaIndex 中的查询系统和检索策略：
1. 查询引擎的类型和配置
2. 检索策略和优化
3. 查询后处理和排序
4. 复杂查询构建
5. 查询性能优化

学习目标：
- 掌握不同查询引擎的使用方法
- 理解检索策略的选择和优化
- 学会构建复杂的查询系统
- 了解查询性能优化技术
"""

import os
import time
from typing import List, Dict, Any, Optional

try:
    from llama_index.core import (
        VectorStoreIndex,
        Document,
        Settings,
        get_response_synthesizer
    )
    from llama_index.core.query_engine import (
        RetrieverQueryEngine,
        SubQuestionQueryEngine
    )
    from llama_index.core.retrievers import (
        VectorIndexRetriever,
        KeywordTableSimpleRetriever
    )
    from llama_index.core.postprocessor import (
        SimilarityPostprocessor,
        KeywordNodePostprocessor
    )
    from llama_index.core.llms import MockLLM
    from llama_index.core.response_synthesizers import ResponseMode
    
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    print("LlamaIndex 未安装，请运行: pip install llama-index")
    LLAMAINDEX_AVAILABLE = False

# 模拟嵌入模型
class MockEmbedding:
    """模拟嵌入模型"""
    
    def get_text_embedding(self, text: str) -> List[float]:
        """生成模拟嵌入向量"""
        import hashlib
        import numpy as np
        
        hash_obj = hashlib.md5(text.encode())
        seed = int(hash_obj.hexdigest()[:8], 16)
        np.random.seed(seed)
        
        return np.random.normal(0, 1, 384).tolist()
    
    def get_text_embedding_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成嵌入向量"""
        return [self.get_text_embedding(text) for text in texts]

def demo_basic_query_engine():
    """演示基础查询引擎"""
    print("=== 基础查询引擎演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    # 配置模型
    Settings.llm = MockLLM()
    Settings.embed_model = MockEmbedding()
    
    # 创建知识库文档
    documents = [
        Document(
            text="Python是一种高级编程语言，由Guido van Rossum于1991年创建。Python以其简洁的语法和强大的功能而闻名，广泛应用于Web开发、数据科学、人工智能等领域。",
            metadata={"topic": "Python", "type": "introduction"}
        ),
        Document(
            text="机器学习是人工智能的一个分支，它使计算机能够从数据中学习模式，而无需明确编程。主要类型包括监督学习、无监督学习和强化学习。",
            metadata={"topic": "机器学习", "type": "definition"}
        ),
        Document(
            text="深度学习是机器学习的子集，使用多层神经网络来学习数据的复杂表示。它在图像识别、自然语言处理、语音识别等任务中取得了突破性进展。",
            metadata={"topic": "深度学习", "type": "definition"}
        ),
        Document(
            text="数据科学结合了统计学、计算机科学和领域专业知识，从数据中提取洞察和知识。常用工具包括Python、R、SQL、Tableau等。",
            metadata={"topic": "数据科学", "type": "overview"}
        )
    ]
    
    try:
        # 创建索引
        index = VectorStoreIndex.from_documents(documents)
        
        # 创建基础查询引擎
        query_engine = index.as_query_engine()
        
        print("基础查询引擎创建成功")
        
        # 测试不同类型的查询
        test_queries = [
            "什么是Python？",
            "机器学习和深度学习有什么区别？",
            "数据科学需要哪些技能？",
            "Python在人工智能中的应用"
        ]
        
        print("\n查询测试:")
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. 查询: {query}")
            try:
                start_time = time.time()
                response = query_engine.query(query)
                query_time = time.time() - start_time
                
                print(f"   回答: {response}")
                print(f"   耗时: {query_time:.3f}秒")
            except Exception as e:
                print(f"   查询失败: {e}")
    
    except Exception as e:
        print(f"基础查询引擎演示失败: {e}")
    
    print()

def demo_custom_retriever():
    """演示自定义检索器"""
    print("=== 自定义检索器演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    # 配置模型
    Settings.llm = MockLLM()
    Settings.embed_model = MockEmbedding()
    
    # 创建技术文档
    documents = [
        Document(
            text="FastAPI是一个现代、快速的Python Web框架，用于构建API。它基于标准Python类型提示，提供自动API文档生成。",
            metadata={"framework": "FastAPI", "language": "Python", "category": "Web"}
        ),
        Document(
            text="Flask是一个轻量级的Python Web框架，它简单易用，适合小型到中型的Web应用开发。Flask遵循WSGI标准。",
            metadata={"framework": "Flask", "language": "Python", "category": "Web"}
        ),
        Document(
            text="Django是一个功能完整的Python Web框架，它遵循'约定优于配置'的原则，内置ORM、管理后台等功能。",
            metadata={"framework": "Django", "language": "Python", "category": "Web"}
        ),
        Document(
            text="React是一个用于构建用户界面的JavaScript库，由Facebook开发。它使用虚拟DOM来提高性能。",
            metadata={"framework": "React", "language": "JavaScript", "category": "Frontend"}
        ),
        Document(
            text="Vue.js是一个渐进式JavaScript框架，易于学习和使用。它提供了响应式数据绑定和组件系统。",
            metadata={"framework": "Vue.js", "language": "JavaScript", "category": "Frontend"}
        )
    ]
    
    try:
        # 创建索引
        index = VectorStoreIndex.from_documents(documents)
        
        # 创建自定义检索器
        retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=3,  # 返回最相似的3个文档
        )
        
        # 创建响应合成器
        response_synthesizer = get_response_synthesizer(
            response_mode=ResponseMode.COMPACT  # 紧凑模式
        )
        
        # 创建自定义查询引擎
        custom_query_engine = RetrieverQueryEngine(
            retriever=retriever,
            response_synthesizer=response_synthesizer
        )
        
        print("自定义检索器创建成功")
        print("配置: 返回top-3相似文档，使用紧凑响应模式")
        
        # 测试查询
        queries = [
            "Python Web框架有哪些？",
            "前端JavaScript框架推荐",
            "FastAPI和Flask的区别"
        ]
        
        print("\n检索测试:")
        for query in queries:
            print(f"\n查询: {query}")
            try:
                # 先测试检索
                retrieved_nodes = retriever.retrieve(query)
                print(f"检索到 {len(retrieved_nodes)} 个相关文档:")
                
                for i, node in enumerate(retrieved_nodes):
                    framework = node.metadata.get('framework', '未知')
                    score = getattr(node, 'score', 0)
                    print(f"  {i+1}. {framework} (相似度: {score:.3f})")
                    print(f"     {node.text[:80]}...")
                
                # 生成完整回答
                response = custom_query_engine.query(query)
                print(f"\n完整回答: {response}")
                
            except Exception as e:
                print(f"检索失败: {e}")
    
    except Exception as e:
        print(f"自定义检索器演示失败: {e}")
    
    print()

def demo_query_postprocessing():
    """演示查询后处理"""
    print("=== 查询后处理演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    # 配置模型
    Settings.llm = MockLLM()
    Settings.embed_model = MockEmbedding()
    
    documents = [
        Document(
            text="Python编程语言具有简洁的语法，适合初学者学习。Python在数据科学领域应用广泛。",
            metadata={"language": "Python", "difficulty": "beginner"}
        ),
        Document(
            text="Java是一种面向对象的编程语言，具有跨平台特性。Java在企业级应用开发中很受欢迎。",
            metadata={"language": "Java", "difficulty": "intermediate"}
        ),
        Document(
            text="JavaScript是Web开发的核心语言，可以用于前端和后端开发。Node.js使JavaScript能够在服务器端运行。",
            metadata={"language": "JavaScript", "difficulty": "intermediate"}
        ),
        Document(
            text="C++是一种高性能的编程语言，常用于系统编程和游戏开发。C++学习曲线较陡峭。",
            metadata={"language": "C++", "difficulty": "advanced"}
        ),
        Document(
            text="Go语言是Google开发的编程语言，具有高并发性能。Go语言语法简洁，编译速度快。",
            metadata={"language": "Go", "difficulty": "intermediate"}
        )
    ]
    
    try:
        # 创建索引
        index = VectorStoreIndex.from_documents(documents)
        
        # 创建基础检索器
        base_retriever = VectorIndexRetriever(
            index=index,
            similarity_top_k=5
        )
        
        # 添加后处理器
        postprocessors = [
            # 相似度过滤器
            SimilarityPostprocessor(similarity_cutoff=0.7),
            
            # 关键词过滤器
            KeywordNodePostprocessor(
                keywords=["编程语言", "开发"],
                exclude_keywords=["游戏"]
            )
        ]
        
        # 创建带后处理的查询引擎
        query_engine = index.as_query_engine(
            node_postprocessors=postprocessors,
            similarity_top_k=5
        )
        
        print("查询后处理器配置:")
        print("1. 相似度过滤: 只保留相似度>0.7的结果")
        print("2. 关键词过滤: 包含'编程语言'或'开发'，排除'游戏'")
        
        # 测试查询
        queries = [
            "适合初学者的编程语言",
            "高性能编程语言推荐",
            "Web开发语言选择"
        ]
        
        print("\n后处理测试:")
        for query in queries:
            print(f"\n查询: {query}")
            try:
                # 先看原始检索结果
                raw_nodes = base_retriever.retrieve(query)
                print(f"原始检索: {len(raw_nodes)} 个结果")
                
                # 再看后处理结果
                response = query_engine.query(query)
                print(f"后处理回答: {response}")
                
            except Exception as e:
                print(f"后处理查询失败: {e}")
    
    except Exception as e:
        print(f"查询后处理演示失败: {e}")
    
    print()

def demo_sub_question_query():
    """演示子问题查询"""
    print("=== 子问题查询演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    print("子问题查询概念:")
    print("1. 将复杂问题分解为多个子问题")
    print("2. 分别回答每个子问题")
    print("3. 综合子问题答案生成最终回答")
    print("4. 适合处理需要多步推理的复杂查询")
    
    # 示例复杂查询
    complex_queries = [
        "比较Python和Java在Web开发和数据科学领域的优缺点",
        "分析机器学习和深度学习的区别，并说明各自的应用场景",
        "评估不同编程语言在性能、易学性和生态系统方面的特点"
    ]
    
    print("\n复杂查询示例:")
    for i, query in enumerate(complex_queries, 1):
        print(f"{i}. {query}")
        
        # 模拟子问题分解
        if "比较Python和Java" in query:
            sub_questions = [
                "Python在Web开发中的优缺点是什么？",
                "Java在Web开发中的优缺点是什么？",
                "Python在数据科学中的优缺点是什么？",
                "Java在数据科学中的优缺点是什么？"
            ]
        elif "机器学习和深度学习" in query:
            sub_questions = [
                "什么是机器学习？",
                "什么是深度学习？",
                "机器学习和深度学习有什么区别？",
                "机器学习的应用场景有哪些？",
                "深度学习的应用场景有哪些？"
            ]
        else:
            sub_questions = [
                "不同编程语言的性能特点是什么？",
                "不同编程语言的易学性如何？",
                "不同编程语言的生态系统怎么样？"
            ]
        
        print(f"   可能的子问题:")
        for j, sub_q in enumerate(sub_questions, 1):
            print(f"   {j}. {sub_q}")
        print()

def demo_query_optimization():
    """演示查询优化技术"""
    print("=== 查询优化技术演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    # 配置模型
    Settings.llm = MockLLM()
    Settings.embed_model = MockEmbedding()
    
    # 创建大量文档进行优化测试
    def generate_tech_documents(count: int) -> List[Document]:
        """生成技术文档"""
        topics = [
            ("Python", "编程语言"),
            ("机器学习", "人工智能"),
            ("Web开发", "前端技术"),
            ("数据库", "后端技术"),
            ("云计算", "基础设施")
        ]
        
        documents = []
        for i in range(count):
            topic, category = topics[i % len(topics)]
            text = f"{topic}是{category}领域的重要技术。"
            text += f"它在现代软件开发中扮演着关键角色。"
            text += f"文档编号：{i+1}，类别：{category}。"
            
            doc = Document(
                text=text,
                metadata={
                    "topic": topic,
                    "category": category,
                    "doc_id": i,
                    "priority": i % 3  # 0=高, 1=中, 2=低
                }
            )
            documents.append(doc)
        
        return documents
    
    # 生成测试文档
    test_docs = generate_tech_documents(30)
    
    try:
        # 创建索引
        index = VectorStoreIndex.from_documents(test_docs)
        
        print("查询优化策略测试:")
        
        # 优化1: 调整相似度阈值
        print("\n1. 相似度阈值优化")
        
        thresholds = [0.5, 0.7, 0.9]
        query = "Python编程技术"
        
        for threshold in thresholds:
            query_engine = index.as_query_engine(
                node_postprocessors=[
                    SimilarityPostprocessor(similarity_cutoff=threshold)
                ]
            )
            
            start_time = time.time()
            try:
                response = query_engine.query(query)
                query_time = time.time() - start_time
                print(f"   阈值 {threshold}: 耗时 {query_time:.3f}秒")
            except Exception as e:
                print(f"   阈值 {threshold}: 查询失败 - {e}")
        
        # 优化2: 调整返回文档数量
        print("\n2. 返回文档数量优化")
        
        top_k_values = [1, 3, 5, 10]
        
        for top_k in top_k_values:
            query_engine = index.as_query_engine(similarity_top_k=top_k)
            
            start_time = time.time()
            try:
                response = query_engine.query(query)
                query_time = time.time() - start_time
                print(f"   Top-{top_k}: 耗时 {query_time:.3f}秒")
            except Exception as e:
                print(f"   Top-{top_k}: 查询失败 - {e}")
        
        # 优化3: 响应模式比较
        print("\n3. 响应模式优化")
        
        response_modes = [
            ResponseMode.REFINE,
            ResponseMode.COMPACT,
            ResponseMode.TREE_SUMMARIZE
        ]
        
        for mode in response_modes:
            try:
                query_engine = index.as_query_engine(
                    response_mode=mode,
                    similarity_top_k=3
                )
                
                start_time = time.time()
                response = query_engine.query(query)
                query_time = time.time() - start_time
                
                print(f"   {mode}: 耗时 {query_time:.3f}秒")
            except Exception as e:
                print(f"   {mode}: 不支持或失败 - {e}")
    
    except Exception as e:
        print(f"查询优化演示失败: {e}")
    
    # 优化建议
    print("\n查询优化建议:")
    print("1. 合理设置相似度阈值，平衡精度和召回")
    print("2. 根据应用需求调整返回文档数量")
    print("3. 选择合适的响应合成模式")
    print("4. 使用缓存机制减少重复计算")
    print("5. 批量处理提高吞吐量")
    print("6. 异步查询提升用户体验")
    
    print()

def demo_query_debugging():
    """演示查询调试技术"""
    print("=== 查询调试技术演示 ===")
    
    print("查询调试方法:")
    print("1. 启用详细日志记录")
    print("2. 检查检索到的文档")
    print("3. 分析相似度分数")
    print("4. 验证查询预处理")
    print("5. 测试不同的查询表述")
    
    # 调试检查清单
    debug_checklist = {
        "查询预处理": [
            "查询文本是否正确？",
            "是否包含特殊字符？",
            "语言是否匹配？"
        ],
        "检索阶段": [
            "检索到的文档数量是否合理？",
            "相似度分数是否在预期范围？",
            "是否检索到相关文档？"
        ],
        "后处理阶段": [
            "过滤器是否过于严格？",
            "排序是否正确？",
            "是否有文档被意外过滤？"
        ],
        "响应生成": [
            "LLM是否正常工作？",
            "提示模板是否合适？",
            "响应是否符合预期？"
        ]
    }
    
    print("\n调试检查清单:")
    for stage, checks in debug_checklist.items():
        print(f"\n{stage}:")
        for check in checks:
            print(f"  - {check}")
    
    print("\n常见问题和解决方案:")
    common_issues = {
        "检索不到相关文档": [
            "检查嵌入模型是否合适",
            "调整相似度阈值",
            "增加文档数量",
            "改进查询表述"
        ],
        "响应质量差": [
            "检查LLM配置",
            "优化提示模板",
            "调整响应模式",
            "增加上下文信息"
        ],
        "查询速度慢": [
            "减少返回文档数量",
            "优化索引结构",
            "使用缓存机制",
            "考虑异步处理"
        ]
    }
    
    for issue, solutions in common_issues.items():
        print(f"\n{issue}:")
        for solution in solutions:
            print(f"  - {solution}")
    
    print()

def main():
    """主函数"""
    print("LlamaIndex 查询系统学习")
    print("=" * 50)
    
    # 检查依赖
    if not LLAMAINDEX_AVAILABLE:
        print("⚠️  LlamaIndex 未安装")
        print("请运行: pip install llama-index")
        print()
    
    # 运行演示
    demo_basic_query_engine()
    demo_custom_retriever()
    demo_query_postprocessing()
    demo_sub_question_query()
    demo_query_optimization()
    demo_query_debugging()
    
    print("=" * 50)
    print("学习要点总结:")
    print("1. 查询引擎是用户与知识库交互的接口")
    print("2. 检索器决定了文档召回的质量")
    print("3. 后处理器可以进一步优化结果")
    print("4. 复杂查询需要分解为子问题")
    print("5. 查询优化平衡精度、速度和资源消耗")
    print("6. 调试技术帮助诊断和解决问题")

if __name__ == "__main__":
    main()