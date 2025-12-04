"""
FastAPI 路由示例

演示如何使用路径参数、查询参数、参数验证和多种路由模式。

运行方式:
    uvicorn 02_routing:app --reload

访问文档:
    http://127.0.0.1:8000/docs
"""

from typing import Optional
from fastapi import FastAPI, Query, Path
from enum import Enum

app = FastAPI(title="路由示例 API", version="1.0.0")


# ============ 1. 基本路由 ============

@app.get("/")
def root():
    """根路径"""
    return {"message": "路由示例 API"}


@app.get("/items")
def list_items():
    """获取所有项目列表"""
    return {
        "items": [
            {"id": 1, "name": "Item 1"},
            {"id": 2, "name": "Item 2"},
            {"id": 3, "name": "Item 3"}
        ]
    }


# ============ 2. 路径参数 ============

@app.get("/items/{item_id}")
def get_item(item_id: int):
    """
    通过 ID 获取单个项目
    
    路径参数会自动进行类型转换和验证
    如果传入非整数，会返回 422 验证错误
    """
    return {
        "item_id": item_id,
        "name": f"Item {item_id}"
    }


# 路径参数验证
@app.get("/items-validated/{item_id}")
def get_item_validated(
    item_id: int = Path(
        ...,  # ... 表示必需参数
        title="项目 ID",
        description="要获取的项目的唯一标识符",
        ge=1,  # greater than or equal: 大于等于 1
        le=1000  # less than or equal: 小于等于 1000
    )
):
    """
    带验证的路径参数
    
    item_id 必须在 1-1000 之间
    """
    return {
        "item_id": item_id,
        "message": "验证通过"
    }


# 多个路径参数
@app.get("/users/{user_id}/items/{item_id}")
def get_user_item(user_id: int, item_id: int):
    """
    获取特定用户的特定项目
    
    可以在一个路径中使用多个参数
    """
    return {
        "user_id": user_id,
        "item_id": item_id,
        "message": f"用户 {user_id} 的项目 {item_id}"
    }


# ============ 3. 查询参数 ============

@app.get("/search")
def search_items(
    q: str,  # 必需的查询参数
    limit: int = 10,  # 可选参数，默认值为 10
    offset: int = 0  # 可选参数，默认值为 0
):
    """
    搜索项目
    
    查询参数示例:
    - /search?q=python
    - /search?q=python&limit=5
    - /search?q=python&limit=5&offset=10
    """
    return {
        "query": q,
        "limit": limit,
        "offset": offset,
        "results": [f"结果 {i}" for i in range(offset, offset + limit)]
    }


# 可选查询参数
@app.get("/filter")
def filter_items(
    category: Optional[str] = None,  # 完全可选的参数
    min_price: Optional[float] = None,
    max_price: Optional[float] = None
):
    """
    过滤项目
    
    所有参数都是可选的
    """
    filters = {}
    if category:
        filters["category"] = category
    if min_price is not None:
        filters["min_price"] = min_price
    if max_price is not None:
        filters["max_price"] = max_price
    
    return {
        "filters": filters,
        "message": "应用过滤器" if filters else "无过滤器"
    }


# 查询参数验证
@app.get("/products")
def get_products(
    page: int = Query(
        1,  # 默认值
        title="页码",
        description="要获取的页码",
        ge=1  # 必须大于等于 1
    ),
    page_size: int = Query(
        10,
        title="每页数量",
        description="每页显示的项目数量",
        ge=1,
        le=100  # 最多 100 条
    ),
    sort_by: Optional[str] = Query(
        None,
        title="排序字段",
        description="用于排序的字段名",
        regex="^(name|price|date)$"  # 只允许这三个值
    )
):
    """
    获取产品列表（带分页和排序）
    
    参数验证:
    - page: 必须 >= 1
    - page_size: 必须在 1-100 之间
    - sort_by: 只能是 name, price 或 date
    """
    return {
        "page": page,
        "page_size": page_size,
        "sort_by": sort_by,
        "total": 100,
        "products": [f"产品 {i}" for i in range((page-1)*page_size, page*page_size)]
    }


# ============ 4. 使用枚举限制参数值 ============

class SortOrder(str, Enum):
    """排序顺序枚举"""
    asc = "asc"
    desc = "desc"


class Category(str, Enum):
    """类别枚举"""
    electronics = "electronics"
    books = "books"
    clothing = "clothing"
    food = "food"


@app.get("/catalog/{category}")
def get_catalog(
    category: Category,  # 使用枚举限制可选值
    sort: SortOrder = SortOrder.asc  # 默认升序
):
    """
    获取分类目录
    
    category 只能是预定义的类别之一
    sort 只能是 asc 或 desc
    """
    return {
        "category": category.value,
        "sort_order": sort.value,
        "message": f"获取 {category.value} 类别，{sort.value} 排序"
    }


# ============ 5. 混合使用路径参数和查询参数 ============

@app.get("/users/{user_id}/posts")
def get_user_posts(
    user_id: int = Path(..., ge=1),
    published: bool = Query(True, description="是否只显示已发布的文章"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    获取用户的文章列表
    
    结合路径参数和查询参数
    """
    return {
        "user_id": user_id,
        "published_only": published,
        "limit": limit,
        "offset": offset,
        "posts": [
            {
                "id": i,
                "title": f"文章 {i}",
                "published": published
            }
            for i in range(offset, offset + limit)
        ]
    }


# ============ 6. 布尔查询参数 ============

@app.get("/tasks")
def get_tasks(
    completed: bool = Query(False, description="是否只显示已完成的任务"),
    urgent: bool = Query(False, description="是否只显示紧急任务")
):
    """
    获取任务列表
    
    布尔参数示例:
    - /tasks
    - /tasks?completed=true
    - /tasks?completed=true&urgent=true
    """
    filters = []
    if completed:
        filters.append("已完成")
    if urgent:
        filters.append("紧急")
    
    return {
        "filters": filters if filters else ["全部"],
        "tasks": ["任务 1", "任务 2", "任务 3"]
    }


# ============ 7. 列表查询参数 ============

@app.get("/multi-filter")
def multi_filter(
    tags: list[str] = Query(
        [],
        title="标签列表",
        description="要过滤的标签"
    )
):
    """
    使用列表查询参数
    
    示例:
    - /multi-filter?tags=python&tags=fastapi&tags=web
    """
    return {
        "tags": tags,
        "count": len(tags),
        "message": f"过滤标签: {', '.join(tags)}" if tags else "无标签过滤"
    }


"""
学习要点:

1. 路径参数 (Path Parameters)
   - 在 URL 路径中使用 {参数名} 定义
   - 自动进行类型转换和验证
   - 使用 Path() 添加额外的验证规则
   - 支持多个路径参数

2. 查询参数 (Query Parameters)
   - 在 URL 中使用 ?key=value 传递
   - 可以设置默认值使其成为可选参数
   - 使用 Optional[类型] 表示完全可选
   - 使用 Query() 添加验证和元数据

3. 参数验证
   - ge: 大于等于 (greater than or equal)
   - le: 小于等于 (less than or equal)
   - gt: 大于 (greater than)
   - lt: 小于 (less than)
   - min_length: 最小长度
   - max_length: 最大长度
   - regex: 正则表达式验证

4. 枚举类型
   - 使用 Enum 限制参数的可选值
   - 提供更好的类型安全和文档
   - 自动在 API 文档中显示可选值

5. 参数组合
   - 可以同时使用路径参数和查询参数
   - 参数顺序不影响功能
   - 建议: 路径参数用于资源标识，查询参数用于过滤和选项

6. 布尔和列表参数
   - 布尔参数自动转换 true/false
   - 列表参数通过重复参数名传递多个值

实践练习:
1. 创建一个 /books/{book_id} 端点，添加价格范围验证
2. 实现一个搜索端点，支持关键词、分类、价格范围过滤
3. 创建一个用户管理端点，支持按角色、状态过滤
4. 使用枚举定义文章状态（草稿、已发布、已归档）
5. 实现一个支持多标签过滤的端点
"""
