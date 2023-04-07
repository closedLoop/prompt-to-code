import logging
from pathlib import Path

from langchain.agents import Tool

from prompt_to_code.config import PromptToCodeConfig


def _read_file_wrapper(config: PromptToCodeConfig, logger: logging.Logger):
    fdir = Path(config.output_directory)

    def file_wrapper(contents: str):
        """Write the contents to the file."""
        filename, *_code = contents.splitlines()
        filename = fdir / filename.strip()

        if not filename.exists():
            return f"ERROR: {filename} does not exist"
        return filename.read_text()

    return file_wrapper


def read_file_tool(config: PromptToCodeConfig, logger: logging.Logger):
    return Tool(
        name="Read file",
        func=_read_file_wrapper(config, logger=logger),
        description="""returns the text content read from the specified filename.  The input is a filename that exists""",
    )
