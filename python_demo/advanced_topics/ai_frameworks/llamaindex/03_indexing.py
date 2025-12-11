"""
LlamaIndex 索引构建详解

本文件介绍 LlamaIndex 中的索引构建和优化：
1. 不同类型的索引
2. 索引构建策略
3. 索引优化技术
4. 索引性能调优
5. 索引管理和维护

学习目标：
- 理解不同索引类型的特点和适用场景
- 掌握索引构建的最佳实践
- 学会优化索引性能
- 了解索引的管理和维护方法
"""

import os
import tempfile
from typing import List, Dict, Any, Optional
import time

try:
    from llama_index.core import (
        VectorStoreIndex,
        ListIndex,
        TreeIndex,
        KeywordTableIndex,
        Document,
        Settings,
        StorageContext,
        ServiceContext
    )
    from llama_index.core.llms import MockLLM
    from llama_index.core.node_parser import SimpleNodeParser, SentenceSplitter
    
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

def demo_vector_store_index():
    """演示向量存储索引"""
    print("=== 向量存储索引演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    # 配置模型
    Settings.llm = MockLLM()
    Settings.embed_model = MockEmbedding()
    
    # 创建示例文档
    documents = [
        Document(
            text="Python是一种高级编程语言，具有简洁的语法和强大的功能。它广泛应用于Web开发、数据科学、人工智能等领域。",
            metadata={"category": "编程语言", "difficulty": "初级"}
        ),
        Document(
            text="机器学习是人工智能的一个分支，它使计算机能够从数据中学习模式，而无需明确编程。常见算法包括线性回归、决策树、神经网络等。",
            metadata={"category": "人工智能", "difficulty": "中级"}
        ),
        Document(
            text="深度学习是机器学习的子集，使用多层神经网络来学习数据的复杂表示。它在图像识别、自然语言处理等任务中表现出色。",
            metadata={"category": "人工智能", "difficulty": "高级"}
        ),
        Document(
            text="数据结构是计算机科学的基础，包括数组、链表、栈、队列、树、图等。选择合适的数据结构对算法效率至关重要。",
            metadata={"category": "计算机科学", "difficulty": "中级"}
        )
    ]
    
    try:
        print("创建向量存储索引...")
        start_time = time.time()
        
        # 创建向量索引
        vector_index = VectorStoreIndex.from_documents(documents)
        
        build_time = time.time() - start_time
        print(f"索引构建完成，耗时: {build_time:.2f} 秒")
        
        # 创建查询引擎
        query_engine = vector_index.as_query_engine(similarity_top_k=2)
        
        # 测试查询
        test_queries = [
            "什么是Python？",
            "机器学习和深度学习的区别？",
            "数据结构有哪些类型？"
        ]
        
        print("\n查询测试:")
        for query in test_queries:
            print(f"\n查询: {query}")
            try:
                start_time = time.time()
                response = query_engine.query(query)
                query_time = time.time() - start_time
                
                print(f"回答: {response}")
                print(f"查询耗时: {query_time:.3f} 秒")
            except Exception as e:
                print(f"查询失败: {e}")
    
    except Exception as e:
        print(f"向量索引创建失败: {e}")
    
    print()

def demo_list_index():
    """演示列表索引"""
    print("=== 列表索引演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    # 配置模型
    Settings.llm = MockLLM()
    
    documents = [
        Document(text="第一步：安装Python开发环境，包括Python解释器和IDE。"),
        Document(text="第二步：学习Python基础语法，包括变量、数据类型、控制结构。"),
        Document(text="第三步：掌握函数和类的使用，理解面向对象编程概念。"),
        Document(text="第四步：学习常用库，如NumPy、Pandas、Matplotlib等。"),
        Document(text="第五步：实践项目开发，将所学知识应用到实际项目中。")
    ]
    
    try:
        print("创建列表索引...")
        
        # 创建列表索引（按顺序处理文档）
        list_index = ListIndex.from_documents(documents)
        
        print("列表索引创建完成")
        print("特点: 按文档顺序处理，适合有序内容")
        
        # 创建查询引擎
        query_engine = list_index.as_query_engine()
        
        # 测试查询
        query = "Python学习的步骤是什么？"
        print(f"\n查询: {query}")
        
        try:
            response = query_engine.query(query)
            print(f"回答: {response}")
        except Exception as e:
            print(f"查询失败: {e}")
    
    except Exception as e:
        print(f"列表索引创建失败: {e}")
    
    print()

def demo_tree_index():
    """演示树索引"""
    print("=== 树索引演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    # 配置模型
    Settings.llm = MockLLM()
    
    # 创建层次化文档
    documents = [
        Document(
            text="编程语言概述：编程语言是用来编写计算机程序的形式语言。",
            metadata={"level": 1, "topic": "编程语言"}
        ),
        Document(
            text="Python语言：Python是一种高级、解释型编程语言，语法简洁。",
            metadata={"level": 2, "topic": "Python"}
        ),
        Document(
            text="Python应用：Web开发、数据科学、人工智能、自动化脚本。",
            metadata={"level": 3, "topic": "Python应用"}
        ),
        Document(
            text="Java语言：Java是一种面向对象的编程语言，具有跨平台特性。",
            metadata={"level": 2, "topic": "Java"}
        ),
        Document(
            text="Java应用：企业级应用、Android开发、大数据处理。",
            metadata={"level": 3, "topic": "Java应用"}
        )
    ]
    
    try:
        print("创建树索引...")
        
        # 创建树索引（层次化组织）
        tree_index = TreeIndex.from_documents(documents)
        
        print("树索引创建完成")
        print("特点: 层次化组织，适合有结构的内容")
        
        # 创建查询引擎
        query_engine = tree_index.as_query_engine()
        
        # 测试查询
        queries = [
            "编程语言有哪些？",
            "Python和Java的应用领域？"
        ]
        
        for query in queries:
            print(f"\n查询: {query}")
            try:
                response = query_engine.query(query)
                print(f"回答: {response}")
            except Exception as e:
                print(f"查询失败: {e}")
    
    except Exception as e:
        print(f"树索引创建失败: {e}")
    
    print()

def demo_keyword_table_index():
    """演示关键词表索引"""
    print("=== 关键词表索引演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    # 配置模型
    Settings.llm = MockLLM()
    
    documents = [
        Document(
            text="Python编程语言具有简洁的语法，适合初学者学习。Python支持多种编程范式，包括面向对象和函数式编程。",
            metadata={"keywords": ["Python", "编程语言", "语法", "面向对象"]}
        ),
        Document(
            text="机器学习算法包括监督学习、无监督学习和强化学习。常用算法有线性回归、决策树、神经网络等。",
            metadata={"keywords": ["机器学习", "算法", "监督学习", "神经网络"]}
        ),
        Document(
            text="Web开发涉及前端和后端技术。前端使用HTML、CSS、JavaScript，后端可以使用Python、Java、Node.js等。",
            metadata={"keywords": ["Web开发", "前端", "后端", "JavaScript", "Python"]}
        )
    ]
    
    try:
        print("创建关键词表索引...")
        
        # 创建关键词表索引
        keyword_index = KeywordTableIndex.from_documents(documents)
        
        print("关键词表索引创建完成")
        print("特点: 基于关键词匹配，适合精确查找")
        
        # 创建查询引擎
        query_engine = keyword_index.as_query_engine()
        
        # 测试关键词查询
        queries = [
            "Python编程",
            "机器学习算法",
            "Web开发技术"
        ]
        
        for query in queries:
            print(f"\n查询: {query}")
            try:
                response = query_engine.query(query)
                print(f"回答: {response}")
            except Exception as e:
                print(f"查询失败: {e}")
    
    except Exception as e:
        print(f"关键词表索引创建失败: {e}")
    
    print()

def demo_index_optimization():
    """演示索引优化技术"""
    print("=== 索引优化技术演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    # 配置模型
    Settings.llm = MockLLM()
    Settings.embed_model = MockEmbedding()
    
    # 创建大量文档进行优化测试
    def generate_documents(count: int) -> List[Document]:
        """生成测试文档"""
        topics = ["Python", "机器学习", "Web开发", "数据科学", "人工智能"]
        documents = []
        
        for i in range(count):
            topic = topics[i % len(topics)]
            text = f"这是关于{topic}的第{i+1}篇文档。{topic}是一个重要的技术领域，"
            text += f"在现代软件开发中扮演着重要角色。文档编号：{i+1}。"
            
            doc = Document(
                text=text,
                metadata={"topic": topic, "doc_id": i, "length": len(text)}
            )
            documents.append(doc)
        
        return documents
    
    # 生成测试文档
    test_docs = generate_documents(50)
    print(f"生成了 {len(test_docs)} 个测试文档")
    
    # 优化1: 使用不同的节点解析器
    print("\n优化1: 节点解析器比较")
    
    try:
        # 默认解析器
        start_time = time.time()
        default_parser = SimpleNodeParser()
        default_nodes = default_parser.get_nodes_from_documents(test_docs)
        default_time = time.time() - start_time
        
        print(f"默认解析器: {len(default_nodes)} 个节点, 耗时: {default_time:.3f}秒")
        
        # 句子分割器
        start_time = time.time()
        sentence_parser = SentenceSplitter(chunk_size=200, chunk_overlap=20)
        sentence_nodes = sentence_parser.get_nodes_from_documents(test_docs)
        sentence_time = time.time() - start_time
        
        print(f"句子分割器: {len(sentence_nodes)} 个节点, 耗时: {sentence_time:.3f}秒")
        
    except Exception as e:
        print(f"节点解析器测试失败: {e}")
    
    # 优化2: 索引构建性能比较
    print("\n优化2: 索引构建性能比较")
    
    try:
        # 小批量文档
        small_docs = test_docs[:10]
        
        # 向量索引
        start_time = time.time()
        vector_index = VectorStoreIndex.from_documents(small_docs)
        vector_time = time.time() - start_time
        
        print(f"向量索引构建: {vector_time:.3f}秒")
        
        # 列表索引
        start_time = time.time()
        list_index = ListIndex.from_documents(small_docs)
        list_time = time.time() - start_time
        
        print(f"列表索引构建: {list_time:.3f}秒")
        
        # 关键词索引
        start_time = time.time()
        keyword_index = KeywordTableIndex.from_documents(small_docs)
        keyword_time = time.time() - start_time
        
        print(f"关键词索引构建: {keyword_time:.3f}秒")
        
    except Exception as e:
        print(f"索引性能测试失败: {e}")
    
    # 优化建议
    print("\n索引优化建议:")
    print("1. 文档预处理: 清理无用内容，统一格式")
    print("2. 合适的分块大小: 平衡检索精度和性能")
    print("3. 选择合适的索引类型: 根据查询模式选择")
    print("4. 批量处理: 减少API调用次数")
    print("5. 缓存机制: 缓存常用查询结果")
    print("6. 增量更新: 避免重建整个索引")
    
    print()

def demo_index_persistence_and_loading():
    """演示索引持久化和加载"""
    print("=== 索引持久化和加载演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    # 配置模型
    Settings.llm = MockLLM()
    Settings.embed_model = MockEmbedding()
    
    documents = [
        Document(text="索引持久化是将索引保存到磁盘的过程，可以避免重复构建。"),
        Document(text="加载索引可以快速恢复之前构建的索引，提高应用启动速度。"),
        Document(text="LlamaIndex支持多种存储后端，包括本地文件系统和云存储。")
    ]
    
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            print("创建并保存索引...")
            
            # 创建索引
            index = VectorStoreIndex.from_documents(documents)
            
            # 保存索引
            index.storage_context.persist(persist_dir=temp_dir)
            print(f"索引已保存到: {temp_dir}")
            
            # 模拟应用重启 - 加载索引
            print("\n模拟应用重启，加载索引...")
            
            from llama_index.core import StorageContext, load_index_from_storage
            
            # 加载存储上下文
            storage_context = StorageContext.from_defaults(persist_dir=temp_dir)
            
            # 加载索引
            loaded_index = load_index_from_storage(storage_context)
            print("索引加载成功")
            
            # 测试加载的索引
            query_engine = loaded_index.as_query_engine()
            query = "什么是索引持久化？"
            
            print(f"\n测试查询: {query}")
            response = query_engine.query(query)
            print(f"回答: {response}")
            
            # 检查索引文件
            import os
            files = os.listdir(temp_dir)
            print(f"\n索引文件: {files}")
            
        except Exception as e:
            print(f"索引持久化演示失败: {e}")
    
    print()

def demo_index_comparison():
    """演示不同索引类型的比较"""
    print("=== 索引类型比较 ===")
    
    comparison_data = {
        "VectorStoreIndex": {
            "原理": "基于向量相似度搜索",
            "优点": ["语义搜索能力强", "处理大规模数据", "支持模糊匹配"],
            "缺点": ["需要嵌入模型", "构建时间较长", "内存占用大"],
            "适用场景": ["语义搜索", "问答系统", "文档检索"],
            "性能": "查询快，构建慢"
        },
        "ListIndex": {
            "原理": "顺序遍历所有文档",
            "优点": ["简单直接", "不需要预处理", "适合小数据集"],
            "缺点": ["查询速度慢", "不适合大数据", "无法并行"],
            "适用场景": ["小型数据集", "顺序处理", "简单查询"],
            "性能": "构建快，查询慢"
        },
        "TreeIndex": {
            "原理": "层次化组织文档",
            "优点": ["结构化查询", "支持层次关系", "查询路径清晰"],
            "缺点": ["构建复杂", "需要结构化数据", "维护成本高"],
            "适用场景": ["层次化数据", "分类查询", "知识图谱"],
            "性能": "中等构建和查询速度"
        },
        "KeywordTableIndex": {
            "原理": "基于关键词匹配",
            "优点": ["精确匹配", "构建快速", "内存占用小"],
            "缺点": ["无语义理解", "依赖关键词", "匹配能力有限"],
            "适用场景": ["精确查找", "关键词搜索", "结构化查询"],
            "性能": "构建和查询都很快"
        }
    }
    
    print("索引类型详细比较:")
    for index_type, info in comparison_data.items():
        print(f"\n{index_type}:")
        print(f"  原理: {info['原理']}")
        print(f"  优点: {', '.join(info['优点'])}")
        print(f"  缺点: {', '.join(info['缺点'])}")
        print(f"  适用场景: {', '.join(info['适用场景'])}")
        print(f"  性能特点: {info['性能']}")
    
    print("\n选择建议:")
    print("1. 语义搜索需求 → VectorStoreIndex")
    print("2. 小数据集简单查询 → ListIndex")
    print("3. 层次化数据 → TreeIndex")
    print("4. 精确关键词匹配 → KeywordTableIndex")
    print("5. 混合需求 → 组合多种索引")
    
    print()

def main():
    """主函数"""
    print("LlamaIndex 索引构建学习")
    print("=" * 50)
    
    # 检查依赖
    if not LLAMAINDEX_AVAILABLE:
        print("⚠️  LlamaIndex 未安装")
        print("请运行: pip install llama-index")
        print()
    
    # 运行演示
    demo_vector_store_index()
    demo_list_index()
    demo_tree_index()
    demo_keyword_table_index()
    demo_index_optimization()
    demo_index_persistence_and_loading()
    demo_index_comparison()
    
    print("=" * 50)
    print("学习要点总结:")
    print("1. 不同索引类型适用于不同场景")
    print("2. 向量索引提供最佳的语义搜索能力")
    print("3. 索引优化可以显著提升性能")
    print("4. 持久化避免重复构建索引")
    print("5. 选择合适的节点解析策略很重要")
    print("6. 根据数据特点和查询需求选择索引类型")

if __name__ == "__main__":
    main()