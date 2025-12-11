"""
LlamaIndex 自定义组件详解

本文件介绍 LlamaIndex 中的自定义组件开发：
1. 自定义数据加载器
2. 自定义节点解析器
3. 自定义检索器
4. 自定义响应合成器
5. 自定义评估器

学习目标：
- 掌握自定义组件的开发方法
- 理解组件接口和扩展点
- 学会集成第三方服务
- 了解组件测试和调试技术
"""

import os
import json
import tempfile
from typing import List, Dict, Any, Optional, Sequence
from abc import ABC, abstractmethod

try:
    from llama_index.core import Document, VectorStoreIndex, Settings
    from llama_index.core.readers.base import BaseReader
    from llama_index.core.node_parser.interface import NodeParser
    from llama_index.core.schema import BaseNode, TextNode, NodeRelationship, RelatedNodeInfo
    from llama_index.core.retrievers import BaseRetriever
    from llama_index.core.response_synthesizers.base import BaseSynthesizer
    from llama_index.core.llms import MockLLM
    from llama_index.core.base.response.schema import Response
    from llama_index.core.prompts import PromptTemplate
    
    LLAMAINDEX_AVAILABLE = True
except ImportError:
    print("LlamaIndex 未安装，请运行: pip install llama-index")
    LLAMAINDEX_AVAILABLE = False

def demo_custom_data_loader():
    """演示自定义数据加载器"""
    print("=== 自定义数据加载器演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    class ConfigFileReader(BaseReader):
        """自定义配置文件读取器"""
        
        def __init__(self, config_type: str = "ini"):
            """
            初始化配置文件读取器
            
            Args:
                config_type: 配置文件类型 ('ini', 'yaml', 'json')
            """
            self.config_type = config_type.lower()
        
        def load_data(self, file_path: str, extra_info: Optional[Dict] = None) -> List[Document]:
            """
            加载配置文件数据
            
            Args:
                file_path: 配置文件路径
                extra_info: 额外信息
            
            Returns:
                文档列表
            """
            documents = []
            
            try:
                if self.config_type == "json":
                    documents = self._load_json_config(file_path, extra_info)
                elif self.config_type == "ini":
                    documents = self._load_ini_config(file_path, extra_info)
                else:
                    raise ValueError(f"不支持的配置文件类型: {self.config_type}")
                
            except Exception as e:
                print(f"加载配置文件失败: {e}")
            
            return documents
        
        def _load_json_config(self, file_path: str, extra_info: Optional[Dict]) -> List[Document]:
            """加载JSON配置文件"""
            documents = []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            # 递归处理配置项
            def process_config_item(key: str, value: Any, path: str = "") -> str:
                current_path = f"{path}.{key}" if path else key
                
                if isinstance(value, dict):
                    content = f"配置节: {current_path}\n"
                    for sub_key, sub_value in value.items():
                        content += process_config_item(sub_key, sub_value, current_path)
                    return content
                elif isinstance(value, list):
                    return f"{current_path}: {', '.join(map(str, value))}\n"
                else:
                    return f"{current_path}: {value}\n"
            
            # 为每个顶级配置节创建文档
            for section_key, section_value in config_data.items():
                content = process_config_item(section_key, section_value)
                
                metadata = {
                    "source": file_path,
                    "type": "config",
                    "format": "json",
                    "section": section_key
                }
                
                if extra_info:
                    metadata.update(extra_info)
                
                doc = Document(text=content.strip(), metadata=metadata)
                documents.append(doc)
            
            return documents
        
        def _load_ini_config(self, file_path: str, extra_info: Optional[Dict]) -> List[Document]:
            """加载INI配置文件"""
            import configparser
            
            documents = []
            config = configparser.ConfigParser()
            config.read(file_path, encoding='utf-8')
            
            for section_name in config.sections():
                content = f"配置节: {section_name}\n"
                
                for key, value in config[section_name].items():
                    content += f"{key}: {value}\n"
                
                metadata = {
                    "source": file_path,
                    "type": "config",
                    "format": "ini",
                    "section": section_name
                }
                
                if extra_info:
                    metadata.update(extra_info)
                
                doc = Document(text=content.strip(), metadata=metadata)
                documents.append(doc)
            
            return documents
    
    # 测试自定义加载器
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建测试配置文件
        json_config = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "myapp",
                "credentials": {
                    "username": "admin",
                    "password": "secret"
                }
            },
            "redis": {
                "host": "localhost",
                "port": 6379,
                "db": 0
            },
            "logging": {
                "level": "INFO",
                "handlers": ["console", "file"]
            }
        }
        
        json_file = os.path.join(temp_dir, "config.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_config, f, ensure_ascii=False, indent=2)
        
        # 使用自定义加载器
        try:
            reader = ConfigFileReader(config_type="json")
            documents = reader.load_data(json_file, extra_info={"environment": "development"})
            
            print(f"成功加载 {len(documents)} 个配置文档")
            
            for doc in documents:
                print(f"\n配置节: {doc.metadata['section']}")
                print(f"内容: {doc.text[:100]}...")
                print(f"元数据: {doc.metadata}")
        
        except Exception as e:
            print(f"自定义加载器测试失败: {e}")
    
    print()

def demo_custom_node_parser():
    """演示自定义节点解析器"""
    print("=== 自定义节点解析器演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    class SemanticNodeParser(NodeParser):
        """语义节点解析器 - 基于语义边界分割文本"""
        
        def __init__(self, 
                     max_chunk_size: int = 500,
                     semantic_separators: Optional[List[str]] = None):
            """
            初始化语义节点解析器
            
            Args:
                max_chunk_size: 最大块大小
                semantic_separators: 语义分隔符列表
            """
            super().__init__()
            self.max_chunk_size = max_chunk_size
            self.semantic_separators = semantic_separators or [
                "\n\n",  # 段落分隔
                "。\n",   # 句子结束
                "！\n",   # 感叹句结束
                "？\n",   # 疑问句结束
                "；",     # 分号
                "，"      # 逗号（最后选择）
            ]
        
        def get_nodes_from_documents(self, 
                                   documents: Sequence[Document],
                                   show_progress: bool = False) -> List[BaseNode]:
            """从文档生成节点"""
            nodes = []
            
            for doc_idx, document in enumerate(documents):
                doc_nodes = self._parse_document(document, doc_idx)
                nodes.extend(doc_nodes)
            
            return nodes
        
        def _parse_document(self, document: Document, doc_idx: int) -> List[TextNode]:
            """解析单个文档"""
            text = document.text
            chunks = self._split_by_semantic_boundaries(text)
            
            nodes = []
            for chunk_idx, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                
                node_id = f"node_{doc_idx}_{chunk_idx}"
                
                node = TextNode(
                    text=chunk.strip(),
                    id_=node_id,
                    metadata=document.metadata.copy()
                )
                
                # 添加块级元数据
                node.metadata.update({
                    "chunk_id": chunk_idx,
                    "chunk_size": len(chunk),
                    "doc_id": doc_idx
                })
                
                nodes.append(node)
            
            # 建立节点间的关系
            for i, node in enumerate(nodes):
                if i > 0:
                    # 前一个节点
                    node.relationships[NodeRelationship.PREVIOUS] = RelatedNodeInfo(
                        node_id=nodes[i-1].node_id
                    )
                if i < len(nodes) - 1:
                    # 后一个节点
                    node.relationships[NodeRelationship.NEXT] = RelatedNodeInfo(
                        node_id=nodes[i+1].node_id
                    )
                
                # 源文档关系
                node.relationships[NodeRelationship.SOURCE] = RelatedNodeInfo(
                    node_id=f"doc_{doc_idx}"
                )
            
            return nodes
        
        def _split_by_semantic_boundaries(self, text: str) -> List[str]:
            """基于语义边界分割文本"""
            chunks = []
            current_chunk = ""
            
            # 首先尝试按段落分割
            paragraphs = text.split("\n\n")
            
            for paragraph in paragraphs:
                if len(current_chunk) + len(paragraph) <= self.max_chunk_size:
                    current_chunk += paragraph + "\n\n"
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                        current_chunk = ""
                    
                    # 如果段落太长，进一步分割
                    if len(paragraph) > self.max_chunk_size:
                        sub_chunks = self._split_long_paragraph(paragraph)
                        chunks.extend(sub_chunks)
                    else:
                        current_chunk = paragraph + "\n\n"
            
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            return chunks
        
        def _split_long_paragraph(self, paragraph: str) -> List[str]:
            """分割长段落"""
            chunks = []
            current_chunk = ""
            
            # 按句子分割
            sentences = self._split_sentences(paragraph)
            
            for sentence in sentences:
                if len(current_chunk) + len(sentence) <= self.max_chunk_size:
                    current_chunk += sentence
                else:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                        current_chunk = ""
                    
                    # 如果单个句子太长，强制分割
                    if len(sentence) > self.max_chunk_size:
                        force_chunks = self._force_split(sentence)
                        chunks.extend(force_chunks)
                    else:
                        current_chunk = sentence
            
            if current_chunk:
                chunks.append(current_chunk.strip())
            
            return chunks
        
        def _split_sentences(self, text: str) -> List[str]:
            """分割句子"""
            import re
            # 简单的句子分割正则
            sentence_pattern = r'[。！？.!?]+\s*'
            sentences = re.split(sentence_pattern, text)
            
            # 重新添加标点符号
            result = []
            for i, sentence in enumerate(sentences[:-1]):  # 最后一个通常是空的
                if sentence.strip():
                    # 找到对应的标点符号
                    matches = list(re.finditer(sentence_pattern, text))
                    if i < len(matches):
                        punctuation = matches[i].group()
                        result.append(sentence + punctuation)
                    else:
                        result.append(sentence)
            
            return result
        
        def _force_split(self, text: str) -> List[str]:
            """强制分割文本"""
            chunks = []
            start = 0
            
            while start < len(text):
                end = start + self.max_chunk_size
                if end >= len(text):
                    chunks.append(text[start:])
                    break
                
                # 尝试在单词边界分割
                while end > start and text[end] not in [' ', '\n', '\t']:
                    end -= 1
                
                if end == start:  # 没找到合适的分割点
                    end = start + self.max_chunk_size
                
                chunks.append(text[start:end])
                start = end
            
            return chunks
    
    # 测试自定义节点解析器
    try:
        # 创建测试文档
        long_document = Document(
            text="""
            人工智能的发展历程

            人工智能（AI）的发展可以分为几个重要阶段。第一阶段是符号主义时期（1950-1970年），这个时期的研究主要集中在符号推理和专家系统上。科学家们试图通过编程让计算机模拟人类的逻辑思维过程。

            第二阶段是机器学习兴起（1980-2000年）。随着计算能力的提升，机器学习算法开始受到关注。神经网络、决策树、支持向量机等算法得到了发展。这个时期的特点是从规则驱动转向数据驱动。

            第三阶段是深度学习革命（2000年至今）。深度学习的突破带来了人工智能的新一轮发展。卷积神经网络在图像识别领域取得突破，循环神经网络在自然语言处理方面表现出色，Transformer架构更是推动了大语言模型的发展。

            未来展望：人工智能将继续快速发展，在更多领域发挥重要作用。同时，我们也需要关注AI的伦理问题、安全问题和社会影响。
            """,
            metadata={"source": "ai_history.txt", "category": "technology"}
        )
        
        # 使用自定义解析器
        parser = SemanticNodeParser(max_chunk_size=200)
        nodes = parser.get_nodes_from_documents([long_document])
        
        print(f"语义节点解析结果: {len(nodes)} 个节点")
        
        for i, node in enumerate(nodes):
            print(f"\n节点 {i+1}:")
            print(f"  ID: {node.node_id}")
            print(f"  大小: {len(node.text)} 字符")
            print(f"  内容: {node.text[:80]}...")
            print(f"  关系: {list(node.relationships.keys())}")
    
    except Exception as e:
        print(f"自定义节点解析器测试失败: {e}")
    
    print()

def demo_custom_retriever():
    """演示自定义检索器"""
    print("=== 自定义检索器演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    class HybridRetriever(BaseRetriever):
        """混合检索器 - 结合向量搜索和关键词匹配"""
        
        def __init__(self, 
                     vector_index: VectorStoreIndex,
                     vector_top_k: int = 5,
                     keyword_weight: float = 0.3,
                     vector_weight: float = 0.7):
            """
            初始化混合检索器
            
            Args:
                vector_index: 向量索引
                vector_top_k: 向量搜索返回数量
                keyword_weight: 关键词匹配权重
                vector_weight: 向量搜索权重
            """
            super().__init__()
            self.vector_index = vector_index
            self.vector_top_k = vector_top_k
            self.keyword_weight = keyword_weight
            self.vector_weight = vector_weight
            
            # 获取所有节点用于关键词搜索
            self.all_nodes = list(vector_index.docstore.docs.values())
        
        def _retrieve(self, query_bundle) -> List[BaseNode]:
            """执行混合检索"""
            query_str = query_bundle.query_str
            
            # 1. 向量搜索
            vector_retriever = self.vector_index.as_retriever(
                similarity_top_k=self.vector_top_k
            )
            vector_nodes = vector_retriever.retrieve(query_bundle)
            
            # 2. 关键词搜索
            keyword_nodes = self._keyword_search(query_str)
            
            # 3. 合并和重新排序
            hybrid_nodes = self._merge_and_rerank(
                query_str, vector_nodes, keyword_nodes
            )
            
            return hybrid_nodes
        
        def _keyword_search(self, query: str) -> List[BaseNode]:
            """关键词搜索"""
            query_words = set(query.lower().split())
            scored_nodes = []
            
            for node in self.all_nodes:
                if hasattr(node, 'text'):
                    node_words = set(node.text.lower().split())
                    
                    # 计算关键词匹配分数
                    intersection = query_words.intersection(node_words)
                    if intersection:
                        score = len(intersection) / len(query_words)
                        scored_nodes.append((node, score))
            
            # 按分数排序
            scored_nodes.sort(key=lambda x: x[1], reverse=True)
            
            # 返回前5个
            return [node for node, score in scored_nodes[:5]]
        
        def _merge_and_rerank(self, 
                            query: str,
                            vector_nodes: List[BaseNode], 
                            keyword_nodes: List[BaseNode]) -> List[BaseNode]:
            """合并和重新排序结果"""
            # 创建节点分数字典
            node_scores = {}
            
            # 向量搜索分数
            for i, node in enumerate(vector_nodes):
                vector_score = (len(vector_nodes) - i) / len(vector_nodes)
                node_id = node.node_id
                node_scores[node_id] = {
                    'node': node,
                    'vector_score': vector_score,
                    'keyword_score': 0.0
                }
            
            # 关键词搜索分数
            for i, node in enumerate(keyword_nodes):
                keyword_score = (len(keyword_nodes) - i) / len(keyword_nodes)
                node_id = node.node_id
                
                if node_id in node_scores:
                    node_scores[node_id]['keyword_score'] = keyword_score
                else:
                    node_scores[node_id] = {
                        'node': node,
                        'vector_score': 0.0,
                        'keyword_score': keyword_score
                    }
            
            # 计算混合分数
            for node_id, scores in node_scores.items():
                hybrid_score = (
                    self.vector_weight * scores['vector_score'] +
                    self.keyword_weight * scores['keyword_score']
                )
                scores['hybrid_score'] = hybrid_score
            
            # 按混合分数排序
            sorted_nodes = sorted(
                node_scores.values(),
                key=lambda x: x['hybrid_score'],
                reverse=True
            )
            
            # 返回前5个节点
            return [item['node'] for item in sorted_nodes[:5]]
    
    # 测试自定义检索器
    try:
        # 配置模型
        Settings.llm = MockLLM()
        
        # 模拟嵌入模型
        class MockEmbedding:
            def get_text_embedding(self, text: str) -> List[float]:
                import hashlib
                import numpy as np
                hash_obj = hashlib.md5(text.encode())
                seed = int(hash_obj.hexdigest()[:8], 16)
                np.random.seed(seed)
                return np.random.normal(0, 1, 384).tolist()
        
        Settings.embed_model = MockEmbedding()
        
        # 创建测试文档
        documents = [
            Document(
                text="Python是一种高级编程语言，广泛用于Web开发和数据科学。",
                metadata={"topic": "Python"}
            ),
            Document(
                text="机器学习是人工智能的重要分支，Python在机器学习领域应用广泛。",
                metadata={"topic": "机器学习"}
            ),
            Document(
                text="Web开发可以使用多种编程语言，Python的Flask和Django是流行的框架。",
                metadata={"topic": "Web开发"}
            ),
            Document(
                text="数据科学需要统计学知识和编程技能，Python是数据科学家的首选语言。",
                metadata={"topic": "数据科学"}
            )
        ]
        
        # 创建向量索引
        index = VectorStoreIndex.from_documents(documents)
        
        # 创建混合检索器
        hybrid_retriever = HybridRetriever(
            vector_index=index,
            vector_top_k=3,
            keyword_weight=0.4,
            vector_weight=0.6
        )
        
        # 测试检索
        from llama_index.core.schema import QueryBundle
        
        test_queries = [
            "Python编程语言",
            "机器学习应用",
            "Web开发框架"
        ]
        
        print("混合检索器测试:")
        for query in test_queries:
            print(f"\n查询: {query}")
            
            query_bundle = QueryBundle(query_str=query)
            retrieved_nodes = hybrid_retriever.retrieve(query_bundle)
            
            print(f"检索到 {len(retrieved_nodes)} 个节点:")
            for i, node in enumerate(retrieved_nodes):
                topic = node.metadata.get('topic', '未知')
                print(f"  {i+1}. {topic}: {node.text[:50]}...")
    
    except Exception as e:
        print(f"自定义检索器测试失败: {e}")
    
    print()

def demo_custom_response_synthesizer():
    """演示自定义响应合成器"""
    print("=== 自定义响应合成器演示 ===")
    
    if not LLAMAINDEX_AVAILABLE:
        print("需要安装 LlamaIndex 才能运行此演示")
        return
    
    class StructuredResponseSynthesizer(BaseSynthesizer):
        """结构化响应合成器 - 生成格式化的回答"""
        
        def __init__(self, 
                     llm=None,
                     response_template: Optional[str] = None):
            """
            初始化结构化响应合成器
            
            Args:
                llm: 语言模型
                response_template: 响应模板
            """
            super().__init__(llm=llm)
            
            self.response_template = response_template or """
基于提供的信息，我来回答您的问题：

问题：{query}

回答：
{answer}

参考信息：
{sources}

置信度：{confidence}

相关主题：{topics}
            """
        
        def synthesize(self, 
                      query: str,
                      nodes: List[BaseNode],
                      additional_source_nodes: Optional[List[BaseNode]] = None,
                      **response_kwargs) -> Response:
            """合成结构化响应"""
            
            if not nodes:
                return Response(
                    response="抱歉，我没有找到相关信息来回答您的问题。",
                    source_nodes=[]
                )
            
            # 提取信息
            context_info = self._extract_context_info(nodes)
            
            # 生成基础回答
            base_answer = self._generate_base_answer(query, context_info)
            
            # 计算置信度
            confidence = self._calculate_confidence(query, nodes)
            
            # 提取主题
            topics = self._extract_topics(nodes)
            
            # 格式化响应
            formatted_response = self.response_template.format(
                query=query,
                answer=base_answer,
                sources=self._format_sources(nodes),
                confidence=f"{confidence:.1%}",
                topics=", ".join(topics)
            )
            
            return Response(
                response=formatted_response,
                source_nodes=nodes
            )
        
        def _extract_context_info(self, nodes: List[BaseNode]) -> str:
            """提取上下文信息"""
            context_parts = []
            
            for i, node in enumerate(nodes):
                if hasattr(node, 'text'):
                    context_parts.append(f"信息{i+1}: {node.text}")
            
            return "\n".join(context_parts)
        
        def _generate_base_answer(self, query: str, context: str) -> str:
            """生成基础回答"""
            # 这里简化处理，实际应该调用LLM
            if "Python" in query:
                return "Python是一种功能强大的编程语言，具有简洁的语法和丰富的生态系统。"
            elif "机器学习" in query:
                return "机器学习是人工智能的重要分支，通过算法让计算机从数据中学习。"
            elif "Web开发" in query:
                return "Web开发涉及创建网站和Web应用程序，需要掌握多种技术。"
            else:
                return "根据提供的信息，我为您整理了相关内容。"
        
        def _calculate_confidence(self, query: str, nodes: List[BaseNode]) -> float:
            """计算置信度"""
            if not nodes:
                return 0.0
            
            # 简单的置信度计算
            query_words = set(query.lower().split())
            total_matches = 0
            total_words = 0
            
            for node in nodes:
                if hasattr(node, 'text'):
                    node_words = set(node.text.lower().split())
                    matches = len(query_words.intersection(node_words))
                    total_matches += matches
                    total_words += len(node_words)
            
            if total_words == 0:
                return 0.0
            
            # 基于匹配度和节点数量计算置信度
            match_ratio = total_matches / len(query_words) if query_words else 0
            node_factor = min(len(nodes) / 3, 1.0)  # 3个节点为满分
            
            confidence = (match_ratio * 0.7 + node_factor * 0.3)
            return min(confidence, 1.0)
        
        def _extract_topics(self, nodes: List[BaseNode]) -> List[str]:
            """提取主题"""
            topics = set()
            
            for node in nodes:
                if hasattr(node, 'metadata') and 'topic' in node.metadata:
                    topics.add(node.metadata['topic'])
            
            return list(topics) if topics else ["通用"]
        
        def _format_sources(self, nodes: List[BaseNode]) -> str:
            """格式化信息源"""
            sources = []
            
            for i, node in enumerate(nodes, 1):
                source_info = f"{i}. "
                
                if hasattr(node, 'metadata'):
                    if 'source' in node.metadata:
                        source_info += f"来源: {node.metadata['source']}"
                    elif 'topic' in node.metadata:
                        source_info += f"主题: {node.metadata['topic']}"
                    else:
                        source_info += "内部知识库"
                else:
                    source_info += "内部知识库"
                
                sources.append(source_info)
            
            return "\n".join(sources)
    
    # 测试自定义响应合成器
    try:
        # 创建测试节点
        test_nodes = [
            TextNode(
                text="Python是一种高级编程语言，语法简洁，功能强大。",
                metadata={"topic": "Python", "source": "programming_guide.txt"}
            ),
            TextNode(
                text="Python在数据科学和机器学习领域应用广泛。",
                metadata={"topic": "数据科学", "source": "data_science.txt"}
            )
        ]
        
        # 创建自定义合成器
        synthesizer = StructuredResponseSynthesizer()
        
        # 测试合成
        query = "Python有什么特点？"
        response = synthesizer.synthesize(query, test_nodes)
        
        print("结构化响应合成器测试:")
        print(f"查询: {query}")
        print(f"响应:\n{response.response}")
    
    except Exception as e:
        print(f"自定义响应合成器测试失败: {e}")
    
    print()

def demo_component_integration():
    """演示组件集成"""
    print("=== 组件集成演示 ===")
    
    print("自定义组件集成步骤:")
    print("1. 开发各个自定义组件")
    print("2. 测试组件的独立功能")
    print("3. 定义组件间的接口")
    print("4. 集成组件到完整系统")
    print("5. 端到端测试")
    print("6. 性能优化和调试")
    
    print("\n组件集成最佳实践:")
    practices = [
        "使用标准接口和抽象基类",
        "实现完整的错误处理",
        "添加详细的日志记录",
        "编写单元测试和集成测试",
        "提供配置选项和参数验证",
        "考虑性能和内存使用",
        "文档化组件的使用方法",
        "版本控制和向后兼容性"
    ]
    
    for i, practice in enumerate(practices, 1):
        print(f"{i}. {practice}")
    
    print("\n常见集成问题:")
    issues = {
        "接口不匹配": "确保组件实现正确的接口",
        "数据格式不一致": "统一数据格式和类型定义",
        "性能瓶颈": "识别和优化关键路径",
        "错误传播": "实现适当的错误处理机制",
        "配置冲突": "使用配置管理系统",
        "依赖问题": "明确声明和管理依赖关系"
    }
    
    for issue, solution in issues.items():
        print(f"- {issue}: {solution}")
    
    print()

def main():
    """主函数"""
    print("LlamaIndex 自定义组件学习")
    print("=" * 50)
    
    # 检查依赖
    if not LLAMAINDEX_AVAILABLE:
        print("⚠️  LlamaIndex 未安装")
        print("请运行: pip install llama-index")
        print()
    
    # 运行演示
    demo_custom_data_loader()
    demo_custom_node_parser()
    demo_custom_retriever()
    demo_custom_response_synthesizer()
    demo_component_integration()
    
    print("=" * 50)
    print("学习要点总结:")
    print("1. 自定义组件扩展了LlamaIndex的功能")
    print("2. 遵循标准接口确保兼容性")
    print("3. 组件设计要考虑可重用性和可测试性")
    print("4. 集成测试验证组件协作")
    print("5. 性能优化和错误处理很重要")
    print("6. 文档和示例帮助其他开发者使用")

if __name__ == "__main__":
    main()