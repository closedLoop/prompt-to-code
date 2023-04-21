"""A prompt to code agent."""
import re

from langchain import LLMChain, SerpAPIWrapper
from langchain.agents import (
    AgentExecutor,
    AgentOutputParser,
    LLMSingleActionAgent,
    Tool,
)
from langchain.chat_models import ChatOpenAI
from langchain.prompts import StringPromptTemplate
from langchain.schema import AgentAction, AgentFinish

from prompt_to_code.tools.codegen import create_codegen_tool
from prompt_to_code.tools.file_list import list_file_tool
from prompt_to_code.tools.file_reader import read_file_tool
from prompt_to_code.tools.file_writer import write_to_file_tool
from prompt_to_code.tools.think import relection_tool

# Set up the base template
template = """Generate concise, well documented and executable code as best you can.
Write all documentation as Markdown (.md) files and all command-line commands into a .sh files.
You have access to the following tools:

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
            [
                f" {i+1}. {tool.name}: {tool.description}"
                for i, tool in enumerate(self.tools)
            ]
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
        if match := re.search(regex, llm_output, re.DOTALL):
            action = match[1].strip()
            action_input = match[2]
            # Return the action and action input
            return AgentAction(
                tool=action,
                tool_input=action_input.strip(" ")
                .strip('"')
                .strip("'")
                .strip("```")
                .strip('"""'),
                log=llm_output,
            )

        regex = r"Thought:[\s]*(.*)"
        if match := re.search(regex, llm_output, re.DOTALL):
            return AgentAction(tool="Think", tool_input=match[1], log=llm_output)
        else:
            raise ValueError(f"Could not parse LLM output: `{llm_output}`")


def build_default_agent(config, logger):
    search = SerpAPIWrapper()
    tools = [
        Tool(
            name="Search",
            func=search.run,
            description="useful for when you need to answer questions about current events",
        ),
        create_codegen_tool(language=None, config=config, logger=logger),
        write_to_file_tool(config=config, logger=logger),
        list_file_tool(config=config, logger=logger),
        read_file_tool(config=config, logger=logger),
        relection_tool(config=config, logger=logger),
    ]
    prompt = CustomPromptTemplate(
        template=template,
        tools=tools,
        # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
        # This includes the `intermediate_steps` variable because that is needed
        input_variables=["input", "intermediate_steps"],
    )
    output_parser = CustomOutputParser()

    llm = ChatOpenAI(temperature=0.7, model="gpt-4", max_tokens=3000)

    # LLM chain consisting of the LLM and a prompt
    llm_chain = LLMChain(llm=llm, prompt=prompt)
    tool_names = [tool.name for tool in tools]
    agent = LLMSingleActionAgent(
        llm_chain=llm_chain,
        output_parser=output_parser,
        stop=["\nObservation:"],
        allowed_tools=tool_names,
    )
    return AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True)
