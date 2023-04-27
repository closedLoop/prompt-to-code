import os
import random
from datetime import datetime
from time import sleep

from rich import box
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.pretty import Pretty
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text
from statemachine import StateMachine

from manyhats.agent import AgentMachine
from manyhats.graph_helpers import ordered_nodes_by_distance


def make_layout(max_states: int = 2, num_apis=2) -> Layout:
    """Define the layout."""
    layout = Layout(name="root")

    layout.split(
        Layout(name="header", size=6 + max(0, num_apis - 3)),
        Layout(name="main", ratio=1, minimum_size=max_states),
        Layout(name="footer", size=7),
    )
    layout["header"].split_row(
        Layout(name="task", ratio=1),
        Layout(name="costs", minimum_size=30),
    )
    layout["main"].split_row(
        Layout(name="agents"),
        Layout(name="state", ratio=1),
    )
    # layout["agents"].split(*[Layout(name=f"agent:{name}") for name in agent_names])
    return layout


class Header:
    """Display header with clock."""

    def __init__(self, **kwargs):
        super().__init__()
        self.agent = kwargs.pop("agent") if "agent" in kwargs else None
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
            agent_str += (
                f"{self.agent.task}" if self.agent.task else f"{self.agent.name or ''}"
            )
        else:
            agent_str = ""

        grid.add_row(
            agent_str,
            # dt
        )
        return Panel(grid, title="[b]ManyHats[/b] Task Runner")


class APIStats:
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


class ConsolePanel(Console):
    def __init__(self, *args, **kwargs):
        console_file = open(os.devnull, "w")
        super().__init__(record=True, file=console_file, *args, **kwargs)

    def __rich_console__(self, console, options):
        texts = self.export_text(clear=False).split("\n")
        yield from texts[-options.height :]


class AgentStatus:
    def __init__(self, **kwargs):
        super().__init__()
        self.agent: StateMachine = kwargs.pop("agent") if "agent" in kwargs else None

    def __rich__(self) -> Panel:
        table = Table(
            expand=True, box=box.SIMPLE, title="Status", border_style="grey50"
        )

        rows = ordered_nodes_by_distance(self.agent.dag, self.agent.initial_state.id)

        table.add_column(self.agent.name, style="cyan", no_wrap=False)

        active_spinner_name = "dots"
        for i, state in enumerate(rows):
            if i == 0:
                active_spinner_name = "dots"
            else:
                i = (i % 12) + 1
                active_spinner_name = f"dots{i}"

            if state == self.agent.current_state_value:
                table.add_row(
                    Spinner(
                        active_spinner_name,
                        text=Text(
                            f" {self.agent.states_map[state].name}", style="green"
                        ),
                    )
                )
            else:
                table.add_row(self.agent.states_map[state].name, style="grey50")
        return table


class Interface:
    def __init__(self, agent: StateMachine, starttime: datetime | None = None) -> None:
        self.starttime: datetime = starttime or datetime.now()
        self.console: ConsolePanel = ConsolePanel()
        self.agent: StateMachine = agent

    def get_renderable(self):
        layout = make_layout(max_states=len(self.agent.states))
        layout["task"].update(Header(agent=self.agent, starttime=self.starttime))
        layout["costs"].update(APIStats(agent=self.agent))
        layout["state"].update(
            Panel(Pretty(self.agent), title="Variables", border_style="grey50")
        )
        layout["agents"].update(AgentStatus(agent=self.agent))
        layout["footer"].update(Panel(self.console, title="Logs"))
        return layout


def render_dashboard(agent: AgentMachine, task: str):
    # Console()
    starttime = datetime.now()
    dashboard = Interface(agent, starttime=starttime)

    with Live(get_renderable=dashboard.get_renderable, refresh_per_second=10):
        agent.log = dashboard.console
        while True:
            sleep(0.2)
            # update agent.api_stats randomly
            for stat in agent.api_stats:
                stat.count += 1
                stat.time += 0.1
                stat.sent += 1
                stat.received += 1
                stat.cost += 0.0001
            if random.random() < 0.1 and agent.task is None:
                agent.task = task

            if agent.current_state.final:
                print("Finished")
                sleep(1.0)
                return

            if random.random() < 0.1:
                agent.go()
