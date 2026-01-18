"""
专利 agent 配置模块
"""

from .review_rules import (
    RuleManager,
    ReviewRule,
    ReviewRuleConfig,
    ReviewSeverity,
    PatentType,
    DEFAULT_PRE_REVIEW_RULES,
    DEFAULT_FIGURE_REVIEW_RULES,
    DEFAULT_SEARCH_RULES,
)

from .model_config import (
    ModelConfig,
    DEEPSEEK_CONFIG,
    GEMINI_CONFIG,
    DEFAULT_CONFIG,
    create_model,
    get_deepseek_model,
    get_gemini_model,
)

__all__ = [
    # Review rules
    "RuleManager",
    "ReviewRule",
    "ReviewRuleConfig",
    "ReviewSeverity",
    "PatentType",
    "DEFAULT_PRE_REVIEW_RULES",
    "DEFAULT_FIGURE_REVIEW_RULES",
    "DEFAULT_SEARCH_RULES",
    # Model config
    "ModelConfig",
    "DEEPSEEK_CONFIG",
    "GEMINI_CONFIG",
    "DEFAULT_CONFIG",
    "create_model",
    "get_deepseek_model",
    "get_gemini_model",
]
