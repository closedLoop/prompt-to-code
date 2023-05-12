from pathlib import Path

import dotenv
from typer import Typer

from manyhats.agents.base import AgentMachine
from manyhats.dashboard import render_dashboard
from manyhats.ee.fantasy_sports_agent import FantasySportsAgent

dotenv.load_dotenv()


def run_sports_handicaper(task: str | None = None):
    """This uses the CLI to communicate with humans"""
    researcher = AgentMachine(
        name="Researcher",
        description="""You are a researcher that works for a sports betting company.""",
    )
    calculator = AgentMachine(
        name="Calculator", description="""You do simple math calculations."""
    )
    print(researcher, calculator)

    if task is None:
        task = "How many receptions has Antonio Brown had in games with 10 or more targets?"
    # task = "What is the average number of fantasy points per game for Amari Cooper dring away games versus home games?"
    return render_dashboard(FantasySportsAgent(), task=task)


def export_graph(agent):
    doc_path = "."
    doc_path = Path(doc_path)
    agent._graph().write_png(doc_path / f"{agent.name.replace(' ','_').lower()}.png")


app = Typer()


@app.command()
def run(task: str | None = None):
    """Run the sports handicaper"""
    run_sports_handicaper(task)


if __name__ == "__main__":
    app()
