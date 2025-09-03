"""compAIr CLI tool."""

__all__ = ["__version__"]

__version__ = "0.1.0"

# Configure root logging similar to pytest CLI logging
import logging
import sys

if not logging.getLogger().handlers:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stdout,
    )
