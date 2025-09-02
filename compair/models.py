from typing import List, Literal, Optional

from pydantic import BaseModel, Field

ChangeType = Literal["added", "removed", "modified", "moved"]
Category = Literal["Critical", "Minor", "Formatting"]
Severity = Literal["low", "medium", "high"]
Party = Literal["Data Controller", "Data Processor", "Both"]


class UnifiedDiff(BaseModel):
    unified_diff: str = Field(description="The unified diff of the two documents.")
    old_excerpt: Optional[str] = Field(default=None, description="The old excerpt of the change.")
    new_excerpt: Optional[str] = Field(default=None, description="The new excerpt of the change.")


class ImpactAnalysis(BaseModel):
    severity: Severity
    party_affected: List[Party]
    rationale: str = Field(description="One-sentence explanation of the legal/operational impact.")


class ChangeClassification(BaseModel):
    change_type: ChangeType
    category: Category
    confidence: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Model confidence for this item."
    )
    location: Optional[str] = Field(
        default=None,
        description="Clause identifier if present (e.g., '5.1.1', 'Appendix 3').",
    )
    impact_analysis: Optional[ImpactAnalysis] = Field(
        default=None,
        description="Optional impact analysis for critical changes only. Otherwise, set to None.",
    )


class Change(BaseModel):
    change_id: Optional[str] = Field(
        default=None,
        description="Stable identifier for the change (e.g. UUID).",
    )
    old_excerpt: Optional[str] = Field(default=None, description="Minimal snippet from document A.")
    new_excerpt: Optional[str] = Field(default=None, description="Minimal snippet from document B.")
    change_classification: ChangeClassification = Field(
        description="The change classification, including optional impact analysis for critical changes only."
    )


class DifferenceReport(BaseModel):
    changes: List[Change] = Field(description="The list of detected and categorized changes.")
    summary: Optional[str] = Field(
        default=None,
        description="Optional high-level summary (<= 120 words).",
    )


class DifferenceReportWithInputs(BaseModel):
    document_a: str = Field(description="Parsed markdown text of the first PDF.")
    document_b: str = Field(description="Parsed markdown text of the second PDF.")
    difference_report: DifferenceReport = Field(description="The difference report.")
