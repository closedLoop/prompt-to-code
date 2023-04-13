from pydantic import BaseModel


class AvailableMethods(BaseModel):
    """Already defined functions within the codebase that can be used to solve the task"""

    name: str
    definition: str
    description: str | None
    parameters: tuple[list[str], list[str]] | None
    return_type: str | None
    filename: str | None
    branch: str | None
    code_hash: str | None = None
    embedding: list[float] | None = None
    usages: dict[str, list[tuple[str, int]]] | None


class TaskDefinition(BaseModel):
    name: str
    description: str | None
    url: str | None
    root_branch: str = "main"
    target_branch: str | None = None
    context: list[str] = []  # A memory of the task
    references: list[
        AvailableMethods
    ] = []  # A list of functions that can be used to solve the task
