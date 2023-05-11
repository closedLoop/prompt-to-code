"""

CLI Commands

Taskforce start
 - launches docker-compose
 - loads .env and other config if exists
 - nginx - for reverse proxy
 - starts prefect server
 - launches postgres
 - redis - for state mgmt
 - runs prefect agents
 - local docker-registry
 - remix dashboard
   - iframe various dashboards inside it - prefect, redis, prisma

taskforce service prefect # a wrapper for "prefect cli"

taskforce login: create a user, organization
 - sets local variables {user, org}
taskforce create: define a taskforce
 - sets local variables {taskforce_id}

taskforce launch:
  - creates / finds a {work_pool, work_queue and build a deployment which registers the flow} for the taskforce
  - Start an agent to pick up flow runs from the work queue
run: Submit a flow run to the work_queue
  - prefect run --name taskforce_name --parameters x=42
Scale: increase the number of agents
  - docker-compose scale agent=5
Monitor: monitor the flow runs
 - From Prefect UI
 - From CLI / dashboard - for costs
 - From TaskForce UI - for costs and flow run status
Stop / Pause / Resume: stop/ pause/resume the agents
Teardown: stops + delete the deployment, work_queue, work_pool
Delete: teardown + remove the taskforce
"""
import subprocess


def start_taskforce():
    """Starts the taskforce docker-compose stack"""
    subprocess.run(["docker-compose", "up", "-d"], check=True)


if __name__ == "__main__":
    start_taskforce()
