# Prompt-to-Code
Use large language models like GPT-4 to write code directly from the CLI

Prompt-to-Code is a Python library that converts natural language text prompts into executable Python code. With this library, you can quickly generate Python code by simply describing the task you want to perform in natural language and it will save it to files to be executed by an intepreter.

## Usage

    $ p2c code "a need a dashboard react component that has a menu, sidebar, chatbox and footer, the name of the app is 'Buildittheywillcome' and it should use typescript"


## Installation
To install the Prompt-to-Code library, you can use pip, the Python package installer, as follows:


    pip install prompt-to-code

## Development

### Creating a Virtual Environment
It is a good practice to create a virtual environment for your Python projects. To create a new virtual environment, you can use the venv module that comes with Python.

First, create a new directory for your project:

    mkdir prompt-to-code
    cd prompt-to-code

Create a new virtual environment inside the directory:

    python3 -m venv env

Activate the virtual environment:

    source env/bin/activate

On Windows, use the following command instead:

    env\Scripts\activate

### Requirements

    pip install -r requirements.txt
    pip install -e .
    pip install -r requirements-dev.txt


### Commit-hooks

    # Install the pre-commit hooks
    pre-commit install --install-hooks

    # Install the Opencommit
    npm install -g opencommit
    opencommit config set OPENAI_API_KEY=<your_api_key>opencommit     opencommit config set emoji=true
    opencommit config set description=true
    opencommit hook set


## Running the Test Suite
Prompt-to-Code comes with a test suite that you can run to ensure that everything is working correctly. To run the test suite, follow these steps:

Clone the Prompt-to-Code repository:

    git clone git@github.com:closedLoop/prompt-to-code.git
    cd prompt-to-code

### Install the test dependencies:

    pip install -r requirements-dev.txt

Run the tests:

    pytest

## Usage
To use the Prompt-to-Code library, simply import the prompt_to_code function from the prompt_to_code module and pass a natural language prompt as a string argument. The function will return a string with the corresponding Python code.

### CLI

    $p2c "Create function that

### import as a library
    from prompt_to_code import prompt_to_code

    prompt = "Create a list of the first 10 even numbers."
    code = prompt_to_code(prompt)

    print(code)
    # Output: [i*2 for i in range(10)]

## Contributing
If you would like to contribute to Prompt-to-Code, please follow these steps:

1. Fork the repository on GitHub.
1. Clone your fork to your local machine.
1. Create a new branch and make your changes.
1. Write tests to ensure that your changes work as expected.
1. Run the test suite and ensure that all tests pass.
1. Push your changes to your fork.
1. Open a pull request on GitHub.
