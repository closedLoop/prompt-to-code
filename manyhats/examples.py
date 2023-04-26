from pathlib import Path

from langchain.chat_models import ChatOpenAI
from statemachine import State, StateMachine


class BaseAgent:
    header_prompt = ""


# def on_enter_red(self):

# def on_exit_red(self):


# def on_enter_green(self):


# def on_exit_green(self):


# def on_enter_refactor(self):


# def on_exit_refactor(self):


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

    understanding = PromptState("🤔 Understanding", initial=True)
    thinking = PromptState(
        "🧠 Thinking",
    )
    asking = PromptState("🙋 Asking")
    doing = PromptState("🏃 Doing")
    formatting = PromptState("📝 Formatting")
    reflecting = PromptState("🤔 Reflecting")
    completed = PromptState("🏁 Finished")

    task_path = (
        understanding.to(thinking)
        | understanding.to(asking)
        | asking.to(understanding)
        | thinking.to(doing)
        | doing.to(formatting)
        | formatting.to(reflecting)
        | reflecting.to(asking)
        | reflecting.to(completed)
    )

    # Understanding Step
    # if off_topic, return "Off Topic"
    # if clarifing questions, ask clarifying questions and await response if --no-clarifying-questions guess best answer and continue

    # Problem decomposition, step types 'data retrieval', 'calculation'
    # Steps, if data retrieval

    # Execution Loop
    # For right now tasks as executed linearly, but could be executed in parallel based on a DAG of steps
    # For each step execute the step -> takes in the input and returns the output

    # Output formatting step

    # Completion step
    # did you successfully answer the question?
    # if no, is there anything you were uncertain about or assumptions you made?
    #        ask clarifying questions and await response if --no-clarifying-questions and repeat from start

    def __init__(self, *args, **kwargs):
        if "name" in kwargs:
            self.name = kwargs.pop("name")
        if "description" in kwargs:
            self.description = kwargs.pop("description")
        if "goal" in kwargs:
            self.goal = kwargs.pop("goal")
        if "task_type" in kwargs:
            self.task_type = kwargs.pop("task_type")
        if "actions" in kwargs:
            self.actions = kwargs.pop("actions")

        super().__init__(*args, **kwargs)
        print(kwargs)
        print(args)

    # def before_tdd(self, event: str, source: State, target: State, message: str = ""):


def run_sports_handicaper():
    """This uses the CLI to communicate with humans"""
    researcher = AgentMachine(
        name="Researcher",
        description="""You are a researcher that works for a sports betting company.""",
    )
    calculator = AgentMachine(
        name="Calculator", description="""You do simple math calculations."""
    )
    print(researcher, calculator)

    sports_handicaper = AgentMachine(
        name="Sports Handicapper",
        description="""You are a professional sports handicapper and commentator that talks many sports television networks.
You are an expert in the field and have access to any dataset you need to answer any sports and fantasy sports related questions.
You only answer questions related to sports and sports-betting. If you do not know the answer you respond with "I don't know".""",
        goal="""Accurately answer questions related to sports and sports-betting.""",
        task_type="question_answering",
        actions={
            "data_retrieval": None,
            "calculation": None,
        },  # could also add in memory and context retrieval actions
    )

    # Understanding Step
    # if off_topic, return "Off Topic"
    # if clarifing questions, ask clarifying questions and await response if --no-clarifying-questions guess best answer and continue

    # Problem decomposition, step types 'data retrieval', 'calculation'
    # Steps, if data retrieval

    # Execution Loop
    # For right now tasks as executed linearly, but could be executed in parallel based on a DAG of steps
    # For each step execute the step -> takes in the input and returns the output

    # Output formatting step

    # Completion step
    # did you successfully answer the question?
    # if no, is there anything you were uncertain about or assumptions you made?
    #        ask clarifying questions and await response if --no-clarifying-questions and repeat from start

    print(sports_handicaper.task_path())

    doc_path = "."
    doc_path = Path(doc_path)

    sports_handicaper._graph().write_png(doc_path / "readme_agent_tdd.png")


if __name__ == "__main__":
    run_sports_handicaper()
