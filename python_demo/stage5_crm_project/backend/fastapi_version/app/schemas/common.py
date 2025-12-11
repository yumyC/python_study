"""
通用 Pydantic 模式

定义跨模块使用的通用模式
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Generic, TypeVar

# 泛型类型变量
T = TypeVar('T')


class PaginationParams(BaseModel):
    """分页参数模式"""
    skip: int = Field(0, ge=0, description="跳过的记录数")
    limit: int = Field(10, ge=1, le=100, description="返回的记录数")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模式"""
    items: List[T] = Field(description="数据项列表")
    total: int = Field(description="总记录数")
    skip: int = Field(description="跳过的记录数")
    limit: int = Field(description="每页记录数")
    has_next: bool = Field(description="是否有下一页")
    has_prev: bool = Field(description="是否有上一页")
    
    class Config:
        from_attributes = True


class ErrorResponse(BaseModel):
    """错误响应模式"""
    error: dict = Field(description="错误信息")
    
    class Config:
        schema_extra = {
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "请求参数验证失败",
                    "details": {},
                    "request_id": "uuid"
                }
            }
        }


class SuccessResponse(BaseModel):
    """成功响应模式"""
    message: str = Field(description="成功消息")
    data: Optional[dict] = Field(None, description="附加数据")
    
    class Config:
        schema_extra = {
            "example": {
                "message": "操作成功",
                "data": {}
            }
        }


class IDResponse(BaseModel):
    """ID 响应模式"""
    id: str = Field(description="资源ID")
    message: str = Field(description="操作消息")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "uuid",
                "message": "创建成功"
            }
        }


class SearchParams(BaseModel):
    """搜索参数模式"""
    search: Optional[str] = Field(None, description="搜索关键词")
    sort_by: Optional[str] = Field(None, description="排序字段")
    sort_order: Optional[str] = Field("asc", regex="^(asc|desc)$", description="排序方向")
    
    class Config:
        schema_extra = {
            "example": {
                "search": "关键词",
                "sort_by": "created_at",
                "sort_order": "desc"
            }
        }


class DateRangeParams(BaseModel):
    """日期范围参数模式"""
    start_date: Optional[str] = Field(None, regex=r"^\d{4}-\d{2}-\d{2}$", description="开始日期 (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, regex=r"^\d{4}-\d{2}-\d{2}$", description="结束日期 (YYYY-MM-DD)")
    
    class Config:
        schema_extra = {
            "example": {
                "start_date": "2023-01-01",
                "end_date": "2023-12-31"
            }
        }


class StatusResponse(BaseModel):
    """状态响应模式"""
    status: str = Field(description="状态")
    timestamp: str = Field(description="时间戳")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "success",
                "timestamp": "2023-12-11T10:00:00Z"
            }
        }