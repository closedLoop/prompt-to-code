import logging
from pathlib import Path

from langchain.agents import Tool

from prompt_to_code.config import PromptToCodeConfig

# implementation of tee from https://stackoverflow.com/a/59109706/2988073
# prefix components:
space = "    "
branch = "│   "
# pointers:
tee = "├── "
last = "└── "


def tree(dir_path: Path, prefix: str = ""):
    """A recursive generator, given a directory Path object
    will yield a visual tree structure line by line
    with each line prefixed by the same characters
    """
    contents = list(dir_path.iterdir())
    # contents each get pointers that are ├── with a final └── :
    pointers = [tee] * (len(contents) - 1) + [last]
    for pointer, path in zip(pointers, contents):
        yield prefix + pointer + path.name
        if path.is_dir():  # extend the prefix and recurse:
            extension = branch if pointer == tee else space
            # i.e. space because last, └── , above so no more |
            yield from tree(path, prefix=prefix + extension)


def _list_files_wrapper(config: PromptToCodeConfig, logger: logging.Logger):
    fdir = Path(config.output_directory)

    def file_wrapper(contents: str):
        """Write the contents to the file."""
        root_dir = fdir / contents.strip()
        return (
            f"Folder tree with root: {root_dir}\n" + "\n".join(list(tree(root_dir)))
            if root_dir.exists()
            else f"ERROR: {root_dir} does not exist"
        )

    return file_wrapper


def list_file_tool(config: PromptToCodeConfig, logger: logging.Logger):
    return Tool(
        name="List files",
        func=_list_files_wrapper(config, logger=logger),
        description="""returns a list of each file  text content read from the specified filename.  The input is a filename that exists""",
    )
