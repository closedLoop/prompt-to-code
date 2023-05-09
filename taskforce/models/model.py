from dataclasses import dataclass
from datetime import datetime
from typing import Any

from pydantic import BaseModel
from statemachine import StateMachine

from manyhats.agent import AgentMachine
from taskforce.models.auth_model import Cluster, User


class Tool(BaseModel):
    id: str
    name: str
    description: str
    params: dict[str, Any]


class Task(BaseModel):
    id: str
    action_item: str
    created_at: datetime = datetime.now()
    agent_id: str
    parent_task: str | None


@dataclass
class AgentDecision:
    source: str
    target: str
    candidates: list[str]
    state: str  # serialization of the state machine


class AgentAction:
    """Action Taken between state transisitons"""

    prev_step: str
    new_step: str
    state: str
    action: str
    action_params: dict[str, Any]
    candidates: list[str]

    output: Any

    # Each action updates these
    side_effects: list[str] = []
    costs: dict[str, Any] = {}
    wall_time: float
    cpu_time: float
    memory: float
    logs: list[str]


class AgentWork(BaseModel):
    """Describes the work that an agent is doing"""

    id: str
    started_at: datetime = datetime.now()
    completed_at: datetime | None = None

    task: Task
    result: Any = None

    # Monitoring
    decisions: list[AgentDecision] = []
    actions: list[AgentAction] = []


class Workflow(BaseModel):
    id: str
    name: str
    machines: dict[str, AgentMachine | StateMachine]
    tools: list[Tool]
    output_formats: list[
        str
    ]  # A description of the types from final nodes of the StateMachines


class Role(BaseModel):
    id: str
    name: str
    description: str
    goal: str
    task_type: str
    workflows: list[Workflow]
    tools: list[Tool]


class WorkerAgent(BaseModel):
    id: str
    logo: str
    name: str
    bio: str
    role: Role
    config: dict[str, Any]


class TaskForce(BaseModel):
    id: str
    name: str
    purpose: str
    description: str  # Descibe any intermediate milestones how performance will be measured
    created_at: datetime = datetime.now()
    updated_at: datetime = datetime.now()
    uuid: str = None

    worker_agents: list[WorkerAgent] = []  # Agents
    lead_agent: WorkerAgent | None = (
        None  # Agent in charge of subscribing to the comms and interacting with users
    )
    users: list[
        User
    ] = []  # Humans who can communicate with worker agents and lead agents
    final_authority: str = None  # id of Final authority for approval can be human or AI

    tools: list[any] = None  # Resources defined as list of ToolSpec
    comms: dict[str, any] = {}  # Communication channels


class TaskForceResults(BaseModel):
    # Monitoring
    costs: dict[str, Any] = {}  # Costs for the task
    metrics: dict[str, Any] = {}  # Metrics for the task
    actions: list[Any] = []  # Actions taken by the taskforce
    tool_usage: dict[str, Any] = {}  # Usage of tools by the taskforce
    full_logs: list[any] = []  # Logs for the task

    # Results
    main: list[
        Any
    ] = []  # Each main task paired with the end result (task, output, side_effects)
    tasks: list[Any] = []  # Task-level results (action_item, output, side_effects)

    # Evaluation
    intra_task_decisions: list[
        Any
    ] = (
        []
    )  # Intra-task decisions (for an agent, within a workflow such as choosing a tool)
    inter_task_decisions: list[Any] = []  # Choosing an agent selection decisions
    feedback: list[Any] = []  # User feedback on the tasks and the decisions


class TaskForceLaunch(BaseModel):
    id: str = None  # UUID for the task
    created_at: datetime = datetime.now()  # Created at
    started_at: datetime = datetime.now()  # Created at
    status: str = "stopped"  # Status of the task

    # Constraints
    deadline: datetime = None  # Deadline for completion
    budget: float = None  # Budget for completion

    # Config
    config: dict[str, Any]  # Applies to each agent unless overridden by an AgentConfig
    environment: Cluster = None  # Environment for the task to run

    results: TaskForceResults = None  # Results of the task

    # Agents
    api_endpoint: str
    chat_endpoint: str
