"""
专利交底书处理器

负责解析、验证专利交底书，并将其转换为专利申请文件
"""

import sys
import os
from typing import List, Optional, Tuple
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from schemas.disclosure_schemas import (
    PatentDisclosure,
    DisclosureStatus,
    TechnicalProblem,
    TechnicalSolution,
    DisclosureValidationResult,
    DisclosureToPatentRequest,
)
from schemas.patent_schemas import (
    PatentDraftRequest,
    PatentApplication,
    PatentType,
    ApplicantInfo,
    InventorInfo,
    PatentClaim,
    ApplicationStatus,
)
from tools.patent_writer import PatentWriter


class DisclosureProcessor:
    """专利交底书处理器
    
    负责：
    1. 验证交底书完整性
    2. 提取关键技术信息
    3. 将交底书转换为专利申请文件
    """
    
    def __init__(self):
        self.patent_writer = PatentWriter()
        # 必填字段
        self.required_fields = [
            "title",
            "inventors",
            "applicant_name",
            "technical_field",
            "background_description",
            "technical_problems",
            "technical_solution",
            "beneficial_effects",
        ]
    
    def validate_disclosure(self, disclosure: PatentDisclosure) -> DisclosureValidationResult:
        """
        验证交底书的完整性和规范性
        
        Args:
            disclosure: 专利交底书
            
        Returns:
            验证结果
        """
        errors = []
        warnings = []
        suggestions = []
        score = 100.0
        
        # 检查必填字段
        if not disclosure.title or len(disclosure.title.strip()) < 5:
            errors.append("发明名称过短或为空，至少需要5个字符")
            score -= 15
        
        if not disclosure.inventors or len(disclosure.inventors) == 0:
            errors.append("必须至少有一位发明人")
            score -= 10
        
        if not disclosure.applicant_name:
            errors.append("申请人名称不能为空")
            score -= 10
        
        if not disclosure.technical_field or len(disclosure.technical_field.strip()) < 10:
            errors.append("技术领域描述过短，至少需要10个字符")
            score -= 10
        
        if not disclosure.background_description or len(disclosure.background_description.strip()) < 50:
            errors.append("背景技术描述过短，至少需要50个字符")
            score -= 10
        
        if not disclosure.technical_problems or len(disclosure.technical_problems) == 0:
            errors.append("必须描述至少一个要解决的技术问题")
            score -= 15
        
        if not disclosure.technical_solution:
            errors.append("技术方案不能为空")
            score -= 15
        elif not disclosure.technical_solution.overview:
            errors.append("技术方案概述不能为空")
            score -= 10
        
        if not disclosure.beneficial_effects or len(disclosure.beneficial_effects) == 0:
            errors.append("必须描述至少一项有益效果")
            score -= 10
        
        # 检查可选但推荐的字段
        if not disclosure.embodiments or len(disclosure.embodiments) == 0:
            warnings.append("建议提供至少一个具体实施例")
            score -= 5
        
        if not disclosure.figure_descriptions or len(disclosure.figure_descriptions) == 0:
            warnings.append("建议提供附图说明")
            score -= 5
        
        if disclosure.patent_type == "utility_model" and len(disclosure.figure_descriptions) == 0:
            errors.append("实用新型专利必须有附图说明")
            score -= 10
        
        # 提供建议
        if len(disclosure.technical_solution.innovation_points) == 0:
            suggestions.append("建议明确列出技术方案的创新点，有助于撰写权利要求书")
        
        if len(disclosure.prior_art_references) == 0:
            suggestions.append("建议提供现有技术参考文献，有助于撰写背景技术部分")
        
        if not disclosure.contact_email:
            suggestions.append("建议提供联系邮箱，便于后续沟通")
        
        # 确保分数在有效范围内
        score = max(0.0, min(100.0, score))
        
        return DisclosureValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            suggestions=suggestions,
            completeness_score=score,
        )
    
    def disclosure_to_patent_request(self, disclosure: PatentDisclosure) -> PatentDraftRequest:
        """
        将交底书转换为专利撰写请求
        
        Args:
            disclosure: 专利交底书
            
        Returns:
            专利撰写请求
        """
        # 合并技术问题描述
        problems_text = ""
        for i, problem in enumerate(disclosure.technical_problems, 1):
            problems_text += f"{i}. {problem.description}"
            if problem.existing_solutions:
                problems_text += f"\n   现有方案：{problem.existing_solutions}"
            if problem.limitations:
                problems_text += f"\n   局限性：{problem.limitations}"
            problems_text += "\n\n"
        
        # 合并技术方案
        solution_text = disclosure.technical_solution.overview + "\n\n"
        if disclosure.technical_solution.key_steps:
            solution_text += "关键步骤：\n"
            for i, step in enumerate(disclosure.technical_solution.key_steps, 1):
                solution_text += f"{i}. {step}\n"
            solution_text += "\n"
        if disclosure.technical_solution.innovation_points:
            solution_text += "创新点：\n"
            for i, point in enumerate(disclosure.technical_solution.innovation_points, 1):
                solution_text += f"{i}. {point}\n"
            solution_text += "\n"
        if disclosure.technical_solution.implementation_details:
            solution_text += f"实现细节：\n{disclosure.technical_solution.implementation_details}\n"
        
        # 合并有益效果
        effects_text = "\n".join([f"- {effect}" for effect in disclosure.beneficial_effects])
        
        # 构建发明描述
        invention_description = f"""
{disclosure.title}

技术方案：
{disclosure.technical_solution.overview}

具体实施方式：
{chr(10).join(disclosure.embodiments) if disclosure.embodiments else '待补充'}
        """.strip()
        
        # 确定专利类型
        patent_type = PatentType.INVENTION
        if disclosure.patent_type == "utility_model":
            patent_type = PatentType.UTILITY_MODEL
        elif disclosure.patent_type == "design":
            patent_type = PatentType.DESIGN
        
        return PatentDraftRequest(
            invention_description=invention_description,
            technical_field=disclosure.technical_field,
            background_info=disclosure.background_description,
            specific_problems=problems_text,
            solution=solution_text,
            beneficial_effects=effects_text,
            patent_type=patent_type,
            language="zh",
        )
    
    def process_disclosure(
        self, 
        disclosure: PatentDisclosure,
        validate: bool = True,
    ) -> Tuple[Optional[PatentApplication], Optional[DisclosureValidationResult]]:
        """
        处理专利交底书，生成专利申请文件
        
        Args:
            disclosure: 专利交底书
            validate: 是否进行验证
            
        Returns:
            (专利申请文件, 验证结果)
        """
        validation_result = None
        
        # 验证交底书
        if validate:
            validation_result = self.validate_disclosure(disclosure)
            if not validation_result.is_valid:
                return None, validation_result
        
        # 转换为专利撰写请求
        draft_request = self.disclosure_to_patent_request(disclosure)
        
        # 创建申请人信息
        applicant_info = ApplicantInfo(
            name=disclosure.applicant_name,
            address=disclosure.applicant_address or "待填写",
            country="中国",
            email=disclosure.contact_email,
            phone=disclosure.contact_phone,
        )
        
        # 创建发明人信息
        inventor_info = [
            InventorInfo(name=name, country="中国")
            for name in disclosure.inventors
        ]
        
        # 生成专利申请文件
        application = self.patent_writer.generate_patent_application(
            request=draft_request,
            applicant_info=applicant_info,
            inventor_info=inventor_info,
        )
        
        # 更新标题（使用交底书的标题）
        application.title = disclosure.title
        
        return application, validation_result
    
    def generate_enhanced_patent(
        self,
        disclosure: PatentDisclosure,
    ) -> str:
        """
        基于交底书生成增强版专利文件
        
        这个方法会生成更详细、更符合实际需求的专利文件
        
        Args:
            disclosure: 专利交底书
            
        Returns:
            格式化的专利申请文件文本
        """
        # 先处理生成基础申请
        application, validation = self.process_disclosure(disclosure, validate=True)
        
        if application is None:
            # 返回验证错误信息
            error_msg = "交底书验证失败：\n"
            if validation:
                for error in validation.errors:
                    error_msg += f"❌ {error}\n"
                for warning in validation.warnings:
                    error_msg += f"⚠️ {warning}\n"
            return error_msg
        
        # 生成格式化的专利文件
        formatted = self._format_enhanced_application(application, disclosure)
        
        return formatted
    
    def _format_enhanced_application(
        self, 
        application: PatentApplication,
        disclosure: PatentDisclosure,
    ) -> str:
        """格式化增强版专利申请文件"""
        
        formatted = "=" * 60 + "\n"
        formatted += "           专 利 申 请 文 件\n"
        formatted += "=" * 60 + "\n\n"
        
        # 专利类型标识
        type_names = {
            PatentType.INVENTION: "发明专利",
            PatentType.UTILITY_MODEL: "实用新型专利",
            PatentType.DESIGN: "外观设计专利",
        }
        formatted += f"【专利类型】{type_names.get(application.patent_type, '发明专利')}\n\n"
        
        # 发明名称
        formatted += "-" * 50 + "\n"
        formatted += f"【发明名称】\n{application.title}\n\n"
        
        # 申请人和发明人信息
        formatted += "-" * 50 + "\n"
        formatted += f"【申请人】{application.applicant.name}\n"
        formatted += f"【地  址】{application.applicant.address}\n"
        formatted += f"【发明人】{', '.join([inv.name for inv in application.inventors])}\n\n"
        
        # 技术领域
        formatted += "-" * 50 + "\n"
        formatted += "【技术领域】\n"
        formatted += f"{application.technical_field}\n\n"
        
        # 背景技术
        formatted += "-" * 50 + "\n"
        formatted += "【背景技术】\n"
        formatted += f"{disclosure.background_description}\n\n"
        
        # 发明内容
        formatted += "-" * 50 + "\n"
        formatted += "【发明内容】\n\n"
        
        # 要解决的技术问题
        formatted += "一、要解决的技术问题\n"
        for i, problem in enumerate(disclosure.technical_problems, 1):
            formatted += f"{i}. {problem.description}\n"
            if problem.limitations:
                formatted += f"   现有技术局限性：{problem.limitations}\n"
        formatted += "\n"
        
        # 技术方案
        formatted += "二、技术方案\n"
        formatted += f"{disclosure.technical_solution.overview}\n\n"
        
        if disclosure.technical_solution.key_steps:
            formatted += "具体包括以下步骤：\n"
            for i, step in enumerate(disclosure.technical_solution.key_steps, 1):
                formatted += f"步骤{i}：{step}\n"
            formatted += "\n"
        
        if disclosure.technical_solution.innovation_points:
            formatted += "本发明的创新点在于：\n"
            for i, point in enumerate(disclosure.technical_solution.innovation_points, 1):
                formatted += f"（{i}）{point}\n"
            formatted += "\n"
        
        # 有益效果
        formatted += "三、有益效果\n"
        formatted += "与现有技术相比，本发明具有以下有益效果：\n"
        for i, effect in enumerate(disclosure.beneficial_effects, 1):
            formatted += f"{i}. {effect}\n"
        formatted += "\n"
        
        # 附图说明
        formatted += "-" * 50 + "\n"
        formatted += "【附图说明】\n"
        if disclosure.figure_descriptions:
            for desc in disclosure.figure_descriptions:
                formatted += f"{desc}\n"
        else:
            formatted += f"{application.brief_description}\n"
        formatted += "\n"
        
        # 具体实施方式
        formatted += "-" * 50 + "\n"
        formatted += "【具体实施方式】\n"
        formatted += "下面结合附图和实施例对本发明作进一步说明。\n\n"
        
        if disclosure.embodiments:
            for i, embodiment in enumerate(disclosure.embodiments, 1):
                formatted += f"实施例{i}：\n{embodiment}\n\n"
        else:
            formatted += f"{application.invention_content}\n\n"
        
        if disclosure.technical_solution.implementation_details:
            formatted += f"实现细节：\n{disclosure.technical_solution.implementation_details}\n\n"
        
        # 权利要求书
        formatted += "-" * 50 + "\n"
        formatted += "【权利要求书】\n\n"
        
        # 生成更详细的权利要求
        claims = self._generate_claims_from_disclosure(disclosure)
        for claim in claims:
            formatted += f"{claim}\n\n"
        
        # 摘要
        formatted += "-" * 50 + "\n"
        formatted += "【摘  要】\n"
        formatted += f"本发明公开了{application.title}，属于{application.technical_field}。"
        formatted += f"本发明要解决的技术问题是{disclosure.technical_problems[0].description if disclosure.technical_problems else '改进现有技术的不足'}。"
        formatted += f"本发明的技术方案是{disclosure.technical_solution.overview[:100]}..."
        formatted += f"本发明的有益效果是{disclosure.beneficial_effects[0] if disclosure.beneficial_effects else '提高了效率'}等。\n\n"
        
        formatted += "=" * 60 + "\n"
        formatted += "                    文件结束\n"
        formatted += "=" * 60 + "\n"
        
        return formatted
    
    def _generate_claims_from_disclosure(self, disclosure: PatentDisclosure) -> List[str]:
        """基于交底书生成权利要求"""
        claims = []
        
        # 独立权利要求1
        claim1 = f"1. {disclosure.title}，其特征在于：\n"
        if disclosure.technical_solution.key_steps:
            for i, step in enumerate(disclosure.technical_solution.key_steps):
                claim1 += f"    （{i+1}）{step}；\n"
        else:
            claim1 += f"    包括{disclosure.technical_solution.overview[:50]}。"
        claims.append(claim1)
        
        # 从属权利要求（基于创新点生成）
        if disclosure.technical_solution.innovation_points:
            for i, point in enumerate(disclosure.technical_solution.innovation_points[:4], 2):
                claim = f"{i}. 根据权利要求1所述的{disclosure.title}，其特征在于：{point}。"
                claims.append(claim)
        else:
            # 生成默认的从属权利要求
            claims.append(f"2. 根据权利要求1所述的{disclosure.title}，其特征在于：所述技术方案还包括数据预处理步骤。")
            claims.append(f"3. 根据权利要求1所述的{disclosure.title}，其特征在于：所述技术方案还包括结果验证步骤。")
            claims.append(f"4. 根据权利要求1所述的{disclosure.title}，其特征在于：所述技术方案可以应用于多种场景。")
        
        # 独立权利要求（系统/装置）
        claims.append(f"5. 一种实现权利要求1-4任一项所述方法的系统，其特征在于：包括处理模块、控制模块和输出模块。")
        
        return claims
