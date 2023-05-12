from pathlib import Path

import dotenv

from manyhats.agents.base import AgentMachine
from manyhats.dashboard import render_dashboard
from manyhats.ee.fantasy_sports_agent import FantasySportsAgent


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


if __name__ == "__main__":
    dotenv.load_dotenv()
    run_sports_handicaper()
