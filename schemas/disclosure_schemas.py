"""
专利交底书数据模型

定义专利交底书的结构和验证规则
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class DisclosureStatus(str, Enum):
    """交底书状态"""
    DRAFT = "draft"  # 草稿
    SUBMITTED = "submitted"  # 已提交
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    REJECTED = "rejected"  # 已退回


class TechnicalProblem(BaseModel):
    """技术问题描述"""
    description: str = Field(description="问题描述")
    existing_solutions: Optional[str] = Field(default=None, description="现有解决方案")
    limitations: Optional[str] = Field(default=None, description="现有方案的局限性")


class TechnicalSolution(BaseModel):
    """技术方案描述"""
    overview: str = Field(description="方案概述")
    key_steps: List[str] = Field(default_factory=list, description="关键步骤")
    innovation_points: List[str] = Field(default_factory=list, description="创新点")
    implementation_details: Optional[str] = Field(default=None, description="实现细节")


class AttachmentInfo(BaseModel):
    """附件信息"""
    file_name: str = Field(description="文件名")
    file_type: str = Field(description="文件类型")
    file_path: Optional[str] = Field(default=None, description="文件路径")
    description: Optional[str] = Field(default=None, description="附件描述")


class PatentDisclosure(BaseModel):
    """专利交底书模型
    
    这是发明人提交的技术交底文档，用于撰写正式专利申请文件
    """
    # 基本信息
    id: Optional[str] = Field(default=None, description="交底书ID")
    title: str = Field(description="发明名称")
    patent_type: str = Field(default="invention", description="专利类型: invention/utility_model/design")
    
    # 发明人和申请人信息
    inventors: List[str] = Field(description="发明人列表")
    applicant_name: str = Field(description="申请人名称")
    applicant_address: Optional[str] = Field(default=None, description="申请人地址")
    contact_person: Optional[str] = Field(default=None, description="联系人")
    contact_phone: Optional[str] = Field(default=None, description="联系电话")
    contact_email: Optional[str] = Field(default=None, description="联系邮箱")
    
    # 技术内容
    technical_field: str = Field(description="技术领域")
    background_description: str = Field(description="背景技术描述")
    technical_problems: List[TechnicalProblem] = Field(description="要解决的技术问题")
    technical_solution: TechnicalSolution = Field(description="技术方案")
    beneficial_effects: List[str] = Field(description="有益效果列表")
    
    # 实施例
    embodiments: List[str] = Field(default_factory=list, description="具体实施例")
    
    # 附图相关
    figure_descriptions: List[str] = Field(default_factory=list, description="附图说明")
    attachments: List[AttachmentInfo] = Field(default_factory=list, description="附件列表")
    
    # 其他信息
    prior_art_references: List[str] = Field(default_factory=list, description="现有技术参考")
    keywords: List[str] = Field(default_factory=list, description="关键词")
    additional_notes: Optional[str] = Field(default=None, description="其他备注")
    
    # 元数据
    status: DisclosureStatus = Field(default=DisclosureStatus.DRAFT, description="状态")
    submitted_at: Optional[datetime] = Field(default=None, description="提交时间")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class DisclosureToPatentRequest(BaseModel):
    """交底书转专利申请请求"""
    disclosure: PatentDisclosure = Field(description="专利交底书")
    output_format: str = Field(default="text", description="输出格式: text/xml/json")
    include_review: bool = Field(default=True, description="是否包含预审")
    language: str = Field(default="zh", description="语言: zh/en")


class DisclosureValidationResult(BaseModel):
    """交底书验证结果"""
    is_valid: bool = Field(description="是否有效")
    errors: List[str] = Field(default_factory=list, description="错误列表")
    warnings: List[str] = Field(default_factory=list, description="警告列表")
    suggestions: List[str] = Field(default_factory=list, description="建议列表")
    completeness_score: float = Field(default=0.0, description="完整性评分 0-100")
