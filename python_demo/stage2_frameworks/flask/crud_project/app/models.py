"""
数据模型定义

定义应用的数据库模型，包括产品（Product）模型。
"""

from app import db
from datetime import datetime


class Product(db.Model):
    """
    产品模型
    
    用于演示 CRUD 操作的示例模型。
    包含产品的基本信息：名称、描述、价格、库存等。
    """
    __tablename__ = 'products'
    
    # 主键
    id = db.Column(db.Integer, primary_key=True)
    
    # 产品信息
    name = db.Column(db.String(100), nullable=False, index=True)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50))
    
    # 状态
    is_active = db.Column(db.Boolean, default=True)
    
    # 时间戳
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """
        将模型转换为字典
        
        用于 JSON 序列化，方便 API 返回数据。
        """
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': self.price,
            'stock': self.stock,
            'category': self.category,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def __repr__(self):
        """字符串表示"""
        return f'<Product {self.name}>'
