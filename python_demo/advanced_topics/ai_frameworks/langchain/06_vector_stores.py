"""
LangChain 向量存储详解

本文件介绍 LangChain 中的向量存储和检索：
1. 向量存储的基本概念
2. 不同向量数据库的使用
3. 嵌入模型的选择和使用
4. 相似性搜索和检索
5. 向量存储的优化策略

学习目标：
- 理解向量存储的工作原理
- 掌握常用向量数据库的使用
- 学会构建高效的检索系统
- 了解嵌入模型的选择策略
"""

import os
import numpy as np
from typing import List, Dict, Any, Optional
import tempfile
import json

from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma, FAISS
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 模拟嵌入模型（当没有API密钥时使用）
class MockEmbeddings:
    """模拟嵌入模型，用于演示"""
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """为文档生成模拟嵌入向量"""
        embeddings = []
        for text in texts:
            # 基于文本长度和字符生成简单的向量
            vector = []
            for i in range(384):  # 384维向量
                # 基于文本内容生成伪随机数
                seed = hash(text + str(i)) % 1000000
                np.random.seed(seed)
                vector.append(np.random.normal(0, 1))
            embeddings.append(vector)
        return embeddings
    
    def embed_query(self, text: str) -> List[float]:
        """为查询生成模拟嵌入向量"""
        return self.embed_documents([text])[0]

def demo_basic_vector_store():
    """演示基础向量存储"""
    print("=== 基础向量存储演示 ===")
    
    # 准备示例文档
    documents = [
        Document(
            page_content="Python是一种高级编程语言，语法简洁明了。",
            metadata={"source": "python_intro", "category": "编程"}
        ),
        Document(
            page_content="机器学习是人工智能的一个重要分支。",
            metadata={"source": "ml_intro", "category": "AI"}
        ),
        Document(
            page_content="深度学习使用神经网络来模拟人脑的学习过程。",
            metadata={"source": "dl_intro", "category": "AI"}
        ),
        Document(
            page_content="数据结构是计算机科学的基础概念。",
            metadata={"source": "ds_intro", "category": "编程"}
        ),
        Document(
            page_content="算法是解决问题的步骤和方法。",
            metadata={"source": "algo_intro", "category": "编程"}
        )
    ]
    
    # 选择嵌入模型
    if os.getenv("OPENAI_API_KEY"):
        embeddings = OpenAIEmbeddings()
        print("使用 OpenAI 嵌入模型")
    else:
        embeddings = MockEmbeddings()
        print("使用模拟嵌入模型（演示用）")
    
    # 创建向量存储
    try:
        vectorstore = FAISS.from_documents(documents, embeddings)
        print(f"成功创建向量存储，包含 {len(documents)} 个文档")
        
        # 相似性搜索
        query = "什么是编程语言？"
        results = vectorstore.similarity_search(query, k=2)
        
        print(f"\n查询: {query}")
        print("最相似的文档:")
        for i, doc in enumerate(results):
            print(f"{i+1}. {doc.page_content}")
            print(f"   来源: {doc.metadata['source']}")
            print(f"   类别: {doc.metadata['category']}")
        
    except Exception as e:
        print(f"向量存储创建失败: {e}")
    
    print()

def demo_similarity_search_with_scores():
    """演示带分数的相似性搜索"""
    print("=== 带分数的相似性搜索演示 ===")
    
    # 创建更多样化的文档
    tech_docs = [
        "Python是一种解释型、面向对象的编程语言，具有简洁的语法。",
        "JavaScript是一种动态类型的编程语言，主要用于Web开发。",
        "机器学习算法可以从数据中自动学习模式和规律。",
        "深度学习是机器学习的一个子集，使用多层神经网络。",
        "数据库是存储和管理数据的系统，支持查询和更新操作。",
        "云计算提供按需访问的计算资源和服务。",
        "区块链是一种分布式账本技术，具有去中心化特性。",
        "人工智能旨在创建能够执行通常需要人类智能的任务的系统。"
    ]
    
    documents = [Document(page_content=content, metadata={"id": i}) 
                for i, content in enumerate(tech_docs)]
    
    embeddings = MockEmbeddings()
    
    try:
        vectorstore = FAISS.from_documents(documents, embeddings)
        
        # 不同类型的查询
        queries = [
            "编程语言有哪些？",
            "什么是人工智能？",
            "数据存储方案"
        ]
        
        for query in queries:
            print(f"查询: {query}")
            
            # 带分数的搜索
            results_with_scores = vectorstore.similarity_search_with_score(query, k=3)
            
            print("搜索结果（带相似度分数）:")
            for doc, score in results_with_scores:
                print(f"  分数: {score:.4f} - {doc.page_content[:50]}...")
            print("-" * 50)
        
    except Exception as e:
        print(f"搜索失败: {e}")
    
    print()

def demo_metadata_filtering():
    """演示元数据过滤"""
    print("=== 元数据过滤演示 ===")
    
    # 创建带有丰富元数据的文档
    documents = [
        Document(
            page_content="Python基础语法教程",
            metadata={"language": "Python", "level": "beginner", "type": "tutorial"}
        ),
        Document(
            page_content="Python高级特性详解",
            metadata={"language": "Python", "level": "advanced", "type": "guide"}
        ),
        Document(
            page_content="JavaScript入门指南",
            metadata={"language": "JavaScript", "level": "beginner", "type": "tutorial"}
        ),
        Document(
            page_content="机器学习算法实现",
            metadata={"language": "Python", "level": "advanced", "type": "implementation"}
        ),
        Document(
            page_content="Web开发最佳实践",
            metadata={"language": "JavaScript", "level": "intermediate", "type": "guide"}
        )
    ]
    
    embeddings = MockEmbeddings()
    
    try:
        vectorstore = FAISS.from_documents(documents, embeddings)
        
        # 基础搜索
        print("1. 基础搜索（无过滤）:")
        results = vectorstore.similarity_search("Python编程", k=3)
        for doc in results:
            print(f"  - {doc.page_content} ({doc.metadata})")
        
        # 注意：FAISS不直接支持元数据过滤，这里演示概念
        print("\n2. 元数据过滤概念演示:")
        print("   可以通过以下方式实现过滤:")
        print("   - 预先按元数据分组存储")
        print("   - 搜索后再过滤结果")
        print("   - 使用支持过滤的向量数据库（如Chroma）")
        
        # 手动过滤示例
        all_results = vectorstore.similarity_search("编程", k=10)
        python_results = [doc for doc in all_results 
                         if doc.metadata.get("language") == "Python"]
        
        print(f"\n3. 手动过滤结果（只显示Python相关）:")
        for doc in python_results[:2]:
            print(f"  - {doc.page_content}")
        
    except Exception as e:
        print(f"过滤演示失败: {e}")
    
    print()

def demo_chroma_vector_store():
    """演示Chroma向量存储"""
    print("=== Chroma向量存储演示 ===")
    
    try:
        # 创建临时目录用于Chroma存储
        with tempfile.TemporaryDirectory() as temp_dir:
            documents = [
                Document(
                    page_content="FastAPI是一个现代、快速的Python Web框架。",
                    metadata={"framework": "FastAPI", "language": "Python"}
                ),
                Document(
                    page_content="Flask是一个轻量级的Python Web框架。",
                    metadata={"framework": "Flask", "language": "Python"}
                ),
                Document(
                    page_content="Django是一个功能完整的Python Web框架。",
                    metadata={"framework": "Django", "language": "Python"}
                ),
                Document(
                    page_content="Express.js是一个Node.js的Web应用框架。",
                    metadata={"framework": "Express", "language": "JavaScript"}
                )
            ]
            
            embeddings = MockEmbeddings()
            
            # 创建Chroma向量存储
            vectorstore = Chroma.from_documents(
                documents=documents,
                embedding=embeddings,
                persist_directory=temp_dir
            )
            
            print("Chroma向量存储创建成功")
            
            # 搜索测试
            query = "Python Web框架"
            results = vectorstore.similarity_search(query, k=2)
            
            print(f"\n查询: {query}")
            for i, doc in enumerate(results):
                print(f"{i+1}. {doc.page_content}")
                print(f"   框架: {doc.metadata['framework']}")
            
            # Chroma支持元数据过滤
            print(f"\n带过滤的搜索（只搜索Python框架）:")
            filtered_results = vectorstore.similarity_search(
                query,
                k=3,
                filter={"language": "Python"}
            )
            
            for doc in filtered_results:
                print(f"- {doc.page_content}")
        
    except Exception as e:
        print(f"Chroma演示失败: {e}")
        print("可能需要安装: pip install chromadb")
    
    print()

def demo_vector_store_operations():
    """演示向量存储的各种操作"""
    print("=== 向量存储操作演示 ===")
    
    embeddings = MockEmbeddings()
    
    # 初始文档
    initial_docs = [
        Document(page_content="初始文档1：关于Python编程", metadata={"id": "1"}),
        Document(page_content="初始文档2：关于机器学习", metadata={"id": "2"})
    ]
    
    try:
        vectorstore = FAISS.from_documents(initial_docs, embeddings)
        print(f"初始向量存储包含 {vectorstore.index.ntotal} 个向量")
        
        # 添加新文档
        new_docs = [
            Document(page_content="新文档1：关于深度学习", metadata={"id": "3"}),
            Document(page_content="新文档2：关于数据科学", metadata={"id": "4"})
        ]
        
        vectorstore.add_documents(new_docs)
        print(f"添加文档后包含 {vectorstore.index.ntotal} 个向量")
        
        # 搜索测试
        results = vectorstore.similarity_search("学习", k=3)
        print(f"\n搜索'学习'的结果:")
        for doc in results:
            print(f"- {doc.page_content}")
        
        # 保存和加载（FAISS支持）
        with tempfile.TemporaryDirectory() as temp_dir:
            save_path = os.path.join(temp_dir, "vectorstore")
            vectorstore.save_local(save_path)
            print(f"\n向量存储已保存到: {save_path}")
            
            # 加载向量存储
            loaded_vectorstore = FAISS.load_local(save_path, embeddings)
            print(f"加载的向量存储包含 {loaded_vectorstore.index.ntotal} 个向量")
        
    except Exception as e:
        print(f"向量存储操作失败: {e}")
    
    print()

def demo_custom_retriever():
    """演示自定义检索器"""
    print("=== 自定义检索器演示 ===")
    
    from langchain.schema import BaseRetriever
    
    class HybridRetriever(BaseRetriever):
        """混合检索器：结合关键词和向量搜索"""
        
        def __init__(self, vectorstore, documents):
            self.vectorstore = vectorstore
            self.documents = documents
        
        def get_relevant_documents(self, query: str) -> List[Document]:
            """获取相关文档"""
            # 1. 向量搜索
            vector_results = self.vectorstore.similarity_search(query, k=3)
            
            # 2. 关键词搜索（简单实现）
            query_words = query.lower().split()
            keyword_results = []
            
            for doc in self.documents:
                content_lower = doc.page_content.lower()
                score = sum(1 for word in query_words if word in content_lower)
                if score > 0:
                    keyword_results.append((doc, score))
            
            # 按分数排序
            keyword_results.sort(key=lambda x: x[1], reverse=True)
            keyword_docs = [doc for doc, score in keyword_results[:2]]
            
            # 3. 合并结果（去重）
            seen_content = set()
            combined_results = []
            
            for doc in vector_results + keyword_docs:
                if doc.page_content not in seen_content:
                    combined_results.append(doc)
                    seen_content.add(doc.page_content)
            
            return combined_results[:3]  # 返回前3个结果
        
        async def aget_relevant_documents(self, query: str) -> List[Document]:
            """异步获取相关文档"""
            return self.get_relevant_documents(query)
    
    # 创建测试数据
    documents = [
        Document(page_content="Python编程语言入门教程", metadata={"type": "tutorial"}),
        Document(page_content="机器学习算法详解", metadata={"type": "guide"}),
        Document(page_content="深度学习神经网络", metadata={"type": "advanced"}),
        Document(page_content="数据分析与可视化", metadata={"type": "analysis"}),
        Document(page_content="Web开发框架比较", metadata={"type": "comparison"})
    ]
    
    embeddings = MockEmbeddings()
    
    try:
        vectorstore = FAISS.from_documents(documents, embeddings)
        
        # 创建混合检索器
        hybrid_retriever = HybridRetriever(vectorstore, documents)
        
        # 测试检索
        query = "Python编程"
        results = hybrid_retriever.get_relevant_documents(query)
        
        print(f"混合检索结果（查询: {query}）:")
        for i, doc in enumerate(results):
            print(f"{i+1}. {doc.page_content}")
            print(f"   类型: {doc.metadata['type']}")
        
    except Exception as e:
        print(f"自定义检索器演示失败: {e}")
    
    print()

def demo_vector_store_comparison():
    """演示不同向量存储的比较"""
    print("=== 向量存储比较 ===")
    
    comparison_data = {
        "FAISS": {
            "优点": ["高性能", "支持大规模数据", "丰富的索引类型", "可持久化"],
            "缺点": ["不支持元数据过滤", "内存占用较大"],
            "适用场景": ["大规模相似性搜索", "高性能要求", "离线处理"]
        },
        "Chroma": {
            "优点": ["支持元数据过滤", "易于使用", "支持持久化", "活跃开发"],
            "缺点": ["相对较新", "性能不如FAISS"],
            "适用场景": ["中小规模应用", "需要元数据过滤", "快速原型开发"]
        },
        "Pinecone": {
            "优点": ["托管服务", "高可用性", "自动扩展", "企业级功能"],
            "缺点": ["需要付费", "依赖网络", "数据在云端"],
            "适用场景": ["生产环境", "大规模应用", "企业用户"]
        },
        "Weaviate": {
            "优点": ["GraphQL API", "多模态支持", "丰富的功能", "开源"],
            "缺点": ["复杂度较高", "学习成本"],
            "适用场景": ["复杂查询", "多模态数据", "企业应用"]
        }
    }
    
    print("向量数据库对比:")
    for name, info in comparison_data.items():
        print(f"\n{name}:")
        print(f"  优点: {', '.join(info['优点'])}")
        print(f"  缺点: {', '.join(info['缺点'])}")
        print(f"  适用场景: {', '.join(info['适用场景'])}")
    
    print("\n选择建议:")
    print("1. 原型开发和学习：使用 Chroma 或 FAISS")
    print("2. 高性能需求：使用 FAISS")
    print("3. 生产环境：考虑 Pinecone 或 Weaviate")
    print("4. 元数据过滤需求：使用 Chroma 或 Weaviate")
    print()

def main():
    """主函数"""
    print("LangChain 向量存储学习")
    print("=" * 50)
    
    # 检查依赖
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  注意: 未检测到 OPENAI_API_KEY 环境变量")
        print("将使用模拟嵌入模型进行演示")
        print()
    
    # 运行演示
    demo_basic_vector_store()
    demo_similarity_search_with_scores()
    demo_metadata_filtering()
    demo_chroma_vector_store()
    demo_vector_store_operations()
    demo_custom_retriever()
    demo_vector_store_comparison()
    
    print("=" * 50)
    print("学习要点总结:")
    print("1. 向量存储是RAG系统的核心组件")
    print("2. 选择合适的嵌入模型很重要")
    print("3. 不同向量数据库有不同的特点")
    print("4. 元数据过滤可以提高检索精度")
    print("5. 混合检索策略通常效果更好")
    print("6. 生产环境需要考虑性能和可扩展性")

if __name__ == "__main__":
    main()