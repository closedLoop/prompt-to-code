from prefect import flow, task


@task()
def plus_one(x):
    print(x + 1)


@flow
def lead_agent_workflow(
    taskforce_id: str,
    action_item: str,
    agent_id: str | None = None,
    parent_task: str | None = None,
):
    plus_one(x=1)


if __name__ == "__main__":
    lead_agent_workflow.run(
        taskforce_id="1", action_item="2", agent_id="3", parent_task="4"
    )
