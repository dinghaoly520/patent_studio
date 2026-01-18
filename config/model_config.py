"""
大模型配置

支持多种大模型提供商：DeepSeek、OpenAI、Google Gemini 等
"""

import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class ModelConfig:
    """模型配置"""
    provider: str  # 提供商: deepseek, openai, gemini
    model_name: str  # 模型名称
    api_key: str  # API 密钥
    base_url: Optional[str] = None  # API 基础 URL
    temperature: float = 0.7  # 温度参数
    max_tokens: int = 4096  # 最大 token 数


# DeepSeek 配置
DEEPSEEK_CONFIG = ModelConfig(
    provider="deepseek",
    model_name="deepseek-chat",
    api_key="sk-aa4f554b2247422599848e6f10b154ff",
    base_url="https://api.deepseek.com/v1",
    temperature=0.7,
    max_tokens=4096,
)

# Gemini 配置（备用）
GEMINI_CONFIG = ModelConfig(
    provider="gemini",
    model_name="gemini/gemini-2.0-flash-exp",
    api_key=os.getenv("GOOGLE_API_KEY", ""),
    temperature=0.7,
    max_tokens=4096,
)

# 默认使用 DeepSeek
DEFAULT_CONFIG = DEEPSEEK_CONFIG


def create_model(config: ModelConfig = None):
    """
    创建大模型实例
    
    Args:
        config: 模型配置，默认使用 DeepSeek
        
    Returns:
        模型实例
    """
    if config is None:
        config = DEFAULT_CONFIG
    
    try:
        from agents.extensions.models.litellm_model import LitellmModel
        
        if config.provider == "deepseek":
            # DeepSeek 使用 OpenAI 兼容接口
            model = LitellmModel(
                model=f"openai/{config.model_name}",
                api_key=config.api_key,
                base_url=config.base_url,
            )
            print(f"✓ DeepSeek 模型初始化成功: {config.model_name}")
            
        elif config.provider == "gemini":
            model = LitellmModel(
                model=config.model_name,
                api_key=config.api_key,
            )
            print(f"✓ Gemini 模型初始化成功: {config.model_name}")
            
        elif config.provider == "openai":
            model = LitellmModel(
                model=config.model_name,
                api_key=config.api_key,
            )
            print(f"✓ OpenAI 模型初始化成功: {config.model_name}")
            
        else:
            raise ValueError(f"不支持的模型提供商: {config.provider}")
        
        return model
        
    except Exception as e:
        print(f"✗ 模型初始化失败: {e}")
        return None


def get_deepseek_model():
    """获取 DeepSeek 模型"""
    return create_model(DEEPSEEK_CONFIG)


def get_gemini_model():
    """获取 Gemini 模型"""
    return create_model(GEMINI_CONFIG)
