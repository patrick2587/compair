"""Module for preprocessing PDF files for LLM-based analysis."""

import logging
import re
from difflib import unified_diff

from pymupdf4llm import to_markdown

from compair.models import DiffHunk

__all__ = ["cleanup_markdown", "diff_texts", "get_markdown_from_pdf", "parse_pdf_to_markdown"]


def parse_pdf_to_markdown(file_path: str) -> str:
    """Parse a PDF file and return its markdown contents as a single string.

    Args:
        file_path: Path to the PDF file on disk.

    Returns:
        The extracted markdown text. If no text can be extracted, returns an empty string.

    Raises:
        ValueError: If ``file_path`` is not a non-empty string.
    """
    if not isinstance(file_path, str) or not file_path.strip():
        raise ValueError("file_path must be a non-empty string")

    logging.info(f"Parsing PDF to markdown: {file_path}")
    markdown_text = to_markdown(file_path)
    logging.info(f"Parsed PDF '{file_path}' to markdown with {len(markdown_text)} characters")
    return markdown_text


def cleanup_markdown(markdown_text: str) -> str:
    """Clean-up markdown extracted from PDFs to reduce spurious diffs.

    - Collapse single newlines within paragraphs to spaces
    - Remove blank lines entirely (no empty lines in output)
    - Collapse multiple spaces to a single space within lines
    - Trim trailing whitespace on lines

    Args:
        markdown_text: Markdown string extracted from a PDF.

    Returns:
        A cleaned-up markdown string with reduced noise.

    Raises:
        ValueError: If ``markdown_text`` is not a string.
    """
    if not isinstance(markdown_text, str):
        raise ValueError("markdown_text must be a string")

    logging.info(f"Normalizing markdown: input length={len(markdown_text)} characters")
    text = markdown_text.replace("\r\n", "\n").replace("\r", "\n")

    # Split into paragraphs separated by blank lines, normalize each paragraph by
    # replacing internal single newlines with spaces, preserving code fences heuristically.

    paragraphs = re.split(r"\n\s*\n", text)

    normalized_paragraphs = []
    for para in paragraphs:
        if para.strip().startswith("```") and para.strip().endswith("```"):
            normalized_paragraphs.append(para)
            continue

        collapsed = re.sub(r"\n+", " ", para)
        collapsed = re.sub(r"\s{2,}", " ", collapsed)
        collapsed = collapsed.strip()
        normalized_paragraphs.append(collapsed)

    non_empty_paragraphs = [p for p in normalized_paragraphs if p]
    normalized = "\n".join(non_empty_paragraphs)
    normalized = re.sub(r"[ \t]+$", "", normalized, flags=re.MULTILINE)
    logging.info(f"Cleaned-up markdown: output length={len(normalized)} characters")
    return normalized


def diff_texts(text_a: str, text_b: str, n_context_lines: int = 3) -> list[DiffHunk]:
    """Compute a unified diff between two markdown strings.

    Args:
        text_a: Text parsed from the first PDF.
        text_b: Text parsed from the second PDF.
        n_context_lines: Number of context lines to include in the diff.

    Returns:
        A list of ``DiffHunk`` objects representing the differences between ``text_a`` and ``text_b``.

    Raises:
        ValueError: If either input is not a string.
    """
    if not isinstance(text_a, str) or not isinstance(text_b, str):
        raise ValueError("Both inputs must be strings")

    lines_a = text_a.splitlines()
    lines_b = text_b.splitlines()

    logging.info(
        f"Computing unified diff: len(A)={len(lines_a)} lines, len(B)={len(lines_b)} lines, context={n_context_lines}"
    )
    diff_lines = list(unified_diff(lines_a, lines_b, lineterm="", n=n_context_lines))
    hunks = DiffHunk.from_unified_diff_lines(diff_lines[2:])
    logging.info(f"Unified diff produced {len(hunks)} hunks")
    return hunks


def get_markdown_from_pdf(pdf_path: str) -> str:
    """Get the markdown text from a PDF file.

    Args:
        pdf_path: Path to the PDF file.

    Returns:
        Cleaned markdown extracted from the PDF file.

    Raises:
        ValueError: If the provided path is invalid.
    """
    if not isinstance(pdf_path, str) or not pdf_path.strip():
        raise ValueError("pdf_path must be a non-empty string")

    logging.info(f"Extracting markdown from PDF: {pdf_path}")
    text = parse_pdf_to_markdown(str(pdf_path))
    cleaned = cleanup_markdown(text)
    logging.info(f"Extracted and cleaned markdown from '{pdf_path}': {len(cleaned)} characters")
    return cleaned
