"""Using the human evaluation dataset to to sample code to test the effectiveness of this approach

Dataset from: https://github.com/openai/human-eval/tree/master
Paper: https://arxiv.org/pdf/2107.03374.pdf
"""

import glob
import json
from pathlib import Path

import tqdm
from typer import Typer

from prompt_to_code.agents.agents import run_agent
from prompt_to_code.config import PromptToCodeConfig

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


def run_human_eval(
    agent="tdd",
    outdir: Path | str = "./examples/human_eval",
    num_samples_per_task=1,
    start_question: int = 0,
    start_ittr: int = 0,
):
    problems = read_problems(HUMAN_EVAL)
    outdir = Path(outdir)
    ittr = tqdm.tqdm(total=len(problems) * num_samples_per_task)
    problem_names = sorted(problems.keys())
    for i, example_id in enumerate(problem_names):
        if i < start_question:
            ittr.update(num_samples_per_task - start_ittr)
            continue
        example = problems[example_id]
        for loop_cnt in range(start_ittr, num_samples_per_task):
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


def score(num_samples_per_task, outdir):
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


app = Typer(name="Prompt-to-code: Human Eval")


@app.command()
def human_eval(
    agent: str = "tdd",
    outdir_root: str = "./examples",
    num_samples_per_task: int = 1,
    just_score: bool = False,
    start_question: int = 0,
    start_ittr: int = 0,
):
    PromptToCodeConfig()
    outdir = Path(outdir_root) / f"./human_eval_{agent}"

    print("Running human eval for agent", agent)
    print(f"saving output to {outdir}")
    print("WARNING THIS WILL COST $$$, please monitor OPENAI bill")
    if not just_score:
        run_human_eval(
            agent=agent,
            outdir=outdir,
            num_samples_per_task=num_samples_per_task,
            start_question=start_question,
            start_ittr=start_ittr,
        )
    score(num_samples_per_task=num_samples_per_task, outdir=outdir)


if __name__ == "__main__":
    app()
