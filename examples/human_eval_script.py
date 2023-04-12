"""Using the human evaluation dataset to to sample code to test the effectiveness of this approach

Dataset from: https://github.com/openai/human-eval/tree/master
Paper: https://arxiv.org/pdf/2107.03374.pdf
"""

import glob
import json
import re
import signal
import time
import traceback
from pathlib import Path

import tqdm
from langchain.chat_models import ChatOpenAI

from create_branch import GitBranchCRUD
from prompt_to_code.agents.prompts import (
    ERROR_PROMPT,
    FUNCTION_MENTION,
    FUNCTIONS_SECTION,
    GREEN_STEP_PROMPT,
    RED_STEP_PROMPT,
    STUB_STEP_PROMPT,
)
from prompt_to_code.parsers import extract_function_definitions

# requires human-eval is installed
# Also need to un-comment out the 'eval' function
try:
    from human_eval.data import HUMAN_EVAL, read_problems
    from human_eval.evaluation import evaluate_functional_correctness
except ImportError:
    print("=" * 80)
    print("Install human-eval from: https://github.com/openai/human-eval")
    print("$ git clone https://github.com/openai/human-eval")
    print("$ pip install -e human-eval")
    print("Then uncomment the import statement from /human_eval/execution.py")
    print("```#                         exec(check_program, exec_globals)```")
    print("=" * 80)
    raise ImportError("human-eval required")


def extract_code_from_response(r) -> str:
    if r.startswith("```python"):
        r = r.split("```python")[1].split("```")[0]
    return r


def call_llm(llm, prompt, prefix="any", log_dir="./logs"):
    token_length = llm.get_num_tokens(prompt)
    cur_time = time.time()
    result = llm.call_as_llm(prompt)
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


def run_agent(agent, name, filename, task: str):
    if agent != "tdd":
        raise NotImplementedError(f"Agent {agent} not implemented")

    print(f"Running {agent}: {name}")
    default_llm = {
        "temperature": 0.2,
        "model_name": "gpt-4",
        "max_tokens": 2000,
    }
    llm = ChatOpenAI(**default_llm)

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
    test_results, failed = GitBranchCRUD()._run_command(f"pytest {test_filename}")
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
    function_data, _g = extract_function_definitions(
        stub_code, filename=filename, branch=None
    )
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

    return GitBranchCRUD()._run_command(f"{command} {filename}")


def timeout_handler_wrapper(timeout=5):
    msg = f"Execution took longer than {format} seconds"

    def timeout_handler(signum, frame):
        raise TimeoutError(msg)

    return timeout_handler


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

    new_prompt = ERROR_PROMPT.format(
        functions_section=functions_section,
        filename=filename,
        prompt=prompt,
        examples="",
        error="".join(tb_str),
        code=code,
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


def run_human_eval(
    agent="tdd", outdir: Path | str = "./examples/human_eval", num_samples_per_task=1
):
    problems = read_problems(HUMAN_EVAL)
    outdir = Path(outdir)
    ittr = tqdm.tqdm(total=len(problems) * num_samples_per_task)
    for i, example in enumerate(problems.values()):
        for loop_cnt in range(num_samples_per_task):
            filename = outdir / f"human_eval_{i:04}_{loop_cnt:04}.py"
            name = example["task_id"]
            prompt = example["prompt"]

            run_agent(agent, name, filename, prompt)
            ittr.update(1)


def aggregate_outputs(outdir: Path | str = "./examples/human_eval"):
    pattern = str(Path(outdir) / "human_eval_*.py")
    results = []
    task_ids = set()
    for fname in glob.glob(pattern):
        code = Path(fname).read_text()

        s = fname.split(str(outdir / "human_eval_"))[1].split(".py")[0]
        if "_" in s:
            task_number, *_ = s.split("_")
        else:
            task_number = s
        task_id = f"HumanEval/{int(task_number)}"
        task_ids.add(task_id)
        results.append({"task_id": task_id, "completion": code})
    with open(outdir / "human_eval_samples.jsonl", "w") as f:
        for problem in results:
            f.write(json.dumps(problem) + "\n")

    problems = read_problems(HUMAN_EVAL)
    with open(outdir / "human_eval_problems.jsonl", "w") as f:
        for problem in problems.values():
            if problem["task_id"] in task_ids:
                f.write(json.dumps(problem) + "\n")


def eval_tests(
    outdir="./examples/human_eval",
    k: list[int] | None = None,
    n_workers: int = 4,
    timeout: float = 3.0,
):
    if k is None:
        k = [1]
    outdir = Path(outdir)
    sample_file = outdir / "human_eval_samples.jsonl"
    problem_file = outdir / "human_eval_problems.jsonl"
    return evaluate_functional_correctness(
        str(sample_file), k, n_workers, timeout, str(problem_file)
    )


def run(agent="tdd", num_samples_per_task=200, outdir="./examples/human_eval"):
    outdir = Path(outdir)
    run_human_eval(
        agent="tdd", outdir=outdir, num_samples_per_task=num_samples_per_task
    )
    aggregate_outputs(outdir=outdir)

    # Eval
    k = [1, 2, 3, 4, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    results = eval_tests(
        outdir=outdir,
        k=[i for i in k if i <= num_samples_per_task],
        n_workers=4,
        timeout=3,
    )
    print(results)
    with open(outdir / "human_eval_results.json", "w") as f:
        json.dump(results, f)


if __name__ == "__main__":
    agent = "tdd"
    outdir = f"./examples/human_eval_{agent}"

    print("Running human eval for agent", agent)
    print("saving output to {outdir}")
    print("WARNING THIS WILL COST $$$, please monitor OPENAI bill")
    run(agent=agent, outdir=outdir, num_samples_per_task=1)
