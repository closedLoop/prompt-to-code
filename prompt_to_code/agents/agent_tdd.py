from langchain.chat_models import ChatOpenAI
from statemachine import State, StateMachine

from prompt_to_code.agents.models import TaskDefinition


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
            "request_timeout": 180,
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
