# https://github.com/GammaTauAI/leetcode-hard-gym


import tempfile
from pathlib import Path

from leetcode_hard_gym.main import run_all
from typer import Typer

from examples.human_eval_script import run_agent
from prompt_to_code.config import PromptToCodeConfig

app = Typer(name="Prompt-to-code: LeetCode Hard Gym")


def agent_wrapper(agent="tdd"):
    def agent_runner(prompt, **kwargs):
        filename = Path(tempfile.mkstemp(prefix="leetcode_gym_", suffix=".py")[1])
        try:
            name = kwargs.get("question_id", "unknown")
            run_agent(agent, name, filename, prompt)
            return Path(filename).read_text()
        except Exception as e:
            print("Error: ", e)
            return prompt

    return agent_runner


@app.command()
def leetcode_eval(
    agent: str = "tdd", output_file="leetcode-results.jsonl", lang="python3"
):
    PromptToCodeConfig()
    run_all(agent_wrapper(agent=agent), output_file=output_file, lang=lang)


if __name__ == "__main__":
    app()
