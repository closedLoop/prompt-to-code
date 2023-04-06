"""A prompt to code agent."""
import logging
import re
from pathlib import Path

from langchain import LLMChain, OpenAI, SerpAPIWrapper
from langchain.agents import (
    AgentExecutor,
    AgentOutputParser,
    LLMSingleActionAgent,
    Tool,
)
from langchain.prompts import PromptTemplate, StringPromptTemplate
from langchain.schema import AgentAction, AgentFinish

from prompt_to_code.config import PromptToCodeConfig
from prompt_to_code.logger import create_logger


def create_file_wrapper(config: PromptToCodeConfig, logger: logging.Logger):
    fdir = Path(config.output_directory)
    fdir.mkdir(parents=True, exist_ok=True)

    def file_wrapper(contents: str):
        """Write the contents to the file."""
        filename, *code = contents.splitlines()
        code = "\n".join(code)
        logger.info(f"Writing {filename} to {fdir}")
        logger.info(f"The code is {code}")
        file_path = fdir / filename

        if file_path.exists():
            new_filename = (
                ".".join(filename.split(".")[:-1]) + "-new." + filename.split(".")[-1]
            )
            logger.info(
                f"File {filename} already exists, changing the name to {new_filename}"
            )
            file_path = fdir / new_filename

        file_path.write_text(code)

    return file_wrapper


def generate_code_wrapper(
    language: str | None,
    config: PromptToCodeConfig,
    logger: logging.Logger,
    temperature=0.2,
):
    llm = OpenAI(temperature=temperature, max_tokens=3000)

    prompt = PromptTemplate(
        input_variables=["input"],
        template="Generate concise, well documented and executable code as best you can that satisfies the following prompt:\n{input}?",
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run


# Set up the base template
template = """Generate concise, well documented and executable code as best you can. You have access to the following tools:

{tools}

Use the following format:

Prompt: a description of the code you must write
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: a JSON formatted list of the filenames that were created or modified

Begin! Remember that at least one file must be created and that the final output is a JSON formatted list of the filenames.

Prompt: {input}

{agent_scratchpad}"""


# Set up a prompt template
class CustomPromptTemplate(StringPromptTemplate):
    # The template to use
    template: str
    # The list of tools available
    tools: list[Tool]

    def format(self, **kwargs) -> str:
        # Get the intermediate steps (AgentAction, Observation tuples)
        # Format them in a particular way
        intermediate_steps = kwargs.pop("intermediate_steps")
        thoughts = ""
        for action, observation in intermediate_steps:
            thoughts += action.log
            thoughts += f"\nObservation: {observation}\nThought: "
        # Set the agent_scratchpad variable to that value
        kwargs["agent_scratchpad"] = thoughts
        # Create a tools variable from the list of tools provided
        kwargs["tools"] = "\n".join(
            [f"{tool.name}: {tool.description}" for tool in self.tools]
        )
        # Create a list of tool names for the tools provided
        kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
        return self.template.format(**kwargs)


class CustomOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> AgentAction | AgentFinish:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action: (.*?)[\n]*Action Input:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")
        action = match[1].strip()
        action_input = match[2]
        # Return the action and action input
        return AgentAction(
            tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output
        )


# def construct_prompt(prompt: str, language:str='python3', agent: str = "default", config: PromptToCodeConfig | None =None, logger: logging.Logger | None = None) -> str:


def process_prompt(
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

    # Define which tools the agent can use to answer user queries
    search = SerpAPIWrapper()
    tools = [
        Tool(
            name="Search",
            func=search.run,
            description="useful for when you need to answer questions about current events",
        ),
        Tool(
            name="Generate code",
            func=generate_code_wrapper(language=language, config=config, logger=logger),
            description="""from a given input, generate code.  The output will be text with the first line being the filename, and the rest of the output being the code.  For example:
Action Input: write a python hello world program
Observation: hello_world.py

def hello_world():
    print("Hello World!")

if __name__ == "__main__":
    hello_world()
""",
        ),
        Tool(
            name="Write code to file",
            func=create_file_wrapper(config, logger=logger),
            description="""writes the input to the filesystem.  The first line of the input should be a unique and descriptive filename, and the rest of the input should be the code to write to the file.  For example:
Action Input: hello_world.py

def hello_world():
    print("Hello World!")

if __name__ == "__main__":
    hello_world()

Observation: saved code to hello_world.py
""",
        ),
    ]
    prompt = CustomPromptTemplate(
        template=template,
        tools=tools,
        # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
        # This includes the `intermediate_steps` variable because that is needed
        input_variables=["input", "intermediate_steps"],
    )
    output_parser = CustomOutputParser()

    llm = OpenAI(temperature=0.7)

    # LLM chain consisting of the LLM and a prompt
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    tool_names = [tool.name for tool in tools]
    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=output_parser,
        stop=["\nObservation:"],
        allowed_tools=tool_names,
    )
    agent_executor = AgentExecutor.from_agent_and_tools(
        agent=agent, tools=tools, verbose=True
    )
    return agent_executor.run(input)
