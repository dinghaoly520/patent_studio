"""
专利交底书提交系统 - Web 用户界面

基于 Streamlit 的专利交底书提交和处理界面
"""

import streamlit as st
import asyncio
import os
import sys
import json
from datetime import datetime
import traceback
from typing import Optional

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置页面
st.set_page_config(
    page_title="专利交底书提交系统",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 添加自定义 CSS
st.markdown("""
<style>
    /* 主题颜色 */
    :root {
        --primary-color: #1e3a5f;
        --secondary-color: #2e5a8f;
        --accent-color: #ff6b35;
        --bg-gradient: linear-gradient(135deg, #1e3a5f 0%, #2e5a8f 50%, #3d7ab8 100%);
    }
    
    /* 主标题 */
    .main-header {
        font-size: 2.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #1e3a5f, #ff6b35);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        font-family: 'Noto Sans SC', sans-serif;
    }
    
    .sub-title {
        text-align: center;
        color: #6c757d;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* 卡片样式 */
    .info-card {
        background: linear-gradient(145deg, #ffffff, #f5f7fa);
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border-left: 4px solid #1e3a5f;
    }
    
    .success-card {
        background: linear-gradient(145deg, #d4edda, #c3e6cb);
        border-left-color: #28a745;
    }
    
    .warning-card {
        background: linear-gradient(145deg, #fff3cd, #ffeeba);
        border-left-color: #ffc107;
    }
    
    .error-card {
        background: linear-gradient(145deg, #f8d7da, #f5c6cb);
        border-left-color: #dc3545;
    }
    
    /* 步骤指示器 */
    .step-indicator {
        display: flex;
        justify-content: center;
        margin-bottom: 2rem;
    }
    
    .step {
        display: flex;
        align-items: center;
        margin: 0 1rem;
    }
    
    .step-number {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: #e9ecef;
        color: #6c757d;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 0.5rem;
    }
    
    .step-active .step-number {
        background: #1e3a5f;
        color: white;
    }
    
    .step-completed .step-number {
        background: #28a745;
        color: white;
    }
    
    /* 结果展示区 */
    .result-container {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 2rem;
        margin-top: 1.5rem;
        border: 1px solid #dee2e6;
        font-family: 'Courier New', monospace;
        white-space: pre-wrap;
        line-height: 1.6;
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0;
        padding: 10px 20px;
    }
    
    /* 表单样式 */
    .stTextArea textarea {
        border-radius: 8px;
    }
    
    .stTextInput input {
        border-radius: 8px;
    }
    
    /* 按钮样式 */
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* 侧边栏 */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* 进度条 */
    .progress-bar {
        height: 8px;
        background: #e9ecef;
        border-radius: 4px;
        overflow: hidden;
        margin: 1rem 0;
    }
    
    .progress-fill {
        height: 100%;
        background: linear-gradient(90deg, #1e3a5f, #ff6b35);
        transition: width 0.5s ease;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """初始化会话状态"""
    if "disclosure_data" not in st.session_state:
        st.session_state.disclosure_data = {}
    if "current_step" not in st.session_state:
        st.session_state.current_step = 1
    if "validation_result" not in st.session_state:
        st.session_state.validation_result = None
    if "patent_result" not in st.session_state:
        st.session_state.patent_result = None
    if "api_configured" not in st.session_state:
        st.session_state.api_configured = os.getenv("GOOGLE_API_KEY") is not None


async def run_disclosure_agent(task: str, inputs: dict = None):
    """运行交底书处理 agent"""
    try:
        from disclosure_agent import disclosure_agent
        from agents import Runner
        
        if inputs:
            input_text = task + "\n\n" + json.dumps(inputs, ensure_ascii=False, indent=2)
        else:
            input_text = task
        
        result = await Runner.run(disclosure_agent, input_text)
        return result.final_output, None
    except Exception as e:
        error_msg = f"执行任务时发生错误：{str(e)}\n\n{traceback.format_exc()}"
        return None, error_msg


def display_header():
    """显示页面头部"""
    st.markdown('<h1 class="main-header">📋 专利交底书提交系统</h1>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-title">提交技术交底书 → 自动生成专利申请文件</p>',
        unsafe_allow_html=True
    )


def display_step_indicator(current_step: int):
    """显示步骤指示器"""
    steps = ["填写基本信息", "填写技术内容", "验证与预览", "生成专利文件"]
    
    cols = st.columns(len(steps))
    for i, (col, step_name) in enumerate(zip(cols, steps), 1):
        with col:
            if i < current_step:
                st.markdown(f"✅ **步骤{i}**: {step_name}")
            elif i == current_step:
                st.markdown(f"🔵 **步骤{i}**: {step_name}")
            else:
                st.markdown(f"⚪ 步骤{i}: {step_name}")


def step1_basic_info():
    """步骤1：填写基本信息"""
    st.markdown("### 📌 基本信息")
    
    col1, col2 = st.columns(2)
    
    with col1:
        title = st.text_input(
            "发明名称 *",
            value=st.session_state.disclosure_data.get("title", ""),
            placeholder="例如：一种基于深度学习的智能推荐方法",
            help="简洁明了地描述发明，一般不超过25个字"
        )
        
        patent_type = st.selectbox(
            "专利类型 *",
            options=["invention", "utility_model", "design"],
            format_func=lambda x: {
                "invention": "发明专利",
                "utility_model": "实用新型专利", 
                "design": "外观设计专利"
            }[x],
            index=["invention", "utility_model", "design"].index(
                st.session_state.disclosure_data.get("patent_type", "invention")
            )
        )
        
        technical_field = st.text_input(
            "技术领域 *",
            value=st.session_state.disclosure_data.get("technical_field", ""),
            placeholder="例如：人工智能、机器学习、数据挖掘",
            help="明确说明发明所属的技术领域"
        )
    
    with col2:
        applicant_name = st.text_input(
            "申请人名称 *",
            value=st.session_state.disclosure_data.get("applicant_name", ""),
            placeholder="公司名称或个人姓名"
        )
        
        applicant_address = st.text_input(
            "申请人地址",
            value=st.session_state.disclosure_data.get("applicant_address", ""),
            placeholder="详细地址"
        )
        
        inventors = st.text_input(
            "发明人 *",
            value=st.session_state.disclosure_data.get("inventors", ""),
            placeholder="多个发明人用逗号分隔，如：张三, 李四",
            help="至少填写一位发明人"
        )
    
    contact_email = st.text_input(
        "联系邮箱",
        value=st.session_state.disclosure_data.get("contact_email", ""),
        placeholder="用于后续沟通"
    )
    
    # 保存数据
    st.session_state.disclosure_data.update({
        "title": title,
        "patent_type": patent_type,
        "technical_field": technical_field,
        "applicant_name": applicant_name,
        "applicant_address": applicant_address,
        "inventors": inventors,
        "contact_email": contact_email,
    })
    
    # 验证必填项
    is_valid = all([title, technical_field, applicant_name, inventors])
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("下一步 →", type="primary", use_container_width=True, disabled=not is_valid):
            st.session_state.current_step = 2
            st.rerun()
    
    if not is_valid:
        st.warning("请填写所有必填项（标记 * 的字段）")


def step2_technical_content():
    """步骤2：填写技术内容"""
    st.markdown("### 📝 技术内容")
    
    # 背景技术
    st.markdown("#### 背景技术 *")
    background_description = st.text_area(
        "描述现有技术的状况及存在的问题",
        value=st.session_state.disclosure_data.get("background_description", ""),
        height=150,
        placeholder="""请详细描述：
1. 现有技术的发展状况
2. 现有技术方案存在的问题和不足
3. 这些问题带来的影响""",
        help="至少50个字符"
    )
    
    # 技术问题
    st.markdown("#### 要解决的技术问题 *")
    technical_problems = st.text_area(
        "明确指出本发明要解决的具体技术问题",
        value=st.session_state.disclosure_data.get("technical_problems", ""),
        height=100,
        placeholder="例如：如何提高系统的处理速度和准确率...",
    )
    
    # 技术方案
    st.markdown("#### 技术方案 *")
    technical_solution = st.text_area(
        "详细描述本发明的技术方案",
        value=st.session_state.disclosure_data.get("technical_solution", ""),
        height=200,
        placeholder="""请详细描述您的技术方案，包括：
1. 整体技术思路
2. 主要技术手段
3. 各组成部分的功能和作用""",
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 关键步骤")
        key_steps = st.text_area(
            "技术方案的关键步骤（用分号分隔）",
            value=st.session_state.disclosure_data.get("key_steps", ""),
            height=100,
            placeholder="步骤1描述; 步骤2描述; 步骤3描述",
        )
    
    with col2:
        st.markdown("#### 创新点")
        innovation_points = st.text_area(
            "技术方案的创新点（用分号分隔）",
            value=st.session_state.disclosure_data.get("innovation_points", ""),
            height=100,
            placeholder="创新点1; 创新点2; 创新点3",
        )
    
    # 有益效果
    st.markdown("#### 有益效果 *")
    beneficial_effects = st.text_area(
        "与现有技术相比的有益效果（用分号分隔）",
        value=st.session_state.disclosure_data.get("beneficial_effects", ""),
        height=100,
        placeholder="效果1; 效果2; 效果3",
    )
    
    # 具体实施例
    st.markdown("#### 具体实施例")
    embodiments = st.text_area(
        "提供具体的实施例（用分号分隔多个实施例）",
        value=st.session_state.disclosure_data.get("embodiments", ""),
        height=150,
        placeholder="实施例1的详细描述; 实施例2的详细描述",
    )
    
    # 附图说明
    st.markdown("#### 附图说明")
    figure_descriptions = st.text_area(
        "附图说明（用分号分隔）",
        value=st.session_state.disclosure_data.get("figure_descriptions", ""),
        height=100,
        placeholder="图1为系统架构图; 图2为流程图; 图3为效果对比图",
    )
    
    # 保存数据
    st.session_state.disclosure_data.update({
        "background_description": background_description,
        "technical_problems": technical_problems,
        "technical_solution": technical_solution,
        "key_steps": key_steps,
        "innovation_points": innovation_points,
        "beneficial_effects": beneficial_effects,
        "embodiments": embodiments,
        "figure_descriptions": figure_descriptions,
    })
    
    # 验证必填项
    is_valid = all([background_description, technical_problems, technical_solution, beneficial_effects])
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← 上一步", use_container_width=True):
            st.session_state.current_step = 1
            st.rerun()
    with col3:
        if st.button("下一步 →", type="primary", use_container_width=True, disabled=not is_valid):
            st.session_state.current_step = 3
            st.rerun()
    
    if not is_valid:
        st.warning("请填写所有必填项")


def step3_validation():
    """步骤3：验证与预览"""
    st.markdown("### ✅ 验证与预览")
    
    # 显示已填写信息摘要
    data = st.session_state.disclosure_data
    
    with st.expander("📋 已填写信息预览", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            **发明名称**: {data.get('title', '')}
            
            **专利类型**: {{'invention': '发明专利', 'utility_model': '实用新型', 'design': '外观设计'}.get(data.get('patent_type', ''), '')}
            
            **技术领域**: {data.get('technical_field', '')}
            
            **申请人**: {data.get('applicant_name', '')}
            
            **发明人**: {data.get('inventors', '')}
            """)
        
        with col2:
            st.markdown(f"""
            **背景技术**: {data.get('background_description', '')[:100]}...
            
            **技术问题**: {data.get('technical_problems', '')[:100]}...
            
            **技术方案**: {data.get('technical_solution', '')[:100]}...
            """)
    
    # 验证按钮
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 验证交底书完整性", type="primary", use_container_width=True):
            with st.spinner("正在验证交底书..."):
                # 构建验证任务
                validation_task = f"""
                请验证以下专利交底书的完整性：
                
                发明名称：{data.get('title', '')}
                发明人：{data.get('inventors', '')}
                申请人：{data.get('applicant_name', '')}
                技术领域：{data.get('technical_field', '')}
                背景技术：{data.get('background_description', '')}
                技术问题：{data.get('technical_problems', '')}
                技术方案：{data.get('technical_solution', '')}
                有益效果：{data.get('beneficial_effects', '')}
                专利类型：{data.get('patent_type', 'invention')}
                """
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result, error = loop.run_until_complete(run_disclosure_agent(validation_task))
                loop.close()
                
                if error:
                    st.session_state.validation_result = {"status": "error", "message": error}
                else:
                    st.session_state.validation_result = {"status": "success", "message": result}
                
                st.rerun()
    
    # 显示验证结果
    if st.session_state.validation_result:
        result = st.session_state.validation_result
        if result["status"] == "success":
            if "验证通过" in result["message"] or "✅" in result["message"]:
                st.markdown('<div class="info-card success-card">', unsafe_allow_html=True)
            else:
                st.markdown('<div class="info-card warning-card">', unsafe_allow_html=True)
            st.markdown(result["message"])
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="info-card error-card">', unsafe_allow_html=True)
            st.error(result["message"])
            st.markdown('</div>', unsafe_allow_html=True)
    
    # 导航按钮
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← 上一步", use_container_width=True):
            st.session_state.current_step = 2
            st.rerun()
    with col3:
        if st.button("生成专利文件 →", type="primary", use_container_width=True):
            st.session_state.current_step = 4
            st.rerun()


def step4_generate():
    """步骤4：生成专利文件"""
    st.markdown("### 📄 生成专利申请文件")
    
    data = st.session_state.disclosure_data
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 开始生成专利申请文件", type="primary", use_container_width=True):
            with st.spinner("正在生成专利申请文件，这可能需要几分钟..."):
                # 构建生成任务
                generate_task = f"""
                请根据以下交底书信息生成完整的专利申请文件：
                
                发明名称：{data.get('title', '')}
                发明人：{data.get('inventors', '')}
                申请人：{data.get('applicant_name', '')}
                申请人地址：{data.get('applicant_address', '待填写')}
                联系邮箱：{data.get('contact_email', '')}
                技术领域：{data.get('technical_field', '')}
                专利类型：{data.get('patent_type', 'invention')}
                
                背景技术：
                {data.get('background_description', '')}
                
                要解决的技术问题：
                {data.get('technical_problems', '')}
                
                技术方案：
                {data.get('technical_solution', '')}
                
                关键步骤：
                {data.get('key_steps', '')}
                
                创新点：
                {data.get('innovation_points', '')}
                
                有益效果：
                {data.get('beneficial_effects', '')}
                
                具体实施例：
                {data.get('embodiments', '')}
                
                附图说明：
                {data.get('figure_descriptions', '')}
                """
                
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result, error = loop.run_until_complete(run_disclosure_agent(generate_task))
                loop.close()
                
                if error:
                    st.session_state.patent_result = {"status": "error", "message": error}
                else:
                    st.session_state.patent_result = {"status": "success", "message": result}
                
                st.rerun()
    
    # 显示生成结果
    if st.session_state.patent_result:
        result = st.session_state.patent_result
        
        if result["status"] == "success":
            st.success("✅ 专利申请文件生成成功！")
            
            # 显示选项卡
            tab1, tab2 = st.tabs(["📄 专利文件", "📥 下载"])
            
            with tab1:
                st.markdown('<div class="result-container">', unsafe_allow_html=True)
                st.text(result["message"])
                st.markdown('</div>', unsafe_allow_html=True)
            
            with tab2:
                # 生成文件名
                filename = f"专利申请文件_{data.get('title', '未命名')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                
                st.download_button(
                    label="📥 下载专利申请文件（TXT）",
                    data=result["message"],
                    file_name=filename,
                    mime="text/plain",
                    use_container_width=True,
                )
                
                # JSON格式
                json_data = {
                    "disclosure_data": data,
                    "patent_document": result["message"],
                    "generated_at": datetime.now().isoformat(),
                }
                json_filename = f"专利数据_{data.get('title', '未命名')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                st.download_button(
                    label="📥 下载完整数据（JSON）",
                    data=json.dumps(json_data, ensure_ascii=False, indent=2),
                    file_name=json_filename,
                    mime="application/json",
                    use_container_width=True,
                )
        else:
            st.error("生成失败")
            st.markdown('<div class="info-card error-card">', unsafe_allow_html=True)
            st.error(result["message"])
            st.markdown('</div>', unsafe_allow_html=True)
    
    # 导航按钮
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← 返回修改", use_container_width=True):
            st.session_state.current_step = 3
            st.rerun()
    with col3:
        if st.button("🔄 重新开始", use_container_width=True):
            st.session_state.disclosure_data = {}
            st.session_state.current_step = 1
            st.session_state.validation_result = None
            st.session_state.patent_result = None
            st.rerun()


def disclosure_template_page():
    """交底书模板页面"""
    st.markdown("### 📋 专利交底书模板")
    
    template = """
# 专利交底书

## 一、基本信息

| 项目 | 内容 |
|------|------|
| 发明名称 | [简洁明了，体现技术特点，不超过25字] |
| 专利类型 | □ 发明专利  □ 实用新型  □ 外观设计 |
| 申请人 | [公司名称或个人姓名] |
| 申请人地址 | [详细地址] |
| 发明人 | [姓名1, 姓名2, ...] |
| 联系方式 | [电话/邮箱] |

## 二、技术领域

[本发明涉及的技术领域，如：人工智能、机械制造、电子通信等]

## 三、背景技术

### 3.1 现有技术描述
[描述当前该技术领域的发展状况和现有解决方案]

### 3.2 存在的问题
[详细列出现有技术存在的问题和不足]
1. 问题一：...
2. 问题二：...
3. 问题三：...

## 四、要解决的技术问题

[明确指出本发明要解决的具体技术问题]

## 五、技术方案

### 5.1 方案概述
[整体技术思路和方案框架]

### 5.2 具体步骤
步骤1：[描述]
步骤2：[描述]
步骤3：[描述]
...

### 5.3 关键技术点
1. [关键技术1]
2. [关键技术2]
3. [关键技术3]

### 5.4 创新点
1. [创新点1]
2. [创新点2]
3. [创新点3]

## 六、有益效果

[与现有技术相比，本发明的有益效果]
1. [效果1，尽量量化]
2. [效果2，尽量量化]
3. [效果3，尽量量化]

## 七、具体实施例

### 实施例1
[详细描述第一个具体实施例]

### 实施例2（可选）
[详细描述第二个具体实施例]

## 八、附图说明

图1：[图1的内容说明]
图2：[图2的内容说明]
图3：[图3的内容说明]

---

## 填写说明

1. **发明名称**：应简洁、准确地反映发明的主题
2. **技术领域**：应具体明确，避免过于宽泛
3. **背景技术**：详细分析现有技术，至少200字
4. **技术方案**：核心内容，需详细描述实现方式
5. **有益效果**：具体、可量化，避免空泛描述
6. **实施例**：提供具体可操作的实施方案
"""
    
    st.markdown(template)
    
    # 下载模板
    st.download_button(
        label="📥 下载交底书模板",
        data=template,
        file_name="专利交底书模板.md",
        mime="text/markdown",
        use_container_width=True,
    )


def main():
    """主函数"""
    init_session_state()
    display_header()
    
    # 检查 API 配置
    if not st.session_state.api_configured:
        st.warning("⚠️ 未配置 GOOGLE_API_KEY 环境变量，部分功能可能不可用")
    
    # 侧边栏导航
    with st.sidebar:
        st.markdown("### 📋 功能导航")
        
        page = st.radio(
            "选择功能",
            ["📝 提交交底书", "📋 交底书模板", "❓ 使用帮助"],
            index=0
        )
        
        st.markdown("---")
        
        # API 状态
        if st.session_state.api_configured:
            st.success("🟢 API 已配置")
        else:
            st.error("🔴 API 未配置")
        
        st.markdown("---")
        
        # 当前进度
        if page == "📝 提交交底书":
            st.markdown("### 📊 当前进度")
            progress = (st.session_state.current_step - 1) / 4 * 100
            st.progress(int(progress))
            st.markdown(f"步骤 {st.session_state.current_step}/4")
    
    # 主内容区
    if page == "📝 提交交底书":
        display_step_indicator(st.session_state.current_step)
        st.markdown("---")
        
        if st.session_state.current_step == 1:
            step1_basic_info()
        elif st.session_state.current_step == 2:
            step2_technical_content()
        elif st.session_state.current_step == 3:
            step3_validation()
        elif st.session_state.current_step == 4:
            step4_generate()
    
    elif page == "📋 交底书模板":
        disclosure_template_page()
    
    elif page == "❓ 使用帮助":
        st.markdown("""
        ### 📖 使用帮助
        
        #### 什么是专利交底书？
        
        专利交底书是发明人向专利代理机构或专利撰写人员提供的技术说明文档，
        包含发明的技术背景、技术方案、有益效果等内容，用于撰写正式的专利申请文件。
        
        #### 使用流程
        
        1. **填写基本信息**：包括发明名称、申请人、发明人等
        2. **填写技术内容**：包括背景技术、技术方案、有益效果等
        3. **验证与预览**：检查交底书的完整性
        4. **生成专利文件**：AI自动生成专利申请文件
        
        #### 专利类型说明
        
        | 类型 | 保护对象 | 保护期限 | 特点 |
        |------|----------|----------|------|
        | 发明专利 | 方法、产品、工艺 | 20年 | 需实质审查 |
        | 实用新型 | 产品结构和形状 | 10年 | 无需实质审查，必须有附图 |
        | 外观设计 | 产品外观 | 15年 | 需要图片或照片 |
        
        #### 注意事项
        
        - 所有标记 * 的字段为必填项
        - 技术描述越详细，生成的专利文件质量越高
        - 建议提供具体的实施例和附图说明
        - 生成的专利文件仅供参考，正式申请前请专业人员审核
        """)


if __name__ == "__main__":
    main()
