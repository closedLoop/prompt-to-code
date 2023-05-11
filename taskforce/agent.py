from prefect import flow, task


@task()
def plus_one(x):
    print(x + 1)


@flow
def lead_agent_workflow(x=1):
    plus_one(x=x)
