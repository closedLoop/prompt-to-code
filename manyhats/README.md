# Manyhats
A framework for managing many Agents coordinating to solve a problem.

## Services

 * Version Control:
   * local git:
   * Github CLI - used to create and edit repos within an organization or user account
 * Github Issue Tracker:
   * A local issue tracker - used to create and edit issues and organize them into projects
   * Linear.app API - used to create and edit issues and organize them into projects
 * Company Notes and plans:
   * Notion / Obsydian / Roam / Google Docs / Github Wiki / etc - used to create and edit notes and plans

## Workflow
A human triggers a new 'project' via CLI or creating a new 'milestone' in the issue tracker and tagging @manyhats

A milestone contains many projects, and a project contains many issues.  Issues can contain issues

Depending on the type of project, certain types of Agents will be spawned to monitor activity in the project and take actions to complete the project.

The general framework for an agent is

 * Thinking:
   * Understand the project and the issues and evaluates when the job is done.
   * Creates subtasks, with dependency graph and assigns them to other agents.
   * Commits changes to the appropriate github repos
 * Doing:
   * A worker that performs the tasks required to complete the task


When given a task, an agent evaluates the feasibility of the task, requests additional information, determines the acceptance criterion and plans subsequent steps and suggests the appropriate state-machines with initial conditions for each step.
Each task has:
 * Main Objective:
 * Relevant Context:
   * Local Context from parent and sibling tasks.
   * Global Context from the milestone, project and repository
 * Acceptance Criteria:
 * Examples:
 * State Machine Canidates:

    def evaluate_task(task):
        """
        Given a task, this function evaluates the feasibility of the task, requests additional information,
        determines the acceptance criterion, plans subsequent steps and suggests the appropriate state-machines
        with initial conditions for each step.

        vbnet
        Copy code
        Parameters:
        task (str): The task description provided to the agent.

        Returns:
        dict: A dictionary containing the feasibility, additional information required, acceptance criterion,
            planned steps, and suggested state-machines with initial conditions for each step.
        """

        # NOTE: This function is a placeholder and does not actually perform the described actions.
        # You would need to implement the actual logic or use a more advanced AI system to perform these tasks.
        # The function currently returns a static example response.

        response = {
            "feasibility": "To be determined",
            "additional_information": "Please provide more details about the task.",
            "acceptance_criterion": "Task should be completed within the given deadline and meet the specified requirements.",
            "planned_steps": [
                {
                    "step": "Step 1",
                    "state_machine": "StateMachine1",
                    "initial_conditions": "Initial conditions for Step 1",
                },
                {
                    "step": "Step 2",
                    "state_machine": "StateMachine2",
                    "initial_conditions": "Initial conditions for Step 2",
                },
            ],
        }

        return response

This is where AgentTDD comes into play.  It assembles tools and collects context and memories.  It determines if the task is completed.

1. evaluates the feasibility of the task

2. requests additional information and
3. plans steps and suggests next actions
4. updates global states and initial starting conditions and perhaps selects from various state machines based on the task at hand
    1. This is where AgentTDD comes into play
5. assembles tools and collects context and memories
6. Determines if the task is completed


# Basic Agents
 1. Test-Driven Development Agent
 2. Marketing Agent
 3. Sales Agent
 4. Customer Service Agent
 5. Project Management Agent
 6. CEO Agent
 7. DevOps Agent
 8. Frontend Agent
 8. Backend Agent

# Enterprise Features
 1. Subscibe to github or linear issues
 2. Run in a Docker container - pull from github
 3. Github Actions - run on a schedule or on a webhook
