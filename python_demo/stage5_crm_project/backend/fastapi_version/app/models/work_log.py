"""
工作日志模型

定义员工工作日志的数据模型
"""

from sqlalchemy import Column, String, Text, Date, Integer, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import enum

from .base import BaseModel


class CompletionStatus(enum.Enum):
    """工作完成状态枚举"""
    COMPLETED = "completed"      # 已完成
    IN_PROGRESS = "in_progress"  # 进行中
    PENDING = "pending"          # 待开始


class WorkLog(BaseModel):
    """
    工作日志模型
    
    记录员工的日常工作情况：
    - 工作内容和完成状态
    - 遇到的问题
    - 明日计划
    - 自评和上级评分
    """
    __tablename__ = "work_logs"
    
    # 员工ID，外键关联到 employees 表
    employee_id = Column(
        UUID(as_uuid=True),
        ForeignKey("employees.id", ondelete="CASCADE"),
        nullable=False,
        comment="员工ID"
    )
    
    # 日志日期
    log_date = Column(
        Date,
        nullable=False,
        index=True,
        comment="日志日期"
    )
    
    # 工作内容
    work_content = Column(
        Text,
        nullable=False,
        comment="工作内容"
    )
    
    # 完成状态
    completion_status = Column(
        Enum(CompletionStatus),
        default=CompletionStatus.IN_PROGRESS,
        nullable=False,
        comment="完成状态"
    )
    
    # 遇到的问题
    problems_encountered = Column(
        Text,
        nullable=True,
        comment="遇到的问题"
    )
    
    # 明日计划
    tomorrow_plan = Column(
        Text,
        nullable=True,
        comment="明日计划"
    )
    
    # 自我评分（1-5分）
    self_rating = Column(
        Integer,
        nullable=True,
        comment="自我评分"
    )
    
    # 上级评分（1-5分）
    supervisor_rating = Column(
        Integer,
        nullable=True,
        comment="上级评分"
    )
    
    # 上级评价
    supervisor_comment = Column(
        Text,
        nullable=True,
        comment="上级评价"
    )
    
    # 关系定义
    # 关联到员工表
    employee = relationship(
        "Employee",
        back_populates="work_logs",
        lazy="select"
    )
    
    def __repr__(self):
        return f"<WorkLog(employee_id={self.employee_id}, log_date={self.log_date}, status={self.completion_status.value})>"
    
    def get_status_display(self):
        """
        获取完成状态的中文显示
        
        Returns:
            str: 状态的中文名称
        """
        status_display = {
            CompletionStatus.COMPLETED: "已完成",
            CompletionStatus.IN_PROGRESS: "进行中",
            CompletionStatus.PENDING: "待开始"
        }
        
        return status_display.get(self.completion_status, "未知")
    
    def is_rated_by_supervisor(self):
        """
        检查是否已被上级评分
        
        Returns:
            bool: 如果已评分返回 True
        """
        return self.supervisor_rating is not None
    
    def get_rating_difference(self):
        """
        获取自评和上级评分的差异
        
        Returns:
            int or None: 评分差异，如果任一评分为空则返回 None
        """
        if self.self_rating is not None and self.supervisor_rating is not None:
            return self.supervisor_rating - self.self_rating
        return None
    
    def validate_rating(self, rating):
        """
        验证评分是否在有效范围内
        
        Args:
            rating: 评分值
            
        Returns:
            bool: 如果评分有效返回 True
        """
        return rating is None or (1 <= rating <= 5)
    
    def set_self_rating(self, rating):
        """
        设置自我评分
        
        Args:
            rating: 评分值（1-5）
            
        Raises:
            ValueError: 如果评分不在有效范围内
        """
        if not self.validate_rating(rating):
            raise ValueError("评分必须在1-5之间")
        self.self_rating = rating
    
    def set_supervisor_rating(self, rating, comment=None):
        """
        设置上级评分和评价
        
        Args:
            rating: 评分值（1-5）
            comment: 评价内容
            
        Raises:
            ValueError: 如果评分不在有效范围内
        """
        if not self.validate_rating(rating):
            raise ValueError("评分必须在1-5之间")
        
        self.supervisor_rating = rating
        if comment:
            self.supervisor_comment = comment
    
    def to_export_dict(self):
        """
        转换为导出格式的字典
        
        Returns:
            dict: 适合导出的数据字典
        """
        return {
            "员工姓名": self.employee.full_name if self.employee else "",
            "日期": self.log_date.strftime("%Y-%m-%d") if self.log_date else "",
            "工作内容": self.work_content or "",
            "完成状态": self.get_status_display(),
            "遇到的问题": self.problems_encountered or "",
            "明日计划": self.tomorrow_plan or "",
            "自我评分": self.self_rating or "",
            "上级评分": self.supervisor_rating or "",
            "上级评价": self.supervisor_comment or "",
            "创建时间": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else ""
        }
    
    @classmethod
    def get_rating_statistics(cls, session, employee_id=None, start_date=None, end_date=None):
        """
        获取评分统计信息
        
        Args:
            session: 数据库会话
            employee_id: 员工ID（可选）
            start_date: 开始日期（可选）
            end_date: 结束日期（可选）
            
        Returns:
            dict: 统计信息
        """
        query = session.query(cls)
        
        if employee_id:
            query = query.filter(cls.employee_id == employee_id)
        if start_date:
            query = query.filter(cls.log_date >= start_date)
        if end_date:
            query = query.filter(cls.log_date <= end_date)
        
        logs = query.all()
        
        if not logs:
            return {
                "total_logs": 0,
                "avg_self_rating": 0,
                "avg_supervisor_rating": 0,
                "completion_rate": 0
            }
        
        # 计算平均评分
        self_ratings = [log.self_rating for log in logs if log.self_rating is not None]
        supervisor_ratings = [log.supervisor_rating for log in logs if log.supervisor_rating is not None]
        
        # 计算完成率
        completed_logs = [log for log in logs if log.completion_status == CompletionStatus.COMPLETED]
        
        return {
            "total_logs": len(logs),
            "avg_self_rating": sum(self_ratings) / len(self_ratings) if self_ratings else 0,
            "avg_supervisor_rating": sum(supervisor_ratings) / len(supervisor_ratings) if supervisor_ratings else 0,
            "completion_rate": len(completed_logs) / len(logs) * 100 if logs else 0,
            "rated_logs": len(supervisor_ratings),
            "rating_coverage": len(supervisor_ratings) / len(logs) * 100 if logs else 0
        }