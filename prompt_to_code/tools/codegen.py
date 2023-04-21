"""A prompt to code agent."""
import logging

from langchain import LLMChain
from langchain.agents import Tool
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

from prompt_to_code.config import PromptToCodeConfig


def _codegen_wrapper(
    language: str | None,
    config: PromptToCodeConfig,
    logger: logging.Logger,
):
    llm = ChatOpenAI(temperature=0.7, model="gpt-4", max_tokens=3000)

    prompt = PromptTemplate(
        input_variables=["input"],
        partial_variables={"language": ((language or "") + " code").strip()},
        template="Generate concise, well documented and executable {language} as best you can that satisfies the following prompt:\n{input}?",
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    return chain.run


def create_codegen_tool(
    language: str, config: PromptToCodeConfig, logger: logging.Logger
):
    return Tool(
        name="Generate code",
        func=_codegen_wrapper(language=language, config=config, logger=logger),
        description="""from a given input, generate code.  The output will be text with the first line being the filename, and the rest of the output being the code.  For example:
    ```
    Action Input: write a python hello world program
    Observation: hello_world.py

    def hello_world():
        print("Hello World!")

    if __name__ == "__main__":
        hello_world()
    ```
""",
    )
