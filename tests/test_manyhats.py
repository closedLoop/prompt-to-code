import dataclasses
import unittest
import uuid
from typing import Any

import httpx
import statemachine
from prefect import flow, task
from statemachine import StateMachine

from manyhats.agents.base import API
from manyhats.agents.trivia import Trivia
from manyhats.dashboard import configure_logging_for_agent


class TestManyHats(unittest.TestCase):
    def test_trivia_agent(self):
        # This should be a test that runs a trivia agent
        # This agent tries to answer questions by searching the web
        # and optionally asking for help from a human for clarification
        # and conduct reasoning or calculations to answer the question
        # This agent should be able to answer questions like:
        # "What is the capital of France?"

        self.assertTrue(True)


@dataclasses.dataclass
class ManyHatsWorkflow:
    name: str
    sm: StateMachine | None = None


@dataclasses.dataclass
class ManyHatsTool:
    name: str


@dataclasses.dataclass
class ManyHatsRole:
    uuid: str
    name: str
    workflow: ManyHatsWorkflow
    tools: list[ManyHatsTool | API]
    kwargs: dict[str, Any] | None


@dataclasses.dataclass
class ManyHatsAgent:
    uuid: str
    hat: ManyHatsRole
    execution_environment: Any
    environment_variables: dict[str, str]


@dataclasses.dataclass
class ManyHatsTask:
    uuid: str
    action_item: str
    agent: ManyHatsAgent
    parent_task: str | None


@task(retries=3)
def get_stars(repo: str):
    url = f"https://api.github.com/repos/{repo}"
    count = httpx.get(url).json()["stargazers_count"]
    print(f"{repo} has {count} stars!")


@task(retries=1)
def run_task(task: ManyHatsTask):
    agent = task.agent.hat.workflow.sm

    configure_logging_for_agent(agent)

    agent.log.print(f"Starting Task: {task}")
    agent.task = task
    while True:
        if agent.current_state.final:
            agent.log.info(f"Result: {agent.result}")
            return agent
        try:
            agent.go()
        except statemachine.exceptions.TransitionNotAllowed:
            agent.log.print(f"Transition not allowed: {agent.current_state.name}")
            raise Exception(f"Transition not allowed: {agent.current_state.name}")


@flow(name="ManyHats")
def run_tasks(action_item: str, hat: str = "trivia", dashboard: bool = False):
    t = Trivia()

    hat = ManyHatsRole(
        uuid=str(uuid.uuid4()),
        name="trivia",
        workflow=ManyHatsWorkflow(name="trivia", sm=Trivia()),
        tools=t.default_actions or [],
        kwargs={},
    )
    agent = ManyHatsAgent(
        uuid=str(uuid.uuid4()),
        hat=hat,
        execution_environment=None,
        environment_variables={},
    )
    root_task = ManyHatsTask(
        uuid=str(uuid.uuid4()),
        action_item=action_item,
        agent=agent,
        parent_task=None,
    )

    run_task(root_task)


if __name__ == "__main__":
    # unittest.main()
    # output = render_dashboard(
    #     Trivia(), task="With which game is Santosh Trophy associated?"
    # )

    # output = render_dashboard(
    #     LMGTFY(), task= "What is the square root of the age of the President of France?"
    # )
    action_item = (
        "Answer: What is the square root of the age of the President of France?"
    )

    # run the flow!
    run_tasks(action_item)

    # output = run_no_dashboard(
    #     LMGTFY(), task=action_item
    # )
    # print(output)
