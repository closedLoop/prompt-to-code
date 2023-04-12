"""Using the human evaluation dataset to to sample code to test the effectiveness of this approach

Dataset from: https://github.com/openai/human-eval/tree/master
Paper: https://arxiv.org/pdf/2107.03374.pdf
"""

import json
import re
import signal
import traceback
from pathlib import Path

from langchain.chat_models import ChatOpenAI

from create_branch import GitBranchCRUD
from prompt_to_code.agents.agent_tdd import (
    ERROR_PROMPT,
    FUNCTIONS_SECTION,
    GREEN_STEP_PROMPT,
    RED_STEP_PROMPT,
    STUB_STEP_PROMPT,
)
from prompt_to_code.parsers import extract_function_definitions


def load_human_eval_dataset():
    """Load the human evaluation dataset"""
    # Load the dataset
    with open("examples/human-eval-v2-20210705.jsonl") as f:
        dataset = [json.loads(l) for l in f.readlines()]
    return dataset


def extract_code_from_response(r) -> str:
    if r.startswith("```python"):
        r = r.split("```python")[1].split("```")[0]
    return r


def run_example(name, filename, task):
    print(f"Running: {name}")
    default_llm = {
        "temperature": 0.7,
        "model_name": "gpt-4",
        "max_tokens": 256,
    }
    llm = ChatOpenAI(**default_llm)

    # RUN STUB
    prompt = STUB_STEP_PROMPT.format(
        functions_section="", filename=filename, prompt=task, examples=""
    )
    prompt = re.sub(r"\n\n\n([\n]+)", "\n\n\n", prompt)
    # generate code
    stub_code = extract_code_from_response(llm.call_as_llm(prompt))
    # Run the code to see if it compiles
    stub_code = run_and_fix(llm, stub_code, max_tries=2, timeout=5)

    result, failed = save_and_run_code(filename, stub_code, "python")
    if failed:
        print(f"Failed to run the code: {result}")
        return
    print(result)

    function_data, _g = extract_function_definitions(stub_code)

    # RUN RED
    functions = "\n".join([f"{f.definition}\n" for f in function_data])
    # TODO add usages to the function definitions

    prompt = RED_STEP_PROMPT.format(
        test_library="pytest",
        functions_section=FUNCTIONS_SECTION.format(functions=functions),
        filename=filename,
        prompt=task,
        examples="",
    )
    prompt = re.sub(r"\n\n\n([\n]+)", "\n\n\n", prompt)

    # generate code
    test_code = extract_code_from_response(llm.call_as_llm(prompt))
    # Run the code to see if it compiles
    test_code = run_and_fix(llm, test_code, max_tries=2, timeout=5)

    # Save file
    test_filename = filename.parent / f"tests/test_{filename.name}"
    test_results, failed = save_and_run_code(test_filename, test_code, "pytest")

    if failed:
        print(f"Created a failing test at: {test_filename}")
    else:
        print(f"Created a passing test at: {test_filename}")

    # RUN GREEN
    prompt = GREEN_STEP_PROMPT.format(
        functions_section=FUNCTIONS_SECTION.format(functions=functions),
        filename=filename,
        prompt=task,
        examples="",
        tests=test_code,
        test_errors=test_results,
    )
    prompt = re.sub(r"\n\n\n([\n]+)", "\n\n\n", prompt)

    # generate code
    code = extract_code_from_response(llm.call_as_llm(prompt))
    # Run the code to see if it compiles
    code = run_and_fix(llm, code, max_tries=2, timeout=5)

    # Save file
    if not filename.parent.exists():
        filename.parent.mkdir(exist_ok=True, parents=True)

    with open(filename, "w") as f:
        f.write(code)

    # Run the tests again
    test_filename = filename.parent / f"tests/test_{filename.name}"
    test_results, failed = GitBranchCRUD()._run_command(f"pytest {test_filename}")
    print(test_results, failed)


def save_and_run_code(filename: Path, code, command) -> tuple[str, bool]:
    """Saves code to filename, runs command and returns stdout and a bool if it had failed"""
    # Save file
    if not filename.parent.exists():
        filename.parent.mkdir(exist_ok=True, parents=True)

    with open(filename, "w") as f:
        f.write(code)

    return GitBranchCRUD()._run_command(f"{command} {filename}")


def timeout_handler_wrapper(timeout=5):
    msg = f"Execution took longer than {format} seconds"

    def timeout_handler(signum, frame):
        raise TimeoutError(msg)

    return timeout_handler


def run_and_fix(llm, code, max_tries=3, timeout=5, count=0):
    if count >= max_tries:
        return code

    # Set the signal handler for the alarm signal
    signal.signal(signal.SIGALRM, timeout_handler_wrapper(timeout=timeout))
    tb_str = None
    try:
        # Set an alarm for 10 seconds
        signal.alarm(timeout)
        exec(code)
    except TimeoutError as te:
        error = f"TimeoutError: Execution took longer than {timeout} seconds"
        tb_str = traceback.format_exception(type(te), value=error, tb=te.__traceback__)
    except Exception as e:
        tb_str = traceback.format_exception(type(e), value=e, tb=e.__traceback__)
    finally:
        # Cancel the alarm if it didn't go off
        signal.alarm(0)
        # Remove the signal handler and set it to the default behavior
        signal.signal(signal.SIGALRM, signal.SIG_DFL)

    if tb_str is None:
        return code

    new_prompt = ERROR_PROMPT.format(error="".join(tb_str), code=code)
    code = llm.call_as_llm(new_prompt)
    code = extract_code_from_response(code)
    return run_and_fix(llm, code, max_tries=max_tries, timeout=timeout, count=count + 1)


if __name__ == "__main__":
    dataset = load_human_eval_dataset()

    for i in range(4):
        example = dataset[i]

        filename = Path(f"examples/human_eval/human_eval_{i:04}.py")
        name = example["task_id"]
        prompt = example["prompt"]

        run_example(name, filename, prompt)
