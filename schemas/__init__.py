"""
专利 agent 数据模型
"""

from .patent_schemas import (
    PatentType,
    ApplicationStatus,
    ReviewResultStatus,
    ApplicantInfo,
    InventorInfo,
    PatentClaim,
    PatentFigure,
    PatentApplication,
    ReviewIssue,
    ReviewResult,
    PatentSearchQuery,
    PatentSearchResult,
    PatentSearchReport,
    PatentDraftRequest,
    PatentWorkflowRequest,
)

from .disclosure_schemas import (
    DisclosureStatus,
    TechnicalProblem,
    TechnicalSolution,
    AttachmentInfo,
    PatentDisclosure,
    DisclosureToPatentRequest,
    DisclosureValidationResult,
)

__all__ = [
    # Patent schemas
    "PatentType",
    "ApplicationStatus",
    "ReviewResultStatus",
    "ApplicantInfo",
    "InventorInfo",
    "PatentClaim",
    "PatentFigure",
    "PatentApplication",
    "ReviewIssue",
    "ReviewResult",
    "PatentSearchQuery",
    "PatentSearchResult",
    "PatentSearchReport",
    "PatentDraftRequest",
    "PatentWorkflowRequest",
    # Disclosure schemas
    "DisclosureStatus",
    "TechnicalProblem",
    "TechnicalSolution",
    "AttachmentInfo",
    "PatentDisclosure",
    "DisclosureToPatentRequest",
    "DisclosureValidationResult",
]
