import json
import os
from pathlib import Path

import pytest

from compair.llm import run_llm_heavy, run_llm_light

RESOURCES_DIR = Path(__file__).parent / "resources"
RESULTS_DIR = Path(__file__).parent.parent / "generated"


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"), reason="Requires OPENAI_API_KEY to run LLM test"
)
@pytest.mark.parametrize("analysis_type", ["light"])
def test_run_llm_heavy(analysis_type: str) -> None:
    pdf_a = RESOURCES_DIR / "1.pdf"
    pdf_b = RESOURCES_DIR / "2.pdf"

    if analysis_type == "heavy":
        report = run_llm_heavy(pdf_a, pdf_b)
    if analysis_type == "light":
        report = run_llm_light(pdf_a, pdf_b)
    else:
        raise ValueError(f"Invalid analysis type: {analysis_type}")

    # store the result JSON under resources for inspection
    out_path = RESULTS_DIR / f"llm_{analysis_type}_diff_report.json"
    out_path.write_text(
        json.dumps(report.model_dump(), indent=2, ensure_ascii=False), encoding="utf-8"
    )

    assert out_path.exists() and out_path.stat().st_size > 0
