from pathlib import Path
from pprint import pprint

import pyfiglet
import typer

from prompt_to_code.agent import process_prompt
from prompt_to_code.config import PromptToCodeConfig
from prompt_to_code.version import VERSION

config = PromptToCodeConfig()
app = typer.Typer(name="prompt-to-code")


def banner():
    banner = pyfiglet.figlet_format("Prompt To Code", font="cybermedium").rstrip()
    banner = "\033[92m" + banner + "\033[0m"
    return f"{banner}  \033[90mv{VERSION}\033[0m"


@app.callback(invoke_without_command=True)
def main(
    output_directory: str
    | None = typer.Option(None, help="The directory to output the code to")
):
    """This can be used to update the configuration via the CLI to override the default values."""
    global config
    if output_directory is not None:
        config.output_directory = Path(output_directory)
    typer.echo(banner() + "\n")


@app.command()
def code(
    prompt: str = typer.Argument(..., help="The prompt to generate code from"),
    language: str
    | None = typer.Argument("python3", help="The language to generate code in"),
    agent: str
    | None = typer.Argument(
        "default", help="The type of behavior used to generate code"
    ),
):
    """Generate code from a prompt and save it to files."""
    global config
    results = process_prompt(
        prompt, language=language or "python3", agent=agent, config=config
    )
    typer.echo(results)


@app.command()
def show_config():
    global config
    typer.echo(pprint(config, compact=True, indent=1))


@app.command()
def show_license():
    typer.echo("MIT License")
    typer.echo("Copyright (c) 2023 Sean Kruzel & ClosedLoop Technologies, LLC")


if __name__ == "__main__":
    app()
