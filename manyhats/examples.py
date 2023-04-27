import dataclasses
from logging import Logger
from pathlib import Path

from langchain.chat_models import ChatOpenAI
from statemachine import State, StateMachine

from manyhats.dashboard import render_dashboard
from manyhats.graph_helpers import get_graph


@dataclasses.dataclass
class APIStat:
    name: str
    count: float = 0
    time: float = 0
    sent: float = 0
    received: float = 0
    units: str = "kb"
    cost: float = 0


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
    task: str = None
    log: Logger.log = None

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
        self.api_stats = kwargs.pop("api_stats") if "api_stats" in kwargs else []

        if "log" in kwargs:
            self.log = kwargs.pop("log")

        super().__init__(*args, **kwargs)

        self.dag = get_graph(self)

    waiting = PromptState("⏳ Waiting for a task", initial=True)
    understanding = PromptState("🤔 Understanding")
    thinking = PromptState(
        "🧠 Thinking",
    )
    asking = PromptState("🙋 Asking")
    doing = PromptState("🏃 Doing")
    formatting = PromptState("📝 Formatting")
    reflecting = PromptState("🤔 Reflecting")
    completed = PromptState("🏁 Finished", final=True)
    failed = PromptState("❌ Failed", final=True)

    # validators=["validation_1", "validation_2"],
    # cond=["condition_1", "condition_2"],
    # unless=["unless_1", "unless_2"],
    # on=["on_inline_1", "on_inline_2"],
    # before=["before_go_inline_1", "before_go_inline_2"],
    # after=["after_go_inline_1", "after_go_inline_2"],

    go = (
        waiting.to(understanding, cond="has_task")
        | waiting.to(waiting, unless="has_task")
        | understanding.to(thinking)
        | understanding.to(asking)
        | asking.to(understanding)
        | thinking.to(doing)
        | doing.to(formatting)
        | formatting.to(reflecting)
        | reflecting.to(asking)
        | reflecting.to(completed)
        | reflecting.to(failed)
    )

    def has_task(self):
        return self.task is not None

    # Generic State Methods
    def on_enter_state(self):
        if self.log:
            self.log.print(f"{self.current_state.name}:\tEntered state ")

    def on_exit_state(self):
        if self.log:
            self.log.print("\t\texited")

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
        api_stats=[
            APIStat(
                name="OpenAI",
                count=0,
                time=0,
                sent=0,
                received=0,
                units="tokens",
                cost=0,
            ),
            APIStat(
                name="SERPAPI",
                count=0,
                time=0,
                sent=0,
                received=0,
                units="kb",
                cost=0,
            ),
        ],
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
    task = "How many receptions has Antonio Brown had in games with 10 or more targets?"
    render_dashboard(sports_handicaper, task=task)
    # while True:

    # for event in sports_handicaper.task_path():
    # print(event)


def export_graph(agent):
    doc_path = "."
    doc_path = Path(doc_path)
    agent._graph().write_png(doc_path / f"{agent.name.replace(' ','_').lower()}.png")


if __name__ == "__main__":
    run_sports_handicaper()
