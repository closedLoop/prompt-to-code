import logging
from pathlib import Path

from langchain.agents import Tool

from prompt_to_code.config import PromptToCodeConfig


def _write_to_file_wrapper(config: PromptToCodeConfig, logger: logging.Logger):
    fdir = Path(config.output_directory)
    fdir.mkdir(parents=True, exist_ok=True)

    def file_wrapper(contents: str):
        """Write the contents to the file."""
        filename, *code = contents.splitlines()
        code = "\n".join(code)
        logger.info(f"Writing {filename} to {fdir}")
        logger.info(f"The code is {code}")
        file_path = fdir / filename

        if file_path.exists():  # append to the filename
            code = file_path.read_text() + "\n" + code
            logger.info(f"File {filename} already exists, appending to it")
        file_path.write_text(code)

    return file_wrapper


def write_to_file_tool(config: PromptToCodeConfig, logger: logging.Logger):
    return Tool(
        name="Write code to file",
        func=_write_to_file_wrapper(config, logger=logger),
        description="""writes the input to the filesystem.  The first line of the input should be a unique and descriptive filename, and the rest of the input should be the code to write to the file.  For example:
    ```
    Action Input: hello_world.py

    def hello_world():
        print("Hello World!")

    if __name__ == "__main__":
        hello_world()

    Observation: saved code to hello_world.py
    ```
""",
    )
