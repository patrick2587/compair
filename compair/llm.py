import base64
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from compair.models import (
    Change,
    ChangeClassification,
    DifferenceReport,
    DifferenceReportWithInputs,
)
from compair.preprocessing import diff_texts, get_markdown_from_pdf

MODEL = "gpt-4.1"
PROMPT_DIR = Path(__file__).parent.parent / "compair" / "prompts"


load_dotenv()  # load OPENAI_API_KEY


# client = OpenAI(
#    api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
#    base_url=os.getenv("AZURE_OPENAI_ENDPOINT", "") + "/openai/v1/",
#    default_query={"api-version": "preview"},
# )


def run_llm_light(
    pdf_path_a: str | Path,
    pdf_path_b: str | Path,
) -> DifferenceReportWithInputs:
    def _classify_diff(diff_lines: str) -> ChangeClassification:
        messages = [
            {
                "role": "system",
                "content": (PROMPT_DIR / "systen_prompt_llm_light.md").read_text(encoding="utf-8"),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "Classify the diff lines provided as unified diff and return ONLY a JSON object conforming to the "
                            "ChangeClassification schema."
                        ),
                    },
                    {"type": "text", "text": f"Unified diff:\n{diff_lines}"},
                ],
            },
        ]

        # client = OpenAI()
        client = OpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
            base_url=os.getenv("AZURE_OPENAI_ENDPOINT", "") + "/openai/v1/",
            default_query={"api-version": "preview"},
        )
        logging.info("Classifying unified diff hunk with llm-light")
        completion = client.beta.chat.completions.parse(
            model=MODEL,
            temperature=0,
            messages=messages,
            response_format=ChangeClassification,
        )
        return completion.choices[0].message.parsed

    logging.info("Running llm-light pipeline")
    document_a_markdown = get_markdown_from_pdf(pdf_path_a)
    document_b_markdown = get_markdown_from_pdf(pdf_path_b)
    changes_as_unified_diff = diff_texts(document_a_markdown, document_b_markdown)

    changes = []
    for i, diff in enumerate(changes_as_unified_diff):
        change_classification = _classify_diff(diff.unified_diff)
        changes.append(
            Change(
                change_id=str(i),
                old_excerpt=diff.old_excerpt,
                new_excerpt=diff.new_excerpt,
                change_classification=change_classification,
            )
        )

    diff_report = DifferenceReport(
        changes=changes,
        summary=None,
    )

    result = DifferenceReportWithInputs(
        document_a=document_a_markdown,
        document_b=document_b_markdown,
        difference_report=diff_report,
    )
    logging.info("llm-light pipeline finished")
    return result


def run_llm_heavy(
    pdf_path_a: str | Path,
    pdf_path_b: str | Path,
) -> DifferenceReportWithInputs:
    """Use Chat Completions structured parsing to return a DifferenceReport.

    The model is instructed via a system message; both documents are provided as text parts in
    the user message. The SDK parses the response directly into the Pydantic model.
    """

    logging.info("Running llm-heavy pipeline")
    document_a_markdown = get_markdown_from_pdf(pdf_path_a)
    document_b_markdown = get_markdown_from_pdf(pdf_path_b)

    messages = [
        {
            "role": "system",
            "content": (PROMPT_DIR / "systen_prompt_llm_heavy.md").read_text(encoding="utf-8"),
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Compare the two documents and return ONLY a JSON object conforming to the "
                        "DifferenceReport schema."
                    ),
                },
                {"type": "text", "text": f"Document A:\n{document_a_markdown}"},
                {"type": "text", "text": f"Document B:\n{document_b_markdown}"},
            ],
        },
    ]

    client = OpenAI()
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        temperature=0,
        messages=messages,
        response_format=DifferenceReport,
    )

    msg = completion.choices[0].message
    diff_report: DifferenceReport = msg.parsed
    result = DifferenceReportWithInputs(
        document_a=document_a_markdown,
        document_b=document_b_markdown,
        difference_report=diff_report,
    )
    logging.info("llm-heavy pipeline finished")
    return result


def run_llm_only(
    pdf_path_a: str | Path,
    pdf_path_b: str | Path,
) -> DifferenceReportWithInputs:
    """Use Chat Completions structured parsing with two PDF uploads.

    Attaches both PDFs as file parts (data URLs) in a single user message. The response is parsed
    directly into a DifferenceReport instance.
    """

    def _pdf_to_data_url(path: str | Path) -> str:
        file_path = Path(path)
        encoded = base64.b64encode(file_path.read_bytes()).decode("utf-8")
        return f"data:application/pdf;base64,{encoded}"

    messages = [
        {
            "role": "system",
            "content": (PROMPT_DIR / "systen_prompt_llm_only.md").read_text(encoding="utf-8"),
        },
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": (
                        "Compare the two attached PDFs and return ONLY a JSON object conforming "
                        "to the DifferenceReport schema."
                    ),
                },
                {
                    "type": "file",
                    "file": {
                        "file_data": _pdf_to_data_url(pdf_path_a),
                        "filename": Path(pdf_path_a).name,
                    },
                },
                {
                    "type": "file",
                    "file": {
                        "file_data": _pdf_to_data_url(pdf_path_b),
                        "filename": Path(pdf_path_b).name,
                    },
                },
            ],
        },
    ]

    logging.info("Running llm-only pipeline")
    client = OpenAI()
    completion = client.beta.chat.completions.parse(
        model=MODEL,
        temperature=0,
        messages=messages,
        response_format=DifferenceReportWithInputs,
    )

    msg = completion.choices[0].message
    diff_report: DifferenceReportWithInputs = msg.parsed
    logging.info("llm-only pipeline finished")
    return diff_report
