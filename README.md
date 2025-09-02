# Comp*AI*r - AI-based legal document comparison

## Prerequisites

- **uv**: Fast Python package and project manager by Astral. Install it using one of the following:
  - macOS (Homebrew):
    ```bash
    brew install uv
    ```
  - Official installer (all platforms):
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```
  - Docs: [`https://docs.astral.sh/uv/`](https://docs.astral.sh/uv/)

## Usage

- **Install dependencies** (creates/updates the virtual environment):
  ```bash
  uv sync
  ```

- **Check code is formatted** (no changes are made):
  ```bash
  uv run ruff format . --check
  ```

- **Run lints**:
  ```bash
  uv run ruff check .
  ```

- **Create dependency list**:
  ```bash
  uv export --format requirements-txt --no-hashes --no-build > generated/requirements.txt
  ```

## Approach

|                       | no-llm      | llm-light   | ... | llm-heavy   | llm-only |
|-----------------------|-------------|-------------|-----|-------------|----------|
| parsing               | pymupdf4llm | pymupdf4llm |     | pymupdf4llm | LLM API  |
| normalization         | textacy     | textacy     |     | textacy     | LLM API  |
| clean-up              | textacy     | textacy     |     | textacy     | LLM API  |
| alignment             | rule-based  | rule-based  |     | LLM API     | LLM API  |
| change detection      | difflib     | difflib     |     | LLM API     | LLM API  |
| change categorization | rule-based  | rule-based  |     | LLM API     | LLM API  |
| impact analysis       | rule-based  | LLM API     |     | LLM API     | LLM API  |
| output generation     | rule-based  | rule-based  |     | LLM API     | LLM API  |

- **no-llm**: Fully deterministic, audit-friendly pipeline. Uses `pymupdf4llm` + classical
  preprocessing (e.g., textacy) for parsing/normalization/clean-up, rule-based alignment,
  `difflib` for change detection, rule-based categorization, impact analysis, and output generation.

- **llm-light**: Primarily deterministic with selective LLM assistance. Preprocessing, alignment,
  change detection, categorization, and output generation remain rule-based; the LLM is used for
  impact analysis to add expert reasoning while preserving traceability.

- **llm-heavy**: Deterministic preprocessing (parsing/normalization/clean-up via `pymupdf4llm` and
  textacy), then delegate alignment, change detection, categorization, impact analysis, and output
  generation to the LLM. Higher flexibility and coverage, with less predictability and higher cost.

- **llm-only**: End-to-end LLM pipeline. Parsing is handled by the LLM API provider. Maximizes
  adaptability and speed of iteration, but is the least deterministic and most costly to operate.

- **hybrid**: Many practical setups blend deterministic steps with selective LLM calls for a balance
  of cost, speed, and explainability:
  - LLM-assisted normalization: use classical preprocessing first, then invoke an LLM to resolve
    stubborn layout issues (tables, footnotes) when heuristics fail.
  - Heuristic alignment with LLM tie-breakers: align by anchors and structure; ask an LLM only for
    ambiguous sections (e.g., reordered clauses).
  - Rule-first categorization with LLM fallback: apply precise rules; backstop edge cases with an LLM
    for nuanced classification.
  - Deterministic diff, LLM impact narrative: compute changes with `difflib`; have the LLM explain
    legal/operational implications and generate summaries.
  - Confidence thresholds and human-in-the-loop: escalate to LLM or reviewer only when signals
    (similarity, coverage) drop below thresholds.