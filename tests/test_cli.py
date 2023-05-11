"""Tests the CRUD actions in the CLI for taskforce"""
import asyncio
import functools
import os
import uuid
from unittest import IsolatedAsyncioTestCase

import dotenv
import prefect
from prefect.cli.work_pool import (
    ObjectAlreadyExists,
    ObjectNotFound,
    WorkPoolCreate,
    get_available_work_pool_types,
    get_client,
    get_default_base_job_template_for_type,
)
from prefect.deployments import Deployment

from prisma import Prisma
from taskforce.agent import lead_agent_workflow


async def create_work_pool(
    name: str,
    type: str,
    paused: bool = False,
):
    base_job_template = await get_default_base_job_template_for_type(type)
    if base_job_template is None:
        raise ValueError(
            f"Unknown work pool type {type!r}. "
            f"Please choose from {', '.join(await get_available_work_pool_types())}."
        )
    async with get_client() as client:
        try:
            wp = WorkPoolCreate(
                name=name,
                type=type,
                base_job_template=base_job_template,
                is_paused=paused,
            )
            work_pool = await client.create_work_pool(work_pool=wp)
        except ObjectAlreadyExists:
            raise ValueError(
                f"Work pool {name} already exists. Please choose a different name."
            )
    return work_pool


async def create_work_queue(
    name: str,
    pool: str,
    limit: int | None = None,
):
    async with get_client() as client:
        try:
            result = await client.create_work_queue(
                name=name,
                work_pool_name=pool,
            )
            if limit is not None:
                await client.update_work_queue(
                    id=result.id,
                    concurrency_limit=limit,
                )
        except ObjectAlreadyExists:
            raise ValueError(f"Work queue with name: {name!r} already exists.")
        except ObjectNotFound:
            raise ValueError(f"Work pool with name: {pool!r} not found.")
    return result


@functools.lru_cache
def client():
    return Prisma(auto_register=False, use_dotenv=True)


class TestCLICrud(IsolatedAsyncioTestCase):
    @classmethod
    async def asyncSetUpClass(_cls):
        dotenv.load_dotenv()

    async def asyncSetUp(self):
        self.client = client()
        await self.client.connect()

    async def asyncTearDown(self):
        await self.client.disconnect()

    def test_org_user_crud(self):
        """Tests the CRUD actions in the CLI for taskforce
        should create a user, create an org, invite the user to the org, and delete the org and user
        """
        # CliRunner(org_app).invoke(
        #     [
        #         "create",
        #         "test_org",
        #     ]
        # )

    async def test_mvp(self):
        """
        HELLO WORLD EXAMPLE - Q/A Bot
        create a user + org
        create a taskforce project
        create a taskforce agents (Q/A bot, Searcher, etc)
        launch the taskforce
        submit questions via the CLI
        view tasks via dashboard
        """

        # START SERVER
        # prefect server start
        # prefect config set PREFECT_API_URL=http://127.0.0.1:4200/api
        # name: _str
        # email: _str
        # permissions: List[_str]
        # request_log: Optional[List['models.UserRequest']]
        # stripe_customer_id: Optional[_str]
        # Organizations: Optional[List['models.Organization']]
        # TaskForce: Optional['models.TaskForce']
        # OrgOwners: Optional[List['models.Organization']]
        # taskForceId: _str

        test_id = str(uuid.uuid4())[:8]

        username = f"test-{os.getlogin().lower().strip()}-{test_id}"

        user = await self.client.user.create(data={"name": username})
        await self.client.organization.create(
            data={
                "name": f"test-org-{test_id}",
                "owner_user": {
                    "connect": {"id": user.id},
                },
            }
        )
        organizations = await self.client.organization.find_many(
            where={"owner_userId": user.id}, include={"owner_user": True}
        )
        assert len(organizations) == 1

        task_force = await self.client.taskforce.create(
            data={
                "name": f"test-taskforce-{test_id}",
                "description": "A minimal example of a taskforce project",
                "purpose": "Question Answering System",
                "organization": {
                    "connect": {"id": organizations[0].id},
                },
                "users": {"connect": {"id": user.id}},
                "tools": "{}",
                "comms": "{}",
            }
        )
        task_forces = await self.client.taskforce.find_many(
            where={"id": task_force.id},
            include={"organization": True, "users": True},
        )
        assert len(task_forces) == 1
        print(task_forces)

        # Create a taskforce agent
        #         name: _str

        agent = await self.client.workeragent.create(
            data={
                "name": "Q/A Bot",
                "logo": ":rocket:",
                "bio": "Born to answer questions",
                "organization": {
                    "connect": {"id": organizations[0].id},
                },
                "taskforce": {
                    "connect": {"id": task_forces[0].id},
                },
                # "leadagent": [],
                "config": "{}",
                "role": {
                    "create": {
                        "name": "Q/A Bot",
                        "task_type": "examples",
                        "goal": "Answer questions",
                        "description": "A simple question answering bot",
                    }
                },
            }
        )

        await self.client.taskforce.update(
            where={"id": task_forces[0].id},
            data={
                "leadagent": {"connect": {"id": agent.id}},
            },
        )
        agents = await self.client.workeragent.find_many(
            where={"id": agent.id},
            include={"organization": True, "taskforce": True, "role": True},
        )
        assert len(agents) == 1
        #                         # "workflows": []
        #                           name        String
        #   description String
        #   goal        String
        #   task_type   String
        #   workflows   Workflow[]
        #   tools       Tool[]
        #   WorkerAgent WorkerAgent[]
        #     }
        # )

        print("------------------AGENT------------------")
        print(agents[0])
        # role: Optional["models.Role"]
        # role_id: _int
        # config: "fields.Json"
        # organization: Optional["models.Organization"]
        # TaskForce: Optional[List["models.TaskForce"]]
        # LeadAgent: Optional[List["models.TaskForce"]]
        # organizationId: _int

        print("------------------LAUNCH------------------")
        # Creates a prefect job queue and creates a prefect flow with the lead agent subscribed to that queue
        # Could launch to prefect cloud (id: 8f0722f9-d451-43f7-9bc7-c75445fe46e0)
        # https://app.prefect.cloud/account/04d724ef-ed29-47bc-b40e-1de8255b5279/workspace/8f0722f9-d451-43f7-9bc7-c75445fe46e0/flows

        # or local agent

        # A workpool in prefect is mapped to the taskforce
        # $ prefect work-pool create --type prefect-agent test-taskforce-00000000
        await create_work_pool(name=task_force.name, type="prefect-agent", paused=False)
        # $ prefect work-queue create --pool test-taskforce-00000000 lead-agent
        await create_work_queue(name="lead-agent", pool=task_force.name, limit=None)

        # Created work queue with properties:
        #     name - 'lead-agent'
        #     work pool - 'test-taskforce-00000000'
        #     id - e7d5492c-a7b1-4e96-a9a1-0259e72f61b9
        #     concurrency limit - None
        # Start an agent to pick up flow runs from the work queue:
        #     prefect agent start -q 'lead-agent -p test-taskforce-00000000'

        # Inspect the work queue:
        #     prefect work-queue inspect 'lead-agent'

        # (venv) sean@lucy:~/repos/closedloop/prompt-to-code$ prefect agent start -q 'lead-agent -p test-taskforce-00000000'
        # Starting v2.10.6 agent with ephemeral API...

        #   ___ ___ ___ ___ ___ ___ _____     _   ___ ___ _  _ _____
        #  | _ \ _ \ __| __| __/ __|_   _|   /_\ / __| __| \| |_   _|
        #  |  _/   / _|| _|| _| (__  | |    / _ \ (_ | _|| .` | | |
        #  |_| |_|_\___|_| |___\___| |_|   /_/ \_\___|___|_|\_| |_|

        # Agent started! Looking for work from queue(s): lead-agent -p test-taskforce-00000000...
        # 22:48:32.356 | INFO    | prefect.agent - Created work queue 'lead-agent -p test-taskforce-00000000'.

        # print("------------------QUESTION------------------")
        # Submit a question to job queue

        # prefect deployment build \
        #     --name taskforce_name \
        #     --description purpose_and_description \
        #     --work-queue lead-agent \
        #     --pool test-taskforce-00000000 \
        #     --infra process \
        #     --apply \
        #     ./taskforce/agent.py:lead_agent_workflow
        # prefect agent start -p 'test-taskforce-00000000'
        # prefect agent start -q 'lead-agent -p test-taskforce-00000000'
        # os.environ["PREFECT_API_URL"] = "http://127.0.0.1:4200/api"
        deployment = await Deployment.build_from_flow(
            flow=lead_agent_workflow,
            name=task_force.name,
            description=f"{task_force.purpose or ''}: {task_force.description or ''}".strip()
            .strip(":")
            .strip(),
            work_queue_name="lead-agent",
            work_pool_name=task_force.name,
            apply=True,
        )
        await deployment.apply()

        import prefect.server.schemas as schemas

        # Create flow run
        async with prefect.get_client() as client:
            deployments = await client.read_deployments(
                deployment_filter=schemas.filters.DeploymentFilter(
                    name={"any_": [task_force.name]}
                )
            )

        assert len(deployments) == 1 and deployments[0].name == task_force.name
        deployment = deployments[0]
        flow_run = await create_flow_run(deployment.id, 42)
        print(flow_run)

        # Do I create workers here?
        # prefect worker start --pool YOUR_WORK_POOL_NAME

        # Can this be used to submit a flow run?
        # from prefect.agent import PrefectAgent, FlowRun

        # agent = PrefectAgent(work_queues=["lead-agent"], work_pool_name=task_force.name)
        # print(agent)
        # agent.start()
        # FlowRun(work_queue_name = "lead-agent")
        # agent.submit_run()
        # agent.submit_run(self, flow_run: FlowRun) ->

        # Launch agents
        print("run")
        print(f"prefect agent start --pool {task_force.name} --work-queue lead-agent")


async def create_flow_run(deployment_id, x):
    pass

    # with temporary_settings(updates={PREFECT_API_URL: os.environ["PREFECT_API_URL"]}):
    async with prefect.get_client() as client:
        return await client.create_flow_run_from_deployment(
            deployment_id, parameters={"x": x}
        )


async def main():
    t = TestCLICrud()
    await t.asyncSetUpClass()
    await t.asyncSetUp()
    await t.test_mvp()


if __name__ == "__main__":
    asyncio.run(main())
    # unittest.main()
