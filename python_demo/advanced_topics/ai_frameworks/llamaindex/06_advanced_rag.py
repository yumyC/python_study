"""
LlamaIndex 高级RAG技术详解

本文件介绍 LlamaIndex 中的高级RAG（检索增强生成）技术：
1. 多模态RAG
2. 分层检索
3. 查询重写和扩展
4. 结果融合和重排序
5. RAG评估和优化

学习目标：
- 掌握高级RAG技术的实现方法
- 理解多模态数据处理
- 学会优化检索和生成质量
- 了解RAG系统的评估方法
"""

import os
import time
from typing import List, Dict, Any, Optional, Tuple
import json

try:
    from llama_index.core import (
        VectorStoreIndex,
        Document,
        Settings,
        QueryBundle
    )
    from llama_index.core.llms import MockLLM
    from llama_index.core.schema import BaseNode, TextNode
    from llama_index.core.retrievers import BaseRetriever
    from llama_index.core.query_engine import BaseQueryEngine
    from llama_index.core.postprocessor import BaseNodePostprocessor
    
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

def demo_hierarchical_retrieval():
    """演示分层检索"""
    print("=== 分层检索演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    class HierarchicalRetriever(BaseRetriever):
        """分层检索器 - 先粗粒度后细粒度检索"""
        
        def __init__(self, 
                     coarse_index: VectorStoreIndex,
                     fine_index: VectorStoreIndex,
                     coarse_top_k: int = 10,
                     fine_top_k: int = 5):
            """
            初始化分层检索器
            
            Args:
                coarse_index: 粗粒度索引（文档级别）
                fine_index: 细粒度索引（段落级别）
                coarse_top_k: 粗检索返回数量
                fine_top_k: 细检索返回数量
            """
            super().__init__()
            self.coarse_index = coarse_index
            self.fine_index = fine_index
            self.coarse_top_k = coarse_top_k
            self.fine_top_k = fine_top_k
        
        def _retrieve(self, query_bundle: QueryBundle) -> List[BaseNode]:
            """执行分层检索"""
            # 第一层：粗粒度检索
            coarse_retriever = self.coarse_index.as_retriever(
                similarity_top_k=self.coarse_top_k
            )
            coarse_nodes = coarse_retriever.retrieve(query_bundle)
            
            # 提取相关文档ID
            relevant_doc_ids = set()
            for node in coarse_nodes:
                if 'doc_id' in node.metadata:
                    relevant_doc_ids.add(node.metadata['doc_id'])
            
            # 第二层：在相关文档内进行细粒度检索
            fine_retriever = self.fine_index.as_retriever(
                similarity_top_k=self.fine_top_k * 2  # 多检索一些，后面过滤
            )
            fine_nodes = fine_retriever.retrieve(query_bundle)
            
            # 过滤：只保留来自相关文档的细粒度结果
            filtered_nodes = []
            for node in fine_nodes:
                if node.metadata.get('doc_id') in relevant_doc_ids:
                    filtered_nodes.append(node)
                
                if len(filtered_nodes) >= self.fine_top_k:
                    break
            
            return filtered_nodes
    
    # 创建分层数据
    try:
        # 配置模型
        Settings.llm = MockLLM()
        Settings.embed_model = MockEmbedding()
        
        # 创建文档级数据（粗粒度）
        coarse_documents = [
            Document(
                text="Python编程语言概述：Python是一种高级编程语言，具有简洁的语法和强大的功能。",
                metadata={"doc_id": "doc_1", "type": "overview", "topic": "Python"}
            ),
            Document(
                text="机器学习基础：机器学习是人工智能的重要分支，包括监督学习、无监督学习等。",
                metadata={"doc_id": "doc_2", "type": "overview", "topic": "机器学习"}
            ),
            Document(
                text="Web开发技术：Web开发涉及前端和后端技术，需要掌握多种编程语言和框架。",
                metadata={"doc_id": "doc_3", "type": "overview", "topic": "Web开发"}
            )
        ]
        
        # 创建段落级数据（细粒度）
        fine_documents = [
            # Python相关段落
            Document(
                text="Python语法特点：Python使用缩进来表示代码块，语法简洁明了。",
                metadata={"doc_id": "doc_1", "type": "detail", "section": "语法"}
            ),
            Document(
                text="Python应用领域：Python广泛应用于Web开发、数据科学、人工智能等领域。",
                metadata={"doc_id": "doc_1", "type": "detail", "section": "应用"}
            ),
            Document(
                text="Python生态系统：Python拥有丰富的第三方库，如NumPy、Pandas、Django等。",
                metadata={"doc_id": "doc_1", "type": "detail", "section": "生态"}
            ),
            
            # 机器学习相关段落
            Document(
                text="监督学习：使用标记数据训练模型，包括分类和回归任务。",
                metadata={"doc_id": "doc_2", "type": "detail", "section": "监督学习"}
            ),
            Document(
                text="无监督学习：从未标记数据中发现模式，如聚类和降维。",
                metadata={"doc_id": "doc_2", "type": "detail", "section": "无监督学习"}
            ),
            
            # Web开发相关段落
            Document(
                text="前端技术：HTML、CSS、JavaScript是Web前端开发的基础技术。",
                metadata={"doc_id": "doc_3", "type": "detail", "section": "前端"}
            ),
            Document(
                text="后端技术：后端开发涉及服务器、数据库、API设计等方面。",
                metadata={"doc_id": "doc_3", "type": "detail", "section": "后端"}
            )
        ]
        
        # 创建索引
        coarse_index = VectorStoreIndex.from_documents(coarse_documents)
        fine_index = VectorStoreIndex.from_documents(fine_documents)
        
        # 创建分层检索器
        hierarchical_retriever = HierarchicalRetriever(
            coarse_index=coarse_index,
            fine_index=fine_index,
            coarse_top_k=2,
            fine_top_k=3
        )
        
        # 测试分层检索
        test_queries = [
            "Python的语法特点",
            "机器学习的类型",
            "Web开发需要什么技术"
        ]
        
        print("分层检索测试:")
        for query in test_queries:
            print(f"\n查询: {query}")
            
            query_bundle = QueryBundle(query_str=query)
            results = hierarchical_retriever.retrieve(query_bundle)
            
            print(f"检索结果 ({len(results)} 个):")
            for i, node in enumerate(results):
                doc_id = node.metadata.get('doc_id', '未知')
                section = node.metadata.get('section', '未知')
                print(f"  {i+1}. 文档{doc_id}-{section}: {node.text[:50]}...")
    
    except Exception as e:
        print(f"分层检索演示失败: {e}")
    
    print()

def demo_query_rewriting():
    """演示查询重写和扩展"""
    print("=== 查询重写和扩展演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    class QueryRewriter:
        """查询重写器"""
        
        def __init__(self):
            # 同义词词典
            self.synonyms = {
                "编程": ["程序设计", "代码编写", "软件开发"],
                "语言": ["编程语言", "程序语言"],
                "学习": ["掌握", "了解", "研究"],
                "框架": ["库", "工具包", "平台"],
                "开发": ["构建", "创建", "制作"],
                "数据": ["信息", "资料"],
                "算法": ["方法", "技术", "策略"]
            }
            
            # 查询扩展模板
            self.expansion_templates = [
                "{query}的特点",
                "{query}的应用",
                "{query}的优势",
                "如何使用{query}",
                "{query}的基础知识"
            ]
        
        def rewrite_query(self, query: str) -> List[str]:
            """重写查询"""
            rewritten_queries = [query]  # 包含原查询
            
            # 1. 同义词替换
            synonym_queries = self._generate_synonym_queries(query)
            rewritten_queries.extend(synonym_queries)
            
            # 2. 查询扩展
            expanded_queries = self._expand_query(query)
            rewritten_queries.extend(expanded_queries)
            
            # 3. 查询简化
            simplified_queries = self._simplify_query(query)
            rewritten_queries.extend(simplified_queries)
            
            # 去重
            unique_queries = list(set(rewritten_queries))
            
            return unique_queries[:5]  # 最多返回5个查询
        
        def _generate_synonym_queries(self, query: str) -> List[str]:
            """生成同义词查询"""
            synonym_queries = []
            words = query.split()
            
            for word in words:
                if word in self.synonyms:
                    for synonym in self.synonyms[word]:
                        new_query = query.replace(word, synonym)
                        if new_query != query:
                            synonym_queries.append(new_query)
            
            return synonym_queries[:2]  # 最多2个同义词查询
        
        def _expand_query(self, query: str) -> List[str]:
            """扩展查询"""
            expanded_queries = []
            
            # 使用扩展模板
            for template in self.expansion_templates[:2]:  # 只用前2个模板
                expanded_query = template.format(query=query)
                expanded_queries.append(expanded_query)
            
            return expanded_queries
        
        def _simplify_query(self, query: str) -> List[str]:
            """简化查询"""
            simplified_queries = []
            
            # 提取关键词
            words = query.split()
            if len(words) > 2:
                # 取前两个词
                simplified = " ".join(words[:2])
                simplified_queries.append(simplified)
                
                # 取最后两个词
                if len(words) > 2:
                    simplified = " ".join(words[-2:])
                    simplified_queries.append(simplified)
            
            return simplified_queries
    
    class MultiQueryRetriever(BaseRetriever):
        """多查询检索器"""
        
        def __init__(self, 
                     base_retriever: BaseRetriever,
                     query_rewriter: QueryRewriter,
                     top_k_per_query: int = 3):
            """
            初始化多查询检索器
            
            Args:
                base_retriever: 基础检索器
                query_rewriter: 查询重写器
                top_k_per_query: 每个查询返回的结果数
            """
            super().__init__()
            self.base_retriever = base_retriever
            self.query_rewriter = query_rewriter
            self.top_k_per_query = top_k_per_query
        
        def _retrieve(self, query_bundle: QueryBundle) -> List[BaseNode]:
            """执行多查询检索"""
            original_query = query_bundle.query_str
            
            # 生成重写查询
            rewritten_queries = self.query_rewriter.rewrite_query(original_query)
            
            # 对每个查询进行检索
            all_nodes = []
            query_results = {}
            
            for query in rewritten_queries:
                query_bundle_new = QueryBundle(query_str=query)
                nodes = self.base_retriever.retrieve(query_bundle_new)[:self.top_k_per_query]
                
                query_results[query] = nodes
                all_nodes.extend(nodes)
            
            # 去重和重排序
            unique_nodes = self._deduplicate_and_rerank(all_nodes, original_query)
            
            return unique_nodes
        
        def _deduplicate_and_rerank(self, 
                                  nodes: List[BaseNode], 
                                  original_query: str) -> List[BaseNode]:
            """去重和重排序"""
            # 简单去重（基于文本内容）
            seen_texts = set()
            unique_nodes = []
            
            for node in nodes:
                if hasattr(node, 'text'):
                    text_hash = hash(node.text)
                    if text_hash not in seen_texts:
                        seen_texts.add(text_hash)
                        unique_nodes.append(node)
            
            # 简单重排序（基于与原查询的相关性）
            def relevance_score(node):
                if not hasattr(node, 'text'):
                    return 0
                
                query_words = set(original_query.lower().split())
                node_words = set(node.text.lower().split())
                intersection = query_words.intersection(node_words)
                
                return len(intersection) / len(query_words) if query_words else 0
            
            unique_nodes.sort(key=relevance_score, reverse=True)
            
            return unique_nodes[:5]  # 返回前5个
    
    # 测试查询重写
    try:
        # 配置模型
        Settings.llm = MockLLM()
        Settings.embed_model = MockEmbedding()
        
        # 创建测试文档
        documents = [
            Document(text="Python是一种编程语言，语法简洁，适合初学者学习。"),
            Document(text="机器学习算法可以从数据中自动学习模式和规律。"),
            Document(text="Web开发框架如Django和Flask简化了网站构建过程。"),
            Document(text="数据科学结合统计学和程序设计来分析信息。"),
            Document(text="人工智能技术正在改变各个行业的工作方式。")
        ]
        
        # 创建索引和检索器
        index = VectorStoreIndex.from_documents(documents)
        base_retriever = index.as_retriever(similarity_top_k=3)
        
        # 创建查询重写器和多查询检索器
        query_rewriter = QueryRewriter()
        multi_query_retriever = MultiQueryRetriever(
            base_retriever=base_retriever,
            query_rewriter=query_rewriter,
            top_k_per_query=2
        )
        
        # 测试查询重写
        test_query = "Python编程学习"
        
        print("查询重写测试:")
        print(f"原始查询: {test_query}")
        
        rewritten_queries = query_rewriter.rewrite_query(test_query)
        print(f"重写查询:")
        for i, query in enumerate(rewritten_queries):
            print(f"  {i+1}. {query}")
        
        # 测试多查询检索
        print(f"\n多查询检索结果:")
        query_bundle = QueryBundle(query_str=test_query)
        results = multi_query_retriever.retrieve(query_bundle)
        
        for i, node in enumerate(results):
            print(f"  {i+1}. {node.text[:60]}...")
    
    except Exception as e:
        print(f"查询重写演示失败: {e}")
    
    print()

def demo_result_fusion():
    """演示结果融合和重排序"""
    print("=== 结果融合和重排序演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    class ResultFuser:
        """结果融合器"""
        
        def __init__(self, fusion_method: str = "rrf"):
            """
            初始化结果融合器
            
            Args:
                fusion_method: 融合方法 ('rrf', 'weighted', 'borda')
            """
            self.fusion_method = fusion_method
        
        def fuse_results(self, 
                        result_lists: List[List[BaseNode]], 
                        weights: Optional[List[float]] = None) -> List[BaseNode]:
            """
            融合多个结果列表
            
            Args:
                result_lists: 多个检索结果列表
                weights: 各列表的权重
            
            Returns:
                融合后的结果列表
            """
            if not result_lists:
                return []
            
            if self.fusion_method == "rrf":
                return self._reciprocal_rank_fusion(result_lists)
            elif self.fusion_method == "weighted":
                return self._weighted_fusion(result_lists, weights)
            elif self.fusion_method == "borda":
                return self._borda_count_fusion(result_lists)
            else:
                raise ValueError(f"不支持的融合方法: {self.fusion_method}")
        
        def _reciprocal_rank_fusion(self, result_lists: List[List[BaseNode]]) -> List[BaseNode]:
            """倒数排名融合 (Reciprocal Rank Fusion)"""
            node_scores = {}
            k = 60  # RRF参数
            
            for result_list in result_lists:
                for rank, node in enumerate(result_list):
                    node_id = self._get_node_id(node)
                    
                    if node_id not in node_scores:
                        node_scores[node_id] = {
                            'node': node,
                            'score': 0.0
                        }
                    
                    # RRF分数计算
                    rrf_score = 1.0 / (k + rank + 1)
                    node_scores[node_id]['score'] += rrf_score
            
            # 按分数排序
            sorted_items = sorted(
                node_scores.values(),
                key=lambda x: x['score'],
                reverse=True
            )
            
            return [item['node'] for item in sorted_items]
        
        def _weighted_fusion(self, 
                           result_lists: List[List[BaseNode]], 
                           weights: Optional[List[float]]) -> List[BaseNode]:
            """加权融合"""
            if weights is None:
                weights = [1.0] * len(result_lists)
            
            if len(weights) != len(result_lists):
                raise ValueError("权重数量必须与结果列表数量相同")
            
            node_scores = {}
            
            for i, result_list in enumerate(result_lists):
                weight = weights[i]
                
                for rank, node in enumerate(result_list):
                    node_id = self._get_node_id(node)
                    
                    if node_id not in node_scores:
                        node_scores[node_id] = {
                            'node': node,
                            'score': 0.0
                        }
                    
                    # 加权分数计算（排名越靠前分数越高）
                    rank_score = (len(result_list) - rank) / len(result_list)
                    weighted_score = weight * rank_score
                    node_scores[node_id]['score'] += weighted_score
            
            # 按分数排序
            sorted_items = sorted(
                node_scores.values(),
                key=lambda x: x['score'],
                reverse=True
            )
            
            return [item['node'] for item in sorted_items]
        
        def _borda_count_fusion(self, result_lists: List[List[BaseNode]]) -> List[BaseNode]:
            """Borda计数融合"""
            node_scores = {}
            
            for result_list in result_lists:
                max_score = len(result_list)
                
                for rank, node in enumerate(result_list):
                    node_id = self._get_node_id(node)
                    
                    if node_id not in node_scores:
                        node_scores[node_id] = {
                            'node': node,
                            'score': 0
                        }
                    
                    # Borda分数计算
                    borda_score = max_score - rank
                    node_scores[node_id]['score'] += borda_score
            
            # 按分数排序
            sorted_items = sorted(
                node_scores.values(),
                key=lambda x: x['score'],
                reverse=True
            )
            
            return [item['node'] for item in sorted_items]
        
        def _get_node_id(self, node: BaseNode) -> str:
            """获取节点ID"""
            if hasattr(node, 'node_id') and node.node_id:
                return node.node_id
            elif hasattr(node, 'text'):
                # 使用文本内容的哈希作为ID
                return str(hash(node.text))
            else:
                return str(id(node))
    
    # 测试结果融合
    try:
        # 创建模拟检索结果
        def create_test_node(text: str, node_id: str = None) -> TextNode:
            return TextNode(
                text=text,
                id_=node_id or str(hash(text))
            )
        
        # 模拟三个不同检索器的结果
        result_list_1 = [
            create_test_node("Python是一种编程语言", "node_1"),
            create_test_node("机器学习算法很重要", "node_2"),
            create_test_node("Web开发需要多种技术", "node_3")
        ]
        
        result_list_2 = [
            create_test_node("机器学习算法很重要", "node_2"),  # 重复
            create_test_node("Python适合数据科学", "node_4"),
            create_test_node("深度学习是AI分支", "node_5")
        ]
        
        result_list_3 = [
            create_test_node("Web开发需要多种技术", "node_3"),  # 重复
            create_test_node("Python适合数据科学", "node_4"),   # 重复
            create_test_node("算法优化很关键", "node_6")
        ]
        
        result_lists = [result_list_1, result_list_2, result_list_3]
        
        print("原始检索结果:")
        for i, result_list in enumerate(result_lists):
            print(f"检索器 {i+1}:")
            for j, node in enumerate(result_list):
                print(f"  {j+1}. {node.text}")
        
        # 测试不同融合方法
        fusion_methods = ["rrf", "weighted", "borda"]
        
        for method in fusion_methods:
            print(f"\n{method.upper()} 融合结果:")
            
            fuser = ResultFuser(fusion_method=method)
            
            if method == "weighted":
                # 给不同检索器不同权重
                weights = [0.5, 0.3, 0.2]
                fused_results = fuser.fuse_results(result_lists, weights)
            else:
                fused_results = fuser.fuse_results(result_lists)
            
            for i, node in enumerate(fused_results):
                print(f"  {i+1}. {node.text}")
    
    except Exception as e:
        print(f"结果融合演示失败: {e}")
    
    print()

def demo_rag_evaluation():
    """演示RAG评估"""
    print("=== RAG评估演示 ===")
    
    print("RAG评估指标:")
    
    evaluation_metrics = {
        "检索质量指标": {
            "召回率 (Recall)": "检索到的相关文档占所有相关文档的比例",
            "精确率 (Precision)": "检索到的相关文档占所有检索文档的比例",
            "F1分数": "精确率和召回率的调和平均数",
            "MRR (Mean Reciprocal Rank)": "平均倒数排名",
            "NDCG": "归一化折扣累积增益"
        },
        "生成质量指标": {
            "BLEU": "与参考答案的n-gram重叠度",
            "ROUGE": "与参考答案的召回率导向指标",
            "BERTScore": "基于BERT的语义相似度",
            "人工评估": "流畅性、相关性、准确性"
        },
        "端到端指标": {
            "答案准确性": "生成答案的事实准确性",
            "答案完整性": "答案是否完整回答了问题",
            "引用质量": "引用的文档是否支持答案",
            "用户满意度": "用户对答案的满意程度"
        }
    }
    
    for category, metrics in evaluation_metrics.items():
        print(f"\n{category}:")
        for metric, description in metrics.items():
            print(f"  - {metric}: {description}")
    
    # 评估框架示例
    print("\n评估框架示例:")
    
    class RAGEvaluator:
        """RAG评估器"""
        
        def __init__(self):
            self.evaluation_results = {}
        
        def evaluate_retrieval(self, 
                             retrieved_docs: List[str],
                             relevant_docs: List[str]) -> Dict[str, float]:
            """评估检索质量"""
            retrieved_set = set(retrieved_docs)
            relevant_set = set(relevant_docs)
            
            # 计算交集
            intersection = retrieved_set.intersection(relevant_set)
            
            # 计算指标
            precision = len(intersection) / len(retrieved_set) if retrieved_set else 0
            recall = len(intersection) / len(relevant_set) if relevant_set else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            return {
                "precision": precision,
                "recall": recall,
                "f1": f1
            }
        
        def evaluate_generation(self, 
                              generated_answer: str,
                              reference_answer: str) -> Dict[str, float]:
            """评估生成质量"""
            # 简单的词汇重叠评估
            gen_words = set(generated_answer.lower().split())
            ref_words = set(reference_answer.lower().split())
            
            intersection = gen_words.intersection(ref_words)
            
            precision = len(intersection) / len(gen_words) if gen_words else 0
            recall = len(intersection) / len(ref_words) if ref_words else 0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            return {
                "word_precision": precision,
                "word_recall": recall,
                "word_f1": f1
            }
        
        def comprehensive_evaluation(self, 
                                   test_cases: List[Dict]) -> Dict[str, float]:
            """综合评估"""
            retrieval_scores = []
            generation_scores = []
            
            for case in test_cases:
                # 检索评估
                ret_score = self.evaluate_retrieval(
                    case["retrieved_docs"],
                    case["relevant_docs"]
                )
                retrieval_scores.append(ret_score)
                
                # 生成评估
                gen_score = self.evaluate_generation(
                    case["generated_answer"],
                    case["reference_answer"]
                )
                generation_scores.append(gen_score)
            
            # 计算平均分数
            avg_retrieval = {
                metric: sum(score[metric] for score in retrieval_scores) / len(retrieval_scores)
                for metric in retrieval_scores[0].keys()
            }
            
            avg_generation = {
                metric: sum(score[metric] for score in generation_scores) / len(generation_scores)
                for metric in generation_scores[0].keys()
            }
            
            return {
                "retrieval": avg_retrieval,
                "generation": avg_generation
            }
    
    # 示例评估
    evaluator = RAGEvaluator()
    
    # 模拟测试用例
    test_cases = [
        {
            "query": "什么是Python？",
            "retrieved_docs": ["doc1", "doc2", "doc3"],
            "relevant_docs": ["doc1", "doc4"],
            "generated_answer": "Python是一种编程语言",
            "reference_answer": "Python是一种高级编程语言"
        },
        {
            "query": "机器学习的类型",
            "retrieved_docs": ["doc2", "doc5"],
            "relevant_docs": ["doc2", "doc5", "doc6"],
            "generated_answer": "机器学习包括监督学习和无监督学习",
            "reference_answer": "机器学习主要包括监督学习、无监督学习和强化学习"
        }
    ]
    
    results = evaluator.comprehensive_evaluation(test_cases)
    
    print("评估结果:")
    print(f"检索质量: {results['retrieval']}")
    print(f"生成质量: {results['generation']}")
    
    print("\n评估最佳实践:")
    best_practices = [
        "建立标准化的评估数据集",
        "使用多种评估指标",
        "结合自动评估和人工评估",
        "定期更新评估标准",
        "A/B测试比较不同方法",
        "关注用户反馈和实际效果"
    ]
    
    for i, practice in enumerate(best_practices, 1):
        print(f"{i}. {practice}")
    
    print()

def main():
    """主函数"""
    print("LlamaIndex 高级RAG技术学习")
    print("=" * 50)
    
    # 检查依赖
    if not LLAMAINDEX_AVAILABLE:
        print("⚠️  LlamaIndex 未安装")
        print("请运行: pip install llama-index")
        print()
    
    # 运行演示
    demo_hierarchical_retrieval()
    demo_query_rewriting()
    demo_result_fusion()
    demo_rag_evaluation()
    
    print("=" * 50)
    print("学习要点总结:")
    print("1. 分层检索提高大规模数据的检索效率")
    print("2. 查询重写和扩展增强检索召回率")
    print("3. 结果融合技术提升检索质量")
    print("4. 多模态RAG处理复杂数据类型")
    print("5. 评估体系确保RAG系统质量")
    print("6. 持续优化是RAG系统成功的关键")

if __name__ == "__main__":
    main()