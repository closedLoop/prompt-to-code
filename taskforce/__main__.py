"""This is the main entrypoint for the cli"""
import pyfiglet

from taskforce.cli.main import app
from taskforce.version import VERSION


def banner():
    banner = pyfiglet.figlet_format("TaskForce", font="cybermedium").rstrip()
    banner = "\033[92m" + banner + "\033[0m"
    return f"{banner}  \033[90mv{VERSION}\033[0m"


def main():
    app()


if __name__ == "__main__":
    main()
