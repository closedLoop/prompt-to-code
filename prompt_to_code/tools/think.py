"""A prompt to code agent."""
import logging

from langchain import LLMChain
from langchain.agents import Tool
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

from prompt_to_code.config import PromptToCodeConfig


def _reflection_wrapper(
    config: PromptToCodeConfig,
    logger: logging.Logger,
):
    llm = ChatOpenAI(temperature=0.7, model="gpt-4", max_tokens=2000)

    prompt = PromptTemplate(
        input_variables=["input"],
        template="""{input}\n now determin the single next best action to take, should be one of the specified tools.  Format your response as follows:\nAction: tool_name\nAction Input: formatted input for the tool""",
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run


def relection_tool(config: PromptToCodeConfig, logger: logging.Logger):
    return Tool(
        name="Think",
        func=_reflection_wrapper(config=config, logger=logger),
        description="""Confinue to expand your thinking from the previous steps and determine the next best action.""",
    )
