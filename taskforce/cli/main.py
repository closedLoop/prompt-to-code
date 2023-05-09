import os
from pathlib import Path
from pprint import pprint
from typing import Annotated

import dotenv
import pyfiglet
import typer

# from taskforce.agents import AGENTS
# from taskforce.dashboard import render_dashboard, run_no_dashboard
from taskforce.config import TaskForceConfig
from taskforce.version import VERSION

dotenv.load_dotenv()
config = TaskForceConfig()
app = typer.Typer(name="TaskForce")


def banner():
    banner = pyfiglet.figlet_format("TaskForce", font="cybermedium").rstrip()
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
def login(
    username: Annotated[
        str | None, typer.Argument(..., help="The username to authenticate with.")
    ] = None
):
    """
    Authenticates the user and sets the current user as ~/.taskforce/current_user
    """
    if username := (username or os.getlogin()).lower().strip():
        # Create the ~/.taskforce directory if it doesn't exist
        taskforce_dir = Path.home() / ".taskforce"
        taskforce_dir.mkdir(parents=True, exist_ok=True)

        # Set the current user
        current_user_file = taskforce_dir / "current_user"
        with current_user_file.open("w") as f:
            f.write(username)

        typer.echo(f"Logged in as {username}")
    else:
        typer.echo("Invalid username")


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

    TaskForceConfig()
    AGENTS = []
    if hat not in AGENTS:
        typer.echo(
            f"Role '{hat}' not found.  Call 'manyhats list' to see available Roles."
        )
        raise typer.Exit(code=1)

    AGENTS[hat]()

    # if dashboard:
    #     output = render_dashboard(agent, task=action_item)
    # else:
    #     output = run_no_dashboard(agent, action_item)
    # print(output)


@app.command()
def show_config():
    global config
    typer.echo(pprint(config, compact=True, indent=1))


@app.command()
def info():
    # typer.echo(banner() + "\n")
    typer.echo("https://github.com/closedLoop/prompt-to-code/blob/main/LICENSE")
    typer.echo("Copyright (c) 2023 Sean Kruzel & ClosedLoop Technologies, LLC")


if __name__ == "__main__":
    app()
