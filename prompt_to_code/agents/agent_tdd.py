from langchain.chat_models import ChatOpenAI
from pydantic import BaseModel
from statemachine import State, StateMachine


class AvailableMethods(BaseModel):
    """Already defined functions within the codebase that can be used to solve the task"""

    name: str
    definition: str
    description: str | None
    parameters: tuple[list[str], list[str]] | None
    return_type: str | None
    file_name: str | None
    branch: str | None
    code_hash: str | None = None
    embedding: list[float] | None = None
    usages: dict[str, dict[str, list[tuple[str, int]]]] | None


class TaskDefinition(BaseModel):
    name: str
    description: str | None
    url: str | None
    root_branch: str = "main"
    target_branch: str | None = None
    context: list[str] = []  # A memory of the task
    references: list[
        AvailableMethods
    ] = []  # A list of functions that can be used to solve the task


ERROR_PROMPT = """Running the code raises the following error, please only the corrected code.  Include any descriptions in comments.

ERROR:
{error}

BROKEN CODE:
{code}

CORRECTED CODE:
"""


FUNCTIONS_SECTION = """FUNCTIONS: You can use any of the following functions to help you:
{functions}
"""

STUB_STEP_PROMPT = """
You are a developer who strictly follows test-driven development best practices and uses the Red-Green-Refactor loop.

Given the following prompt, write a "stub" file that just defines the function names, their arguments and specifies the return types to be later implemented.  Do not implement the function themselves.

{functions_section}

FILENAME: {filename}

PROMPT:
{prompt}

{examples}

STUB FILE:
""".lstrip()

RED_STEP_PROMPT = """
You are a developer who strictly follows test-driven development best practices and uses the Red-Green-Refactor loop.

Given the following code prompt implement a failing test using `{test_library}`.  The CODE section below should include only the test code and not the function implementation.

{functions_section}

FILENAME: {filename}

PROMPT:
{prompt}

{examples}

TESTS (excluding function implementations):
""".lstrip()

GREEN_STEP_PROMPT = """
You are a developer who strictly follows test-driven development best practices and uses the Red-Green-Refactor loop.

Given the following code prompt and failing test, implement the functions to pass the tests.  The CODE section below should NOT include the test code.

{functions_section}

FILENAME: {filename}

PROMPT:
{prompt}

{examples}

TESTS:
{tests}

FAILED TESTS MESSAGE:
{test_errors}

CODE (excluding tests):
""".lstrip()


def on_enter_red(self):
    print("Write a failing test.")


def on_exit_red(self):
    print("Failing test written.")


def on_enter_green(self):
    print("Write code to pass the test.")


def on_exit_green(self):
    print("All tests pass")


def on_enter_refactor(self):
    print("Refactor code and tests.")


def on_exit_refactor(self):
    print("All tests pass after refactoring.")


class PromptState(State):
    """Manages LLM Prompts before and after states"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        default_llm = {
            "temperature": 0.7,
            "model": "gpt-4",
            "max_tokens": 3000,
        }
        default_llm |= kwargs.get("llm", {})
        self.llm = ChatOpenAI(**default_llm)


def create_branch(self, branch_name: str = ""):
    # Check if in a git repo
    # Check if branch name is valid and provided
    # Check if branch name already exists
    # Check if uncommitted changes exist
    # check if branch name is provided
    # Check if branch exists
    # Check out branch
    print(f"Creating branch {branch_name}")


class TDDMachine(StateMachine):
    "A Red-Green-Refactor Statemachine"

    create_branch = PromptState(initial=True)
    red = PromptState(
        "Red",
        enter="on_enter_red",
    )
    green = PromptState()
    refactor = PromptState()
    commit = PromptState()
    make_pull_request = PromptState(final=True)
    tdd = (
        create_branch.to(red)
        | red.to(green)
        | green.to(refactor)
        | refactor.to(commit)
        | commit.to(red)
        | commit.to(make_pull_request)
    )

    task: TaskDefinition

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task = TaskDefinition(**kwargs.get("task", {}))

    def before_tdd(self, event: str, source: State, target: State, message: str = ""):
        message = f". {message}" if message else ""
        return f"Running {event} from {source.id} to {target.id}{message}"


if __name__ == "__main__":
    sm = TDDMachine()
    print(sm.tdd())
    print(sm.tdd())
    print(sm.tdd())
    print(sm.tdd())
