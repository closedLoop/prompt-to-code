from pydantic import BaseModel

from taskforce.models.model import TaskForce, WorkerAgent


class UserRequest(BaseModel):
    id: str
    user_id: str
    created_at: str
    payload: str
    channel: str
    target_agent: str


class User(BaseModel):
    id: str
    name: str
    email: str
    permissions: list[str]
    teams: list[str]
    request_log: list[UserRequest]
    stripe_customer_id: str | None


class AgentConfig(BaseModel):
    id: str
    name: str
    config: dict[str, str]


class Cluster(BaseModel):
    id: str
    name: str
    spec: str
    config: dict[str, str]


class Organization(BaseModel):
    id: str
    name: str
    description: str
    logo: str
    url: str
    owner_user: User
    task_forces: list[TaskForce]
    users: list[User]
    configs: list[AgentConfig]
    agents: list[WorkerAgent]
