from dataclasses import dataclass
from typing import Any

from statemachine import StateMachine

from manyhats.agent import AgentMachine


@dataclass
class Tool:
    id: str
    name: str


@dataclass
class Workflow:
    id: str
    name: str
    machines: dict[str, AgentMachine | StateMachine]
    tools: list[Tool]


@dataclass
class Role:
    id: str
    name: str
    description: str
    goal: str
    task_type: str
    workflows: list[Workflow]
    tools: list[Tool]
    config: dict[str, Any]


@dataclass
class WorkerAgent:
    id: str
    role: Role
    execution_environment: str
    environment_variables: dict[str, str]


@dataclass
class Task:
    id: str
    action_item: str
    agent: WorkerAgent
    parent_task: str | None


@dataclass
class Cluster:
    id: str
    name: str
    spec: str
    config: dict[str, Any]


@dataclass
class Worksite:
    id: str
    name: str
    infrastructure: list[Cluster]
    worker_agents: list[WorkerAgent]
    global_config: dict[str, Any]
    central_logs: list[str]
    results_logs: list[str]
    api_endpoint: str
    chat_endpoint: str
    chat_agent: WorkerAgent | None
    task_sources: dict[str, str]


@dataclass
class Permission:
    id: str
    name: str
    description: str


@dataclass
class User:
    id: str
    name: str
    email: str
    permissions: list[Permission]
    teams: list["Team"]
    request_log: list[str]


@dataclass
class Team:
    id: str
    name: str
    description: str
    logo: str
    url: str
    members: list[User]
    stripe_customer_id: str
    owner_user: User
    config: dict[str, str]
    custom_agents: list[WorkerAgent]
    worksites: list[Worksite]
    clusters: list[str]


@dataclass
class Organization:
    id: str
    name: str
    description: str
    logo: str
    url: str
    teams: list[Team]
    users: list[User]
    owner_user: User
    stripe_customer_id: str | None
    config: dict[str, str]
    custom_agents: list[WorkerAgent]
