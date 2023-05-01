import dataclasses
import json
import sys
import time
from collections.abc import Callable
from logging import Logger

import networkx as nx
import pandas as pd
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI
from statemachine import State, StateMachine

from manyhats.graph_helpers import get_graph


@dataclasses.dataclass
class APIStat:
    name: str = ""
    count: float = 0
    time: float = 0
    sent: float = 0
    received: float = 0
    units: str = "kb"
    cost: float = 0


@dataclasses.dataclass
class InternalState:
    on_task: bool = False
    task_as_understood: str = ""
    questions: list[str] | None = None
    statements: list[str] | None = None
    entities: list[str] | None = None
    steps: list[str] | None = None
    intermediate_results: dict[str, any] | None = None
    result: any = None


class API:
    name: str = "API"
    description: str = "Generic API request"
    stats: APIStat
    model: Callable

    def __init__(self, name: str, model: Callable, cost_units: str = "kb"):
        self.name = name
        self.stats = APIStat(name=name, units=cost_units)
        self.model = model

    def __call__(self, prompt: str) -> str:
        """Updates stats and returns the result of the model"""
        if hasattr(self.model, "get_num_tokens"):
            request_size = self.model.get_num_tokens(prompt)
        else:
            request_size = sys.getsizeof(json.dumps(prompt)) / 1024

        # Call API
        with time.time() as cur_time:
            result = self.call(prompt)
            duration = time.time() - cur_time

        if hasattr(self.model, "get_num_tokens"):
            response_size = self.model.get_num_tokens(result)
        else:
            response_size = sys.getsizeof(json.dumps(result)) / 1024

        cost = self.cost(request_size, response_size)

        self.stats.count += 1
        self.stats.time += duration
        self.stats.sent += request_size
        self.stats.received += response_size
        self.stats.cost += cost

        return result

    def call(self, prompt: str) -> str:
        return (
            self.model.call_as_llm(prompt)
            if hasattr(self.model, "call_as_llm")
            else self.model(prompt)
        )

    def cost(self, request_size, response_size):
        return request_size * 0 + response_size * 0.06 / 1000


class TaskState(State):
    _api_actions: list[API] | None = None

    def __init__(self, *args, **kwargs):
        if "api_actions" in kwargs:
            self._api_actions = kwargs.pop("api_actions")

        super().__init__(*args, **kwargs)

        default_llm = {
            "temperature": 0.7,
            "model": "gpt-4",
            "max_tokens": 3000,
            "request_timeout": 180,
        }
        default_llm |= kwargs.get("llm", {})
        self.llm = ChatOpenAI(**default_llm)

    @property
    def api_actions(self) -> list[API]:
        return self._api_actions or []


class AgentMachine(StateMachine):
    "A generic agent that robustly handles tasks"

    # Parameters
    task: str | None = None
    description: str | None = None
    disable_questions: bool = False
    default_actions: list[API] = [
        API(
            "OpenAI",
            OpenAI(temperature=0.0, model_name="text-davinci-003", request_timeout=60),
            cost_units="tokens",
        )
    ]
    failure_reason: str | None = None
    result: any = None

    # Status and State
    internal_state: InternalState = InternalState()
    log: Logger.log = None
    dag: nx.DiGraph = None

    @property
    def api_stats(self) -> list[APIStat]:
        df = pd.DataFrame(self._all_stats())
        if len(df) == 0:
            return []
        df = df.groupby(["name", "units"]).sum().reset_index()
        return [APIStat(**dict(r[1])) for r in df.iterrows()]

    def _all_stats(self) -> list[APIStat]:
        stats = {
            id(a.stats): a.stats
            for s in self.states
            if hasattr(s, "api_actions")
            for a in (s.api_actions or []) + (self.default_actions or [])
        } | {id(a.stats): a.stats for a in (self.default_actions or [])}
        return list(stats.values())

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
        if "disable_questions" in kwargs:
            self.disable_questions = kwargs.pop("disable_questions", False)

        if "log" in kwargs:
            self.log = kwargs.pop("log")

        super().__init__(*args, **kwargs)

        self.dag = get_graph(self)

    waiting = TaskState("⏳ Waiting for a task", initial=True)
    understanding = TaskState(
        "🤔 Understanding",
    )
    thinking = TaskState(
        "🧠 Thinking",
    )
    asking = TaskState("🙋 Asking")
    doing = TaskState("🏃 Doing")
    formatting = TaskState("📝 Formatting")
    reflecting = TaskState("🤔 Reflecting")
    completed = TaskState("🏁 Finished", final=True)
    failed = TaskState("❌ Failed", final=True)

    # Transitions
    go = (
        waiting.to(understanding, cond="has_task")
        | waiting.to(waiting, unless="has_task")
        | understanding.to(thinking, cond="valid_and_clear_task")
        | understanding.to(asking, unless="valid_and_clear_task")
        | asking.to(thinking)
        | thinking.to(doing)
        | doing.to(formatting)
        | formatting.to(reflecting)
        | reflecting.to(completed, cond="task_completed")
        | reflecting.to(failed, unless="task_completed")
        # | reflecting.to(asking)
    )

    # Conditions
    def has_task(self):
        return self.task is not None

    def valid_task(self):
        return self.internal_state.on_task

    def no_questions(self):
        return (
            self.disable_questions
            or (self.internal_state.questions is None)
            or len(self.internal_state.questions) == 0
        )

    def task_completed(self):
        return self.internal_state.task_completed

    def valid_and_clear_task(self):
        return self.no_questions() and self.valid_task()

    # Generic State Methods
    def on_enter_state(self):
        pass

    def on_exit_state(self):
        pass

    def on_enter_understanding(self):
        prompt = """{description}
If you do not know the answer you respond with "I don't know".

Given the following question answer the following questions:
 a. Is this question related to your area of expertise? (Yes or No)
 b. List of all the entities mentioned in the question:
 c. Re-write the question for clarity:
 d. Only if the question is vague or ambiguous, provide a list of clarifying questions:

Question: {question}

Response:"""
        actions = self.current_state.api_actions or []
        if len(actions) == 0:
            actions = self.default_actions or []
        response = actions[0](
            prompt.format(description=self.description, question=self.task)
        )

        data = response.split("\n")
        at_end = False
        for row in data:
            if row.strip().startswith("a."):
                self.internal_state.on_task = "yes" in row[2:].strip().lower()
            elif row.strip().startswith("b."):
                self.internal_state.entities = [
                    e.strip() for e in row[2:].strip().split(",") if e.strip()
                ]
            elif row.strip().startswith("c."):
                self.internal_state.task_as_understood = row[2:].strip()
            elif row.strip().startswith("d."):
                q = row[2:].strip()
                self.internal_state.questions = [] if q.startswith("N/A") else [q]
                at_end = True
            elif at_end:
                self.internal_state.questions.append(row[2:].strip())
            else:
                self.log.print(f"Ignoring response: {row}")

    def on_enter_asking(self):
        questions = [q for q in self.internal_state.questions if q.strip()]

        if not questions:
            self.internal_state.statements = []
            self.internal_state.questions = []
            return

        prompt = """{description}

In the context of this question (do not answer this question): {question}

Only answer each of the following clarifing-questions with the most likely response:
{questions}

Answers (in a markdown-formatted list):
"""
        actions = self.current_state.api_actions or []
        if len(actions) == 0:
            actions = self.default_actions or []

        response = actions[0](
            prompt.format(
                description=self.description,
                question=self.task,
                questions="\n".join(questions),
            )
        )

        data = response.split("\n")
        self.internal_state.statements = data
        self.internal_state.questions = []

    def on_enter_thinking(self):
        prompt = """{description}
Given the following question, decompose it into a markdown-formatted list of the steps required to answer the question.

Relevant Entities:
{entities}

Assuming:
{statements}

Question: {question}

Each step should be of a type:  [retrieval, calculation]
Steps (in a markdown-formatted list):
"""
        actions = self.current_state.api_actions or []
        if len(actions) == 0:
            actions = self.default_actions or []

        response = actions[0](
            prompt.format(
                description=self.description,
                question=self.task,
                statements="\n".join(
                    [q for q in self.internal_state.statements if q.strip()]
                ),
                entities="\n".join(
                    [e for e in self.internal_state.entities or [] if e.strip()]
                ),
            )
        )
        data = response.split("\n")
        self.internal_state.steps = data

    def on_enter_doing(self):
        self.log.print("Doing steps")
        if self.internal_state.intermediate_results is None:
            self.internal_state.intermediate_results = {}
        for i, step in enumerate(self.internal_state.steps or []):
            self.log.print(f"{i} - {step}")
            # TODO store the results of each step
            self.internal_state.intermediate_results[i] = ""

    def on_enter_formatting(self):
        # Combine the outputs of the functions to generate the result
        prompt = """{description}

Given the following question, our assumptions and all of the intermediate steps and results, only return the answer to the question:
{question}

Assuming:
{statements}

Steps:
{steps}

Question:
{question}

Answer:
"""
        actions = self.current_state.api_actions or []
        if len(actions) == 0:
            actions = self.default_actions or []

        steps = []
        for i, step in enumerate(self.internal_state.steps or []):
            steps.append(f"{i}. {step}".strip())
            result = self.internal_state.intermediate_results[i].strip()
            steps.append(f"\t-> {result}")

        response = actions[0](
            prompt.format(
                description=self.description,
                question=self.task,
                statements="\n".join(
                    [q for q in self.internal_state.statements if q.strip()]
                ),
                steps="\n".join(steps),
            )
        )
        self.internal_state.result = response
        self.log.print(f"Doing Formatting of answer: {self.internal_state.result}")

    def on_enter_reflecting(self):
        self.log.print(f"Reflecting on answer: {self.internal_state.result}")

        prompt = """{description}

Given the following question, is the answer likely accurate? (YES or NO)
If not, say why not and what we need to do to improve the answer.

Question:
{question}

Answer:
{answer}

Result:
"""
        self.log.print(f"Reflecting on answer: {self.internal_state.result}")
        actions = self.current_state.api_actions or []
        if len(actions) == 0:
            actions = self.default_actions or []

        response = actions[0](
            prompt.format(
                description=self.description,
                question=self.task,
                answer=self.internal_state.result,
            )
        )
        self.log.print(f"Reflecting on answer: {self.internal_state.result}")
        self.internal_state.task_completed = response.strip().lower().startswith("yes")
        if self.internal_state.task_completed:
            self.internal_state.failure_reason = None
        else:
            self.internal_state.failure_reason = response.strip()

    def on_enter_finished(self):
        self.log.print(f"Answer: {self.internal_state.result}")
        return self.internal_state.result

    def on_enter_failed(self):
        self.log.print(
            f"Could not complete task because: {self.internal_state.failure_reason}"
        )
        return self.internal_state.result
