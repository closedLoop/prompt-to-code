from pathlib import Path
from pprint import pprint

import dotenv
import pyfiglet
import typer

from manyhats.agents import AGENTS
from manyhats.dashboard import render_dashboard, run_no_dashboard
from prompt_to_code.config import PromptToCodeConfig
from prompt_to_code.version import VERSION

dotenv.load_dotenv()
config = PromptToCodeConfig()
app = typer.Typer(name="ManyHats")


def banner():
    banner = pyfiglet.figlet_format("ManyHats", font="cybermedium").rstrip()
    banner = "\033[92m" + banner + "\033[0m"
    return f"{banner}  \033[90mv{VERSION}\033[0m"


@app.callback(invoke_without_command=True)
def main(
    output_directory: str = typer.Option(
        None, help="The directory to output the code to"
    )
):
    """This can be used to update the configuration via the CLI to override the default values."""
    global config
    if output_directory is not None:
        config.output_directory = Path(output_directory)
    typer.echo(banner() + "\n")


@app.command()
def list():
    """List the available Roles."""
    typer.echo("Available Roles:")
    for role in AGENTS:
        typer.echo(f"  - {role}")


@app.command()
def run(
    action_item: str = typer.Argument(
        ..., help="A description of the action to be taken"
    ),
    hat: str = typer.Option(
        "general",
        help="The name of the Role to use.  Call 'manyhats list' to see available Roles.",
    ),
    dashboard: bool = typer.Option(True, help="Whether to show the dashboard or not"),
):
    """
    manyhats run --hat trivia "What is the square root of the age of the President of France?"

    """

    PromptToCodeConfig()

    if hat not in AGENTS:
        typer.echo(
            f"Role '{hat}' not found.  Call 'manyhats list' to see available Roles."
        )
        raise typer.Exit(code=1)

    agent = AGENTS[hat]()

    if dashboard:
        output = render_dashboard(agent, task=action_item)
    else:
        output = run_no_dashboard(agent, action_item)
    print(output)


@app.command()
def show_config():
    global config
    typer.echo(pprint(config, compact=True, indent=1))


@app.command()
def show_license():
    typer.echo("https://github.com/closedLoop/prompt-to-code/blob/main/LICENSE")
    typer.echo("Copyright (c) 2023 Sean Kruzel & ClosedLoop Technologies, LLC")


if __name__ == "__main__":
    app()
