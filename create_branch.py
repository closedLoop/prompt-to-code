import re
import subprocess

import requests


class GitBranchCRUD:
    def __init__(self):
        pass

    def _run_command(self, command) -> tuple[str, bool]:
        """Returns stdout of command and a boolean indicating if there was an error"""
        try:
            result = subprocess.run(
                command, capture_output=True, text=True, check=True, shell=True
            )
            return result.stdout.strip(), False
        except subprocess.CalledProcessError as e:
            if e.stdout:
                return e.stdout.strip(), True
            return f"Command failed: {command}. Error: {e}", True
        except Exception as e:
            raise RuntimeError(f"Command failed: {command}. Error: {e}") from e

    def create_branch(self, branch_name: str | None):
        # Check if in a git repo
        self._run_command("git rev-parse --is-inside-work-tree")

        # Check if branch name is valid and provided
        if not branch_name:
            raise RuntimeError("Branch name is required")
        if not re.match(r"^(?!\.)[a-zA-Z0-9\-\._]+(?<!\.)$", branch_name):
            raise RuntimeError("Invalid branch name")

        (status, failed) = self._run_command("git status --porcelain")
        if status or failed:
            raise RuntimeError(
                "You have uncommitted changes. Commit or stash your changes before creating a new branch"
            )

        # Check if branch exists
        branches, failed = self._run_command("git branch --list")
        if branch_name in branches.split("\n"):
            raise RuntimeError(f"Branch {branch_name} already exists")

        # Check out branch
        self._run_command(f"git checkout -b {branch_name}")
        print(f"Switched to a new branch: {branch_name}")

    def commit_changes(self, commit_message: str):
        if not commit_message:
            raise RuntimeError("Commit message is required")

        # Check if uncommitted changes exist
        status, failed = self._run_command("git status --porcelain")
        if not status:
            raise RuntimeError("No changes to commit")

        # Add changes and create a commit
        self._run_command("git add .")
        self._run_command(f'git commit -m "{commit_message}"')
        print(f"Changes committed with message: {commit_message}")

    def create_pull_request(
        self,
        base_branch: str,
        head_branch: str,
        title: str,
        token: str,
        repo_owner: str,
        repo_name: str,
    ):
        if (
            not base_branch
            or not head_branch
            or not title
            or not token
            or not repo_owner
            or not repo_name
        ):
            raise RuntimeError("Missing required information to create a pull request")

        # Check if the branches exist
        branches, failed = self._run_command("git branch --list")
        if base_branch not in branches.split("\n") or head_branch not in branches.split(
            "\n"
        ):
            raise RuntimeError("One or both branches do not exist")

        # Create a pull request using GitHub API
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github+json",
        }
        data = {
            "title": title,
            "head": head_branch,
            "base": base_branch,
        }

        response = requests.post(
            f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls",
            headers=headers,
            json=data,
        )

        if response.status_code != 201:
            raise RuntimeError(
                f"Failed to create a pull request. Error: {response.json()}"
            )

        pull_request_url = response.json()["html_url"]
        print(f"Pull request created: {pull_request_url}")


if __name__ == "__main__":
    git_branch_creator = GitBranchCRUD()
    git_branch_creator.create_branch("new_branch")
    git_branch_creator.create_branch("new_branch")
