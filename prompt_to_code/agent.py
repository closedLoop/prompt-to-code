"""A prompt to code agent."""
import logging

from prompt_to_code.agents.basic_linear import build_default_agent
from prompt_to_code.config import PromptToCodeConfig
from prompt_to_code.logger import create_logger


def run(
    input: str,
    language: str = "python3",
    agent: str = "default",
    config: PromptToCodeConfig | None = None,
    logger: logging.Logger | None = None,
):
    """Process a prompt and generate code."""
    if config is None:
        config = PromptToCodeConfig()

    if logger is None:
        logger = create_logger(config.logging)

    if agent != "default":
        raise ValueError(f"Unknown agent: {agent}")

    logging.debug(f"Agent: {agent}")
    logging.debug(f"Language: {language}")
    logging.debug(f"Processing prompt: {input}")

    agent_executor = build_default_agent(config=config, logger=logger)
    return agent_executor.run(input)
