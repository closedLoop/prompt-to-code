from datetime import datetime

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table

from manyhats.agent import AgentMachine


def make_layout(agent_names: list[str], num_apis=2) -> Layout:
    """Define the layout."""
    layout = Layout(name="root")

    layout.split(
        Layout(name="header", size=6 + max(0, num_apis - 3)),
        Layout(name="main", ratio=1),
        Layout(name="footer", size=7),
    )
    layout["header"].split_row(
        Layout(name="task", ratio=1),
        Layout(name="costs", minimum_size=30),
    )
    layout["main"].split_row(
        Layout(name="agents"),
        Layout(name="state", ratio=1, minimum_size=60),
    )
    layout["agents"].split(*[Layout(name=f"agent:{name}") for name in agent_names])
    return layout


class Header:
    """Display header with clock."""

    def __init__(self, **kwargs):
        super().__init__()
        self.agent = kwargs.pop("agent") if "agent" in kwargs else None
        self.task = kwargs.pop("task") if "task" in kwargs else None
        self.starttime = kwargs.pop("starttime") if "starttime" in kwargs else None

    def __rich__(self) -> Panel:
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        # grid.add_column(justify="right")

        if self.starttime:
            seconds = round((datetime.now() - self.starttime).total_seconds(), 1)
            dt = f" ({seconds}s)"
        else:
            dt = ""
        if self.agent:
            if self.agent.task_type == "question_answering":
                task_type = "[b]Q/A[/b]"
            else:
                task_type = f"[b]{self.agent.task_type}[/b]"
            agent_str = f"{task_type}{dt}:\t"
            agent_str += f"{self.task}" if self.task else f"{self.agent.name or ''}"
        else:
            agent_str = ""

        grid.add_row(
            agent_str,
            # dt
        )
        return Panel(grid, title="[b]ManyHats[/b] Task Runner")


class APIStats:
    """Display header with clock."""

    def __init__(self, **kwargs):
        super().__init__()
        self.agent = kwargs.pop("agent") if "agent" in kwargs else None

    def __rich__(self) -> Panel:
        table = Table(expand=True, box=box.SIMPLE)

        table.add_column("API Name", style="cyan", no_wrap=True)
        table.add_column("Count")
        table.add_column("Time")
        table.add_column("Sent")
        table.add_column("Received")
        table.add_column("Cost($)", justify="right", style="magenta")

        for stat in self.agent.api_stats:
            table.add_row(
                stat.name,
                str(stat.count),
                f"{stat.time:,.1f}s",
                (f"{stat.sent} {stat.units or ''}").strip(),
                (f"{stat.received} {stat.units or ''}").strip(),
                f"${stat.cost:,.4f}",
            )
        return table


def render_dashboard(agent: AgentMachine, task: str):
    Console()
    starttime = datetime.now()
    layout = make_layout([agent.name])
    layout["task"].update(Header(agent=agent, task=task, starttime=starttime))
    layout["costs"].update(APIStats(agent=agent))
    # layout["box2"].update(Panel(make_syntax(), border_style="green"))
    layout["state"].update(Panel(layout.tree, title="Variables", border_style="grey50"))
    # layout["footer"].update(progress_table)

    from time import sleep

    from rich.live import Live

    with Live(layout, refresh_per_second=10, screen=True):
        while True:
            sleep(0.2)
            # update agent.api_stats randomly
            for stat in agent.api_stats:
                stat.count += 1
                stat.time += 0.1
                stat.sent += 1
                stat.received += 1
                stat.cost += 0.0001

            # for job in job_progress.tasks:
            #     if not job.finished:
            #         job_progress.advance(job.id)

            # completed = sum(task.completed for task in job_progress.tasks)
            # overall_progress.update(overall_task, completed=completed)
