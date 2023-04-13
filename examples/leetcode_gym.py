# https://github.com/GammaTauAI/leetcode-hard-gym


import tempfile

from leetcode_hard_gym.main import run_all

from examples.human_eval_script import run_agent
from prompt_to_code.config import PromptToCodeConfig


def agent_wrapper(prompt, **kwargs):
    filename = tempfile.mkstemp(prefix="leetcode_gym_", suffix=".py")[1]

    try:
        name = kwargs.get("question_id", "unknown")
        run_agent("tdd", name, filename, prompt)

        with open(filename) as f:
            code = f.read()
        return code
    except Exception as e:
        print("Error: ", e)
        return prompt


def run():
    run_all(agent_wrapper, output_file="leetcode-results.jsonl", lang="python3")


if __name__ == "__main__":
    PromptToCodeConfig()
    run()
