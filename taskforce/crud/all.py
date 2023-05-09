from prisma.models import Role, Tool, Workflow

from prisma import Client


class CRUDTool:
    def __init__(self, client: Client):
        self.client = client

    async def create_tool(self, name: str) -> Tool:
        async with self.client:
            return await self.client.tool.create({"name": name})

    async def get_tool(self, id: str) -> Tool | None:
        async with self.client:
            return await self.client.tool.find_unique({"id": id})

    async def get_all_tools(self) -> list[Tool]:
        async with self.client:
            return await self.client.tool.find_many()

    async def update_tool(self, id: str, name: str) -> Tool | None:
        async with self.client:
            return await self.client.tool.update(
                {"where": {"id": id}, "data": {"name": name}}
            )

    async def delete_tool(self, id: str) -> Tool | None:
        async with self.client:
            return await self.client.tool.delete({"id": id})


# Workflow, Role, WorkerAgent, Task, Cluster, Worksite, Permission, User, Team, Organization
# Workflow, Role, WorkerAgent, Task, Cluster, Worksite, Permission, User, Team, Organization
# WorkerAgent, Task, Cluster, Worksite, Permission, User, Team, Organization


class CRUDWorkflow:
    def __init__(self, client: Client):
        self.client = client

    async def create_workflow(
        self, name: str, machines: dict, tool_ids: list[str]
    ) -> Workflow:
        async with self.client:
            return await self.client.workflow.create(
                {
                    "name": name,
                    "machines": machines,
                    "tools": {"connect": [{"id": id} for id in tool_ids]},
                }
            )

    async def get_workflow(self, id: str) -> Workflow | None:
        async with self.client:
            return await self.client.workflow.find_unique({"id": id})

    async def get_all_workflows(self) -> list[Workflow]:
        async with self.client:
            return await self.client.workflow.find_many()

    async def update_workflow(
        self, id: str, name: str, machines: dict, tool_ids: list[str]
    ) -> Workflow | None:
        async with self.client:
            return await self.client.workflow.update(
                {
                    "where": {"id": id},
                    "data": {
                        "name": name,
                        "machines": machines,
                        "tools": {"connect": [{"id": id} for id in tool_ids]},
                    },
                }
            )

    async def delete_workflow(self, id: str) -> Workflow | None:
        async with self.client:
            return await self.client.workflow.delete({"id": id})


# Repeat the same CRUD class structure for the other models (Role, WorkerAgent, Task, Cluster, Worksite, Permission, User, Team, Organization)


# For example, CRUD class for the Role model:
class CRUDRole:
    def __init__(self, client: Client):
        self.client = client

    async def create_role(
        self,
        name: str,
        description: str,
        goal: str,
        task_type: str,
        workflow_ids: list[str],
        tool_ids: list[str],
        config: dict,
    ) -> Role:
        async with self.client:
            return await self.client.role.create(
                {
                    "name": name,
                    "description": description,
                    "goal": goal,
                    "task_type": task_type,
                    "workflows": {"connect": [{"id": id} for id in workflow_ids]},
                    "tools": {"connect": [{"id": id} for id in tool_ids]},
                    "config": config,
                }
            )

    async def get_role(self, id: str) -> Role | None:
        async with self.client:
            return await self.client.role.find_unique({"id": id})

    async def get_all_roles(self) -> list[Role]:
        async with self.client:
            return await self.client.role.find_many()

    async def update_role(
        self,
        id: str,
        name: str,
        description: str,
        goal: str,
        task_type: str,
        workflow_ids: list[str],
        tool_ids: list[str],
        config: dict,
    ) -> Role | None:
        async with self.client:
            return await self.client.role.update(
                {
                    "where": {"id": id},
                    "data": {
                        "name": name,
                        "description": description,
                        "goal": goal,
                        "task_type": task_type,
                        "workflows": {"connect": [{"id": id} for id in workflow_ids]},
                        "tools": {"connect": [{"id": id} for id in tool_ids]},
                        "config": config,
                    },
                }
            )

    async def delete_role(self, id: str) -> Role | None:
        async with self.client:
            return await self.client.role.delete({"id": id})


# ... Implement similar CRUD classes for the remaining models (WorkerAgent, Task, Cluster, Worksite, Permission, User, Team, Organization)
