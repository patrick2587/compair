import json
from pathlib import Path

from compair.models import DifferenceReportWithInputs

RESULTS_DIR = Path(__file__).parent.parent / "generated"


def test_generate_api() -> None:
    """Generate JSON schema for DifferenceReportWithInputs for the web viewer."""
    schema = DifferenceReportWithInputs.model_json_schema()

    out_path = RESULTS_DIR / "api.json"
    out_path.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")

    assert out_path.exists()
    data = json.loads(out_path.read_text(encoding="utf-8"))
    # Basic sanity checks for a JSON Schema-like structure
    assert isinstance(data, dict)
    assert "title" in data and "type" in data and "properties" in data
