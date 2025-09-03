import argparse
import json
import logging

from dotenv import load_dotenv

from compair import llm

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
        result = llm.run_llm_light(args.file1, args.file2)
    elif args.analysis_type == "llm-heavy":
        result = llm.run_llm_heavy(args.file1, args.file2)
    elif args.analysis_type == "llm-only":
        result = llm.run_llm_only(args.file1, args.file2)
    else:
        raise ValueError(f"Invalid analysis type: {args.analysis_type}")

    # Write result to output file
    with open(args.output, "w") as f:
        json.dump(result.model_dump(), f)


if __name__ == "__main__":
    app()
