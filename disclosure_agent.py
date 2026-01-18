"""
专利交底书处理智能体

负责处理专利交底书并生成专利申请文件

工作流程：
1. 接收专利交底书
2. 验证交底书完整性
3. 提取关键技术信息
4. 调用AI生成高质量专利文件
5. 进行预审和优化
"""

import asyncio
import sys
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import Agent, Runner, function_tool, set_tracing_disabled

# 导入工具和模型
from tools import PatentSearchTool, PatentWriter, PatentPreReviewer, DisclosureProcessor
from schemas.patent_schemas import PatentType, PatentApplication
from schemas.disclosure_schemas import (
    PatentDisclosure,
    TechnicalProblem,
    TechnicalSolution,
    DisclosureStatus,
    DisclosureValidationResult,
)
from config.review_rules import RuleManager

# 禁用跟踪
set_tracing_disabled(disabled=True)


def create_gemini_model():
    """创建 Gemini 模型"""
    try:
        from agents.extensions.models.litellm_model import LitellmModel
        
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("⚠ 未设置 GOOGLE_API_KEY")
            return None
        
        model = LitellmModel(
            model="gemini/gemini-2.0-flash-exp",
            api_key=api_key
        )
        print("✓ 交底书处理 Agent Gemini 模型初始化成功")
        return model
    except Exception as e:
        print(f"✗ 模型初始化失败: {e}")
        return None


# 创建工具实例
disclosure_processor = DisclosureProcessor()
patent_writer = PatentWriter()
patent_search_tool = PatentSearchTool()
rule_manager = RuleManager()
pre_reviewer = PatentPreReviewer(rule_manager)
gemini_model = create_gemini_model()


@function_tool
def validate_disclosure(
    title: str,
    inventors: str,
    applicant_name: str,
    technical_field: str,
    background_description: str,
    technical_problems: str,
    technical_solution: str,
    beneficial_effects: str,
    patent_type: str = "invention",
) -> str:
    """
    验证专利交底书的完整性
    
    Args:
        title: 发明名称
        inventors: 发明人（多个用逗号分隔）
        applicant_name: 申请人名称
        technical_field: 技术领域
        background_description: 背景技术描述
        technical_problems: 要解决的技术问题
        technical_solution: 技术方案描述
        beneficial_effects: 有益效果（多个用分号分隔）
        patent_type: 专利类型
        
    Returns:
        验证结果报告
    """
    try:
        # 构建交底书对象
        disclosure = PatentDisclosure(
            title=title,
            inventors=[inv.strip() for inv in inventors.split(",")],
            applicant_name=applicant_name,
            technical_field=technical_field,
            background_description=background_description,
            technical_problems=[
                TechnicalProblem(description=technical_problems)
            ],
            technical_solution=TechnicalSolution(
                overview=technical_solution,
            ),
            beneficial_effects=[eff.strip() for eff in beneficial_effects.split(";")],
            patent_type=patent_type,
        )
        
        # 验证
        result = disclosure_processor.validate_disclosure(disclosure)
        
        # 格式化报告
        report = "=" * 50 + "\n"
        report += "       专利交底书验证报告\n"
        report += "=" * 50 + "\n\n"
        
        if result.is_valid:
            report += "✅ 验证通过！交底书内容完整\n\n"
        else:
            report += "❌ 验证未通过，请修正以下问题：\n\n"
        
        report += f"📊 完整性评分：{result.completeness_score:.1f}/100\n\n"
        
        if result.errors:
            report += "❌ 错误（必须修正）：\n"
            for error in result.errors:
                report += f"   • {error}\n"
            report += "\n"
        
        if result.warnings:
            report += "⚠️ 警告（建议修正）：\n"
            for warning in result.warnings:
                report += f"   • {warning}\n"
            report += "\n"
        
        if result.suggestions:
            report += "💡 建议：\n"
            for suggestion in result.suggestions:
                report += f"   • {suggestion}\n"
            report += "\n"
        
        return report
        
    except Exception as e:
        return f"验证交底书时发生错误：{str(e)}"


@function_tool
def process_disclosure_to_patent(
    title: str,
    inventors: str,
    applicant_name: str,
    technical_field: str,
    background_description: str,
    technical_problems: str,
    technical_solution: str,
    key_steps: Optional[str] = None,
    innovation_points: Optional[str] = None,
    beneficial_effects: str = "",
    embodiments: Optional[str] = None,
    figure_descriptions: Optional[str] = None,
    patent_type: str = "invention",
    applicant_address: Optional[str] = None,
    contact_email: Optional[str] = None,
) -> str:
    """
    将专利交底书转换为完整的专利申请文件
    
    Args:
        title: 发明名称
        inventors: 发明人（多个用逗号分隔）
        applicant_name: 申请人名称
        technical_field: 技术领域
        background_description: 背景技术描述
        technical_problems: 要解决的技术问题
        technical_solution: 技术方案概述
        key_steps: 关键步骤（多个用分号分隔）
        innovation_points: 创新点（多个用分号分隔）
        beneficial_effects: 有益效果（多个用分号分隔）
        embodiments: 具体实施例（多个用分号分隔）
        figure_descriptions: 附图说明（多个用分号分隔）
        patent_type: 专利类型
        applicant_address: 申请人地址
        contact_email: 联系邮箱
        
    Returns:
        完整的专利申请文件
    """
    try:
        # 解析列表字段
        inventors_list = [inv.strip() for inv in inventors.split(",") if inv.strip()]
        effects_list = [eff.strip() for eff in beneficial_effects.split(";") if eff.strip()]
        steps_list = [step.strip() for step in key_steps.split(";")] if key_steps else []
        points_list = [point.strip() for point in innovation_points.split(";")] if innovation_points else []
        embodiments_list = [emb.strip() for emb in embodiments.split(";")] if embodiments else []
        figures_list = [fig.strip() for fig in figure_descriptions.split(";")] if figure_descriptions else []
        
        # 构建交底书对象
        disclosure = PatentDisclosure(
            title=title,
            inventors=inventors_list,
            applicant_name=applicant_name,
            applicant_address=applicant_address,
            contact_email=contact_email,
            technical_field=technical_field,
            background_description=background_description,
            technical_problems=[
                TechnicalProblem(description=technical_problems)
            ],
            technical_solution=TechnicalSolution(
                overview=technical_solution,
                key_steps=steps_list,
                innovation_points=points_list,
            ),
            beneficial_effects=effects_list,
            embodiments=embodiments_list,
            figure_descriptions=figures_list,
            patent_type=patent_type,
            status=DisclosureStatus.SUBMITTED,
            submitted_at=datetime.now(),
        )
        
        # 生成专利文件
        patent_text = disclosure_processor.generate_enhanced_patent(disclosure)
        
        return patent_text
        
    except Exception as e:
        return f"处理交底书时发生错误：{str(e)}"


@function_tool
def get_disclosure_template() -> str:
    """
    获取专利交底书模板
    
    Returns:
        交底书填写模板和说明
    """
    template = """
📋 专利交底书模板
=====================================

【基本信息】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
发明名称：[简洁明了，体现技术特点]
专利类型：[发明专利/实用新型/外观设计]
申请人：[公司名称或个人姓名]
申请人地址：[详细地址]
发明人：[多个用逗号分隔]
联系邮箱：[用于后续沟通]

【技术内容】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

一、技术领域
[本发明涉及的技术领域，例如：人工智能、机械制造、电子通信等]

二、背景技术
[描述现有技术的状况、存在的问题和不足]
1. 现有技术方案...
2. 存在的问题...
3. 技术局限性...

三、要解决的技术问题
[明确指出本发明要解决的具体技术问题]

四、技术方案
[详细描述本发明的技术方案]

4.1 方案概述：
[整体技术思路]

4.2 关键步骤：
步骤1：...
步骤2：...
步骤3：...

4.3 创新点：
创新点1：...
创新点2：...
创新点3：...

五、有益效果
[与现有技术相比，本发明的有益效果]
1. ...
2. ...
3. ...

六、具体实施例
[提供1-3个具体实施例]

实施例1：
...

实施例2：
...

七、附图说明
[如有附图，请说明每张图的内容]
图1：...
图2：...
图3：...

【填写说明】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ 发明名称：简洁、准确，一般不超过25个字
✅ 技术领域：具体明确，避免过于宽泛
✅ 背景技术：至少200字，详细分析现有技术
✅ 技术方案：核心内容，需详细描述
✅ 有益效果：具体、可量化，避免空泛描述
✅ 实施例：提供具体可操作的例子

【专利类型选择指南】
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 发明专利：
   - 保护方法、产品、工艺
   - 保护期限20年
   - 需要实质审查

📌 实用新型：
   - 仅保护产品结构和形状
   - 保护期限10年
   - 无需实质审查
   - 必须有附图

📌 外观设计：
   - 保护产品外观
   - 保护期限15年
   - 必须有图片或照片
    """.strip()
    
    return template


@function_tool
def search_prior_art(
    keywords: str,
    technical_field: Optional[str] = None,
) -> str:
    """
    检索现有技术（用于交底书撰写参考）
    
    Args:
        keywords: 检索关键词（多个用逗号分隔）
        technical_field: 技术领域限定
        
    Returns:
        现有技术检索报告
    """
    try:
        from schemas.patent_schemas import PatentSearchQuery, PatentType
        
        keyword_list = [k.strip() for k in keywords.split(",") if k.strip()]
        
        query = PatentSearchQuery(
            keywords=keyword_list,
            patent_types=[PatentType.INVENTION, PatentType.UTILITY_MODEL],
        )
        
        result = asyncio.run(patent_search_tool.search_patents(query))
        
        report = "=" * 50 + "\n"
        report += "       现有技术检索报告\n"
        report += "=" * 50 + "\n\n"
        
        report += f"📌 检索关键词：{', '.join(keyword_list)}\n"
        if technical_field:
            report += f"📌 技术领域：{technical_field}\n"
        report += f"📌 检索时间：{result.generated_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        report += f"📊 检索结果统计：\n"
        report += f"   总计：{result.total_results} 篇\n"
        report += f"   高相关：{result.high_relevance_count} 篇\n"
        report += f"   中相关：{result.medium_relevance_count} 篇\n"
        report += f"   低相关：{result.low_relevance_count} 篇\n\n"
        
        if result.novelty_analysis:
            report += f"🔍 新颖性分析：\n{result.novelty_analysis}\n\n"
        
        if result.results:
            report += "📚 主要相关专利：\n"
            report += "-" * 40 + "\n"
            for i, patent in enumerate(result.results[:5], 1):
                report += f"\n{i}. {patent.title}\n"
                report += f"   申请人：{patent.applicant}\n"
                if patent.similarity_score:
                    report += f"   相似度：{patent.similarity_score:.2%}\n"
                if patent.abstract:
                    report += f"   摘要：{patent.abstract[:100]}...\n"
        
        if result.recommendations:
            report += "\n💡 撰写建议：\n"
            for rec in result.recommendations:
                report += f"   • {rec}\n"
        
        return report
        
    except Exception as e:
        return f"检索现有技术时发生错误：{str(e)}"


# 创建交底书处理 Agent
disclosure_agent = Agent(
    name="专利交底书助手",
    instructions="""你是一个专业的专利交底书处理专家。你的主要职责是：

【核心功能】
1. 📝 帮助用户填写专利交底书
2. ✅ 验证交底书的完整性和规范性
3. 📄 将交底书转换为正式的专利申请文件
4. 🔍 检索现有技术提供参考

【工作流程】
当用户提交交底书信息时，你应该：
1. 首先调用 validate_disclosure 验证交底书完整性
2. 如果验证通过，调用 process_disclosure_to_patent 生成专利文件
3. 如果验证不通过，指出问题并提供修改建议

【核心规则】
1. 🚫 不要询问不必要的问题，基于现有信息直接工作
2. ✅ 验证不通过时，要明确指出具体问题
3. 📝 生成的专利文件必须完整、规范
4. 🎯 重点关注技术方案和创新点

【交底书必要信息】
1. 发明名称 - 简洁明了
2. 发明人 - 至少一位
3. 申请人 - 公司或个人
4. 技术领域 - 具体明确
5. 背景技术 - 现有技术分析
6. 技术问题 - 要解决的问题
7. 技术方案 - 核心内容
8. 有益效果 - 技术优势

【使用工具】
- get_disclosure_template: 获取交底书模板
- validate_disclosure: 验证交底书
- process_disclosure_to_patent: 生成专利文件
- search_prior_art: 检索现有技术

现在开始工作！""",
    model=gemini_model,
    tools=[
        get_disclosure_template,
        validate_disclosure,
        process_disclosure_to_patent,
        search_prior_art,
    ],
)


async def main():
    """主函数 - 演示交底书处理流程"""
    print("\n" + "=" * 70)
    print("📋 专利交底书处理系统")
    print("=" * 70)
    
    # 检查 API
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ 未配置 GOOGLE_API_KEY")
        return
    
    print(f"✓ API 密钥: {api_key[:10]}...")
    
    # 演示1：获取模板
    print("\n" + "-" * 50)
    print("📋 获取交底书模板")
    print("-" * 50)
    
    result = await Runner.run(
        disclosure_agent,
        "请提供专利交底书模板"
    )
    print(result.final_output)
    
    # 演示2：处理交底书
    print("\n" + "=" * 70)
    print("📝 处理交底书示例")
    print("=" * 70)
    
    disclosure_info = """
    请根据以下交底书信息生成专利申请文件：
    
    发明名称：一种基于深度学习的智能图像识别方法
    发明人：张三，李四
    申请人：智能科技有限公司
    申请人地址：北京市海淀区中关村大街1号
    技术领域：人工智能、图像识别、深度学习
    
    背景技术：
    目前，图像识别技术在工业检测、安防监控等领域有广泛应用。
    传统的图像识别方法主要基于手工特征提取，存在以下问题：
    1. 特征提取依赖人工经验，难以适应复杂场景
    2. 识别准确率受光照、角度等因素影响较大
    3. 处理速度较慢，难以满足实时性要求
    
    要解决的技术问题：
    如何提高图像识别的准确率、鲁棒性和实时性
    
    技术方案：
    本发明提出一种基于深度学习的智能图像识别方法，采用卷积神经网络
    自动提取图像特征，结合注意力机制增强关键区域识别能力。
    
    关键步骤：
    1. 图像预处理，包括尺寸归一化和数据增强
    2. 使用多层卷积网络提取图像特征
    3. 引入注意力机制聚焦关键区域
    4. 通过全连接层进行分类识别
    5. 输出识别结果和置信度
    
    创新点：
    1. 采用轻量级网络结构，提升处理速度
    2. 引入自适应注意力机制，提高复杂场景识别能力
    3. 设计在线学习模块，持续优化模型性能
    
    有益效果：
    1. 识别准确率提升到98%以上
    2. 处理速度达到实时要求（>30fps）
    3. 对光照变化、角度变化具有良好鲁棒性
    4. 模型体积小，易于部署到边缘设备
    """
    
    result = await Runner.run(
        disclosure_agent,
        disclosure_info
    )
    
    print("\n" + result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
