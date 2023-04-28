import re
import time
from pathlib import Path

from langchain.chat_models import ChatOpenAI
from langchain.llms.openai import OpenAI
from statemachine import State, StateMachine

from create_branch import run_shell_command
from manyhats.agents.base import AgentMachine
from prompt_to_code.agents.models import TaskDefinition
from prompt_to_code.agents.prompts import (
    ERROR_PROMPT,
    FUNCTION_MENTION,
    FUNCTIONS_SECTION,
    GREEN_STEP_PROMPT,
    RED_STEP_PROMPT,
    STUB_STEP_PROMPT,
)
from prompt_to_code.parsers import extract_function_definitions
from prompt_to_code.tools.execution import run_code


class TDDCoderAgent(AgentMachine):
    name = ("TDD Coder",)
    description = (
        """You are a professional sports handicapper and commentator that talks many sports television networks.
You are an expert in the field and have access to any dataset you need to answer any sports and fantasy sports related questions.
You only answer questions related to sports and sports-betting. If you do not know the answer you respond with "I don't know".""",
    )
    goal = ("""Accurately answer questions related to sports and sports-betting.""",)
    task_type = ("question_answering",)
    actions = (
        {
            "data_retrieval": None,
            "calculation": None,
        },
    )  # could also add in memory and context retrieval actions


class BaseAgent:
    header_prompt = ""


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


class AgentMachine(StateMachine):
    "A generic agent that robustly handles tasks"

    create_branch = PromptState(initial=True)
    red = PromptState(
        "Red",
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


"""Using the human evaluation dataset to to sample code to test the effectiveness of this approach

Dataset from: https://github.com/openai/human-eval/tree/master
Paper: https://arxiv.org/pdf/2107.03374.pdf
"""


def extract_code_from_response(code) -> str:
    code = re.sub(r"```[a-zA-Z]+[a-zA-Z0-9\-]*", "", code)
    if code.startswith("```"):
        code = code[3:]
    if code.endswith("```"):
        code = code[:-3]
    return code.strip()


def call_llm(llm, prompt, prefix="any", log_dir="./logs"):
    token_length = llm.get_num_tokens(prompt)
    cur_time = time.time()
    if hasattr(llm, "call_as_llm"):
        result = llm.call_as_llm(prompt)
    else:
        result = llm(prompt)
    duration = time.time() - cur_time

    fname = Path(log_dir) / f"{prefix}-{round(cur_time*1000)}.log"
    if not fname.parent.exists():
        fname.parent.mkdir(parents=True, exist_ok=True)
    with open(fname, "w") as f:
        f.write(prompt)
        f.write("\n\n" + "=" * 80 + "\n\n")
        f.write(result)
    cost = token_length * 0.06 / 1000
    print(f"\tLLM {token_length} tokens, {duration:1f} seconds, ${cost:04f} - {fname}")
    return result


def run_agent(agent, name, filename, task: str, request_timeout=180):
    default_llm = {
        "temperature": 0.2,
        "max_tokens": 2000,
        "request_timeout": request_timeout,
    }
    Model = OpenAI
    if agent == "tdd3":
        Model = ChatOpenAI
        default_llm["model_name"] = "gpt-3.5-turbo"
    elif agent in ["tdd", "tdd-chat", "tdd4"]:
        Model = ChatOpenAI
        default_llm["model_name"] = "gpt-4"
    elif agent.startswith("tdd-"):
        default_llm["model_name"] = "-".join(agent.split("-")[1:])
    else:
        raise NotImplementedError(f"Agent {agent} not implemented")

    llm = Model(**default_llm)
    print(f"Running {agent}: {name} {llm}")

    # Run the steps
    _stub_code, functions_section = stub_step(filename, task, llm, name=name)
    test_code, test_results = red_step(
        filename, task, llm, functions_section, name=name
    )
    test_results, failed = green_step(
        filename, task, llm, functions_section, test_code, test_results, name=name
    )
    # TODO: REFACTOR STEP
    print(test_results, failed)


def green_step(
    filename, task, llm, functions_section, test_code, test_results, name="tdd"
):
    print("GREEN STEP")
    prompt = GREEN_STEP_PROMPT.format(
        functions_section=functions_section,
        filename=filename,
        prompt=task,
        examples="",
        tests=test_code,
        test_errors=test_results,
    )
    prompt = re.sub(r"\n\n\n([\n]+)", "\n\n\n", prompt)

    # generate code
    code = extract_code_from_response(
        call_llm(llm, prompt, prefix="human-eval-green", log_dir=f"./logs/{name}")
    )
    # Run the code to see if it compiles
    code = run_and_fix(
        llm,
        code,
        max_tries=2,
        timeout=5,
        name=name,
        functions_section=functions_section,
        filename=filename,
        prompt=task,
    )

    # Save file
    if not filename.parent.exists():
        filename.parent.mkdir(exist_ok=True, parents=True)

    with open(filename, "w") as f:
        f.write(code)

    # Run the tests again
    test_filename = filename.parent / f"tests/test_{filename.name}"
    test_results, failed = run_shell_command(f"pytest {test_filename}")
    return test_results, failed


def red_step(filename, task, llm, functions_section: str, name="tdd"):
    print("RED STEP")
    prompt = RED_STEP_PROMPT.format(
        test_library="pytest",
        functions_section=functions_section,
        filename=filename,
        prompt=task,
        examples="",
    )
    prompt = re.sub(r"\n\n\n([\n]+)", "\n\n\n", prompt)

    # generate code
    test_code = extract_code_from_response(
        call_llm(llm, prompt, prefix="human-eval-red", log_dir=f"./logs/{name}")
    )
    # Run the code to see if it compiles
    test_code = run_and_fix(
        llm,
        test_code,
        max_tries=2,
        timeout=5,
        name=name,
        functions_section=functions_section,
        filename=filename,
        prompt=task,
    )

    # Save file
    test_filename = filename.parent / f"tests/test_{filename.name}"
    test_results, failed = save_and_run_code(test_filename, test_code, "pytest")

    if failed:
        print(f"Created a failing test at: {test_filename}")
    else:
        print(f"Created a passing test at: {test_filename}")
    return test_code, test_results


def stub_step(filename, task, llm, name="tdd", functions_section="") -> tuple[str, str]:
    print("STUB STEP")
    prompt = STUB_STEP_PROMPT.format(
        functions_section=functions_section, filename=filename, prompt=task, examples=""
    )
    prompt = re.sub(r"\n\n\n([\n]+)", "\n\n\n", prompt)
    # generate code
    stub_code = extract_code_from_response(
        call_llm(llm, prompt, prefix="human-eval-stub", log_dir=f"./logs/{name}")
    )
    # Run the code to see if it compiles
    stub_code = run_and_fix(
        llm,
        stub_code,
        max_tries=2,
        timeout=5,
        name=name,
        functions_section=functions_section,
        filename=filename,
        prompt=task,
    )

    result, failed = save_and_run_code(filename, stub_code, "python")

    functions_section = create_function_list_for_prompts(filename, stub_code)

    # TODO add usages to the function definitions
    if failed:
        print(f"Failed to run the code: {result}")
    return stub_code, functions_section


def create_function_list_for_prompts(filename, stub_code) -> str:
    try:
        function_data, _g = extract_function_definitions(
            stub_code, filename=filename, branch=None
        )
    except Exception as e:
        print(f"Failed to extract function definitions: {e}")
        function_data = []

    functions = [FUNCTIONS_SECTION]
    # TODO add common usages to docstring
    # TODO dynamic language
    for f in function_data:
        fn = FUNCTION_MENTION.format(
            filename=f.filename,
            name=f.name,
            language="python",
            definition=f.definition,
            docstring="\n    ...",
        )
        functions.append(fn + "\n")

    return "\n".join(functions) + "\n" if len(functions) > 1 else ""


def save_and_run_code(filename: Path, code, command) -> tuple[str, bool]:
    """Saves code to filename, runs command and returns stdout and a bool if it had failed"""
    # Save file
    if not filename.parent.exists():
        filename.parent.mkdir(exist_ok=True, parents=True)

    with open(filename, "w") as f:
        f.write(code)

    return run_shell_command(f"{command} {filename}")


def run_and_fix(
    llm,
    code,
    max_tries=2,
    timeout=5,
    count=0,
    name="tdd",
    functions_section: str = "",
    filename: str = "",
    prompt: str = "",
):
    if count >= max_tries:
        return code

    # Set the signal handler for the alarm signal
    tb_str = run_code(code, timeout)

    if tb_str is None:
        return code

    new_prompt = ERROR_PROMPT.format(
        functions_section=functions_section,
        filename=filename,
        prompt=prompt,
        examples="",
        error="".join(tb_str),
        code=code,
        language="python3",
    )

    code = extract_code_from_response(
        call_llm(
            llm, new_prompt, prefix=f"human-eval-fix-{count}", log_dir=f"./logs/{name}"
        )
    )
    return run_and_fix(
        llm,
        code,
        max_tries=max_tries,
        timeout=timeout,
        count=count + 1,
        name=name,
        functions_section=functions_section,
        filename=filename,
        prompt=prompt,
    )
