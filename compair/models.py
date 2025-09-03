import logging
import re
from typing import List, Literal, Optional

from pydantic import BaseModel, Field

ChangeType = Literal["added", "removed", "modified", "moved"]
Category = Literal["Critical", "Minor", "Formatting"]
Severity = Literal["low", "medium", "high"]
Party = Literal["Data Controller", "Data Processor", "Both"]


class HunkHeader(BaseModel):
    start_line_old: int = Field(description="The start line of the change.")
    end_line_old: int = Field(description="The end line of the change.")
    start_line_new: int = Field(description="The start line of the change.")
    end_line_new: int = Field(description="The end line of the change.")


class DiffHunk(BaseModel):
    unified_diff: str = Field(description="The unified diff of the two documents.")
    old_excerpt: Optional[str] = Field(default=None, description="The old excerpt of the change.")
    new_excerpt: Optional[str] = Field(default=None, description="The new excerpt of the change.")
    hunk_header: HunkHeader = Field(description="The hunk header of the change.")

    @classmethod
    def from_unified_diff_lines(cls, diff_lines: List[str]) -> List["DiffHunk"]:
        """Convert unified diff lines into a list of ``DiffHunk`` models.

        Expects header lines in the form: ``@@ -<start_old>,<len_old> +<start_new>,<len_new> @@``.

        Args:
            diff_lines: Lines from a unified diff (including header and +/- context lines).

        Returns:
            A list of ``DiffHunk`` instances parsed from the provided unified diff lines.
        """
        result: List[DiffHunk] = []

        current_diff_lines: List[str] = []
        current_new_excerpt: List[str] = []
        current_old_excerpt: List[str] = []

        header_re = re.compile(r"^@@ -([0-9]+),([0-9]+) \+([0-9]+),([0-9]+) @@")

        def flush_block(match_groups: Optional[List[str]]) -> None:
            nonlocal current_diff_lines, current_new_excerpt, current_old_excerpt, result
            if not current_diff_lines or match_groups is None:
                return
            start_old, len_old, start_new, len_new = map(int, match_groups)
            result.append(
                cls(
                    unified_diff="\n".join(current_diff_lines),
                    old_excerpt="\n".join(current_old_excerpt) if current_old_excerpt else None,
                    new_excerpt="\n".join(current_new_excerpt) if current_new_excerpt else None,
                    hunk_header=HunkHeader(
                        start_line_old=start_old,
                        end_line_old=start_old + len_old,  # FIX: -1 since last line is included
                        start_line_new=start_new,
                        end_line_new=start_new + len_new,  # FIX: -1 since last line is included
                    ),
                )
            )

        last_header_groups: Optional[List[str]] = None

        for line in diff_lines:
            m = header_re.match(line)
            if m:
                # Flush previous block before starting a new one
                flush_block(last_header_groups)
                last_header_groups = list(m.groups())
                # Reset and start new block, include header line in unified diff
                current_diff_lines = [line]
                current_new_excerpt = []
                current_old_excerpt = []
                continue

            if line.startswith("+"):
                current_new_excerpt.append(line[1:])
                current_diff_lines.append(line)
            elif line.startswith("-"):
                current_old_excerpt.append(line[1:])
                current_diff_lines.append(line)
            else:
                current_diff_lines.append(line)

        # Flush last collected block
        flush_block(last_header_groups)

        logging.info(f"Converted unified diff into {len(result)} hunks")
        return result


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
    summary: Optional[str] = Field(
        default=None,
        description="Optional high-level summary as single sentence.",
    )


class Change(BaseModel):
    change_id: Optional[str] = Field(
        default=None,
        description="Stable identifier for the change (e.g. UUID).",
    )
    diff_hunk: DiffHunk = Field(description="The diff hunk of the change.")
    change_classification: ChangeClassification = Field(
        description="The change classification, including optional impact analysis for critical changes only."
    )


class DifferenceReport(BaseModel):
    changes: List[Change] = Field(description="The list of detected and categorized changes.")
    summary: Optional[str] = Field(
        default=None,
        description="Optional high-level summary as single sentence.",
    )


class DifferenceReportWithInputs(BaseModel):
    document_a: str = Field(description="Parsed markdown text of the first PDF.")
    document_b: str = Field(description="Parsed markdown text of the second PDF.")
    difference_report: DifferenceReport = Field(description="The difference report.")
