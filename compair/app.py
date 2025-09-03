import argparse
import logging
import json
from pathlib import Path

from dotenv import load_dotenv

from compair import pipelines

load_dotenv()


def app():
    # Create the parser
    parser = argparse.ArgumentParser(description="CLI tool for AI-based legal document comparison.")

    # Add arguments
    parser.add_argument("file1", type=str, help="Path to the first file to compare")
    parser.add_argument("file2", type=str, help="Path to the second file to compare")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="comparison-result.json",
        help="Path to the output json file",
    )
    parser.add_argument(
        "-a",
        "--analysis-type",
        type=str,
        default="llm-light",
        help="Type of analysis to perform",
        choices=["llm-light", "llm-heavy", "llm-only"],
    )

    # Parse arguments
    args = parser.parse_args()

    # Print greeting
    logging.info(f"Processing {args.file1} and {args.file2} with {args.analysis_type} analysis type!")

    if args.analysis_type == "llm-light":
        report = pipelines.run_llm_light(args.file1, args.file2)
    elif args.analysis_type == "llm-heavy":
        report = pipelines.run_llm_heavy(args.file1, args.file2)
    elif args.analysis_type == "llm-only":
        report = pipelines.run_llm_only(args.file1, args.file2)
    else:
        raise ValueError(f"Invalid analysis type: {args.analysis_type}")

    # Write result to output file
    Path(args.output).write_text(
        json.dumps(report.model_dump(), indent=2, ensure_ascii=False), encoding="utf-8"
    )


if __name__ == "__main__":
    app()
