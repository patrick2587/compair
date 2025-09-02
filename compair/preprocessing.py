import logging
from difflib import unified_diff

from pymupdf4llm import to_markdown

from compair.models import UnifiedDiff

__all__ = ["cleanup_markdown", "diff_texts", "get_markdown_from_pdf", "parse_pdf_to_markdown"]


def parse_pdf_to_markdown(file_path: str) -> str:
    """Parse a PDF file and return its markdown contents as a single string.

    Args:
        file_path: Path to the PDF file on disk.

    Returns:
        The extracted markdown text. If no text can be extracted, returns an empty string.
    """
    if not isinstance(file_path, str) or not file_path.strip():
        raise ValueError("file_path must be a non-empty string")

    logging.info(f"Parsing PDF to markdown: {file_path}")
    markdown_text = to_markdown(file_path)
    logging.info(f"Parsed PDF '{file_path}' to markdown with {len(markdown_text)} characters")
    return markdown_text


def cleanup_markdown(markdown_text: str) -> str:
    """Normalize markdown extracted from PDFs to reduce spurious diffs.

    - Collapse single newlines within paragraphs to spaces
    - Remove blank lines entirely (no empty lines in output)
    - Collapse multiple spaces to a single space within lines
    - Trim trailing whitespace on lines

    Args:
        markdown_text: Markdown string extracted from a PDF.

    Returns:
        A normalized markdown string with reduced noise.
    """
    if not isinstance(markdown_text, str):
        raise ValueError("markdown_text must be a string")

    logging.info(f"Normalizing markdown: input length={len(markdown_text)} characters")
    text = markdown_text.replace("\r\n", "\n").replace("\r", "\n")

    # Split into paragraphs separated by blank lines, normalize each paragraph by
    # replacing internal single newlines with spaces, preserving code fences heuristically.
    import re

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
    logging.info(f"Normalized markdown: output length={len(normalized)} characters")
    return normalized


def convert_unified_diff_to_model(diff_lines: list[str]) -> UnifiedDiff:
    """Convert a unified diff string to a UnifiedDiff model."""
    result: list[UnifiedDiff] = []

    current_diff_lines = []
    current_new_excerpt = ""
    current_old_excerpt = ""
    for line in diff_lines:
        if line.startswith("@@"):
            if current_diff_lines:
                result.append(
                    UnifiedDiff(
                        unified_diff="\n".join(current_diff_lines),
                        old_excerpt=current_old_excerpt,
                        new_excerpt=current_new_excerpt,
                    )
                )
            current_diff_lines = []
            current_new_excerpt = ""
            current_old_excerpt = ""
        if line.startswith("+"):
            current_new_excerpt += line[1:]
        if line.startswith("-"):
            current_old_excerpt += line[1:]
        current_diff_lines.append(line)

    logging.info(f"Converted unified diff into {len(result)} hunks")
    return result


def diff_texts(text_a: str, text_b: str, n_context_lines: int = 3) -> list[UnifiedDiff]:
    """Compute a unified diff between two markdown strings.

    Args:
        text_a: Text parsed from the first PDF.
        text_b: Text parsed from the second PDF.
        n_context_lines: Number of context lines to include in the diff.

    Returns:
        A unified diff string representing the differences between ``text_a`` and ``text_b``.
        Returns an empty string when there are no differences.
    """
    if not isinstance(text_a, str) or not isinstance(text_b, str):
        raise ValueError("Both inputs must be strings")

    lines_a = text_a.splitlines()
    lines_b = text_b.splitlines()

    logging.info(
        f"Computing unified diff: len(A)={len(lines_a)} lines, len(B)={len(lines_b)} lines, context={n_context_lines}"
    )
    diff_lines = list(unified_diff(lines_a, lines_b, lineterm="", n=n_context_lines))
    hunks = convert_unified_diff_to_model(diff_lines[2:])
    logging.info(f"Unified diff produced {len(hunks)} hunks")
    return hunks


def get_markdown_from_pdf(pdf_path: str) -> str:
    """Get the markdown text from a PDF file."""
    logging.info(f"Extracting markdown from PDF: {pdf_path}")
    text = parse_pdf_to_markdown(str(pdf_path))
    cleaned = cleanup_markdown(text)
    logging.info(f"Extracted and cleaned markdown from '{pdf_path}': {len(cleaned)} characters")
    return cleaned
