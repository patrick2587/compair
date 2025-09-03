from pathlib import Path

import pytest

from compair.preprocessing import (
    cleanup_markdown,
    diff_texts,
    parse_pdf_to_markdown,
)

RESOURCES_DIR = Path(__file__).parent / "resources"


@pytest.mark.parametrize(
    "pdf_file_path",
    ["1.pdf", "2.pdf"],
)
def test_parse_pdf_to_markdown(pdf_file_path: str) -> None:
    pdf_path = RESOURCES_DIR / pdf_file_path

    assert pdf_path.exists(), f"Missing test resource: {pdf_path}"

    text = parse_pdf_to_markdown(str(pdf_path))

    assert isinstance(text, str)
    assert text.strip() != ""


@pytest.mark.parametrize("left,right", [("1.pdf", "2.pdf")])
def test_diff_texts(left: str, right: str) -> None:
    left_text = parse_pdf_to_markdown(str(RESOURCES_DIR / left))
    right_text = parse_pdf_to_markdown(str(RESOURCES_DIR / right))

    diff = diff_texts(cleanup_markdown(left_text), cleanup_markdown(right_text))
    assert isinstance(diff[0].unified_diff, str)


@pytest.mark.parametrize(
    "input_text,expected",
    [
        (
            "This is a line\nthat wrapped in PDF.\n\nNext paragraph stays.\n",
            "This is a line that wrapped in PDF.\nNext paragraph stays.",
        ),
        (
            "Line with  multiple    spaces\nshould   collapse.",
            "Line with multiple spaces should collapse.",
        ),
        (
            "```\ncode block\nwith line breaks\n```",
            "```\ncode block\nwith line breaks\n```",
        ),
    ],
)
def test_cleanup_markdown(input_text: str, expected: str) -> None:
    assert cleanup_markdown(input_text) == expected
