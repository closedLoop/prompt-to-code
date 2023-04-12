FUNCTION_MENTION = """
## Filename: `{filename}`
### Name: {name}
```{language}
{definition}{docstring}
```""".lstrip()

FUNCTIONS_SECTION = """
# FUNCTIONS: You can use any of the following functions to help you:
""".lstrip()


STUB_STEP_PROMPT = """
You are a developer who strictly follows test-driven development best practices and uses the Red-Green-Refactor loop.

Given the following prompt, write a "stub" file that just defines the function names, their arguments and specifies the return types to be later implemented.  Do not implement the function themselves.

{functions_section}

# FILENAME: {filename}

# PROMPT:
{prompt}

{examples}

# STUB FILE:
""".lstrip()

RED_STEP_PROMPT = """
You are a developer who strictly follows test-driven development best practices and uses the Red-Green-Refactor loop.

Given the following code prompt implement a failing test using `{test_library}`.  The CODE section below should include only the test code and not the function implementation.

{functions_section}

# FILENAME: {filename}

# PROMPT:
{prompt}

{examples}

# TESTS (excluding function implementations):
""".lstrip()

GREEN_STEP_PROMPT = """
You are a developer who strictly follows test-driven development best practices and uses the Red-Green-Refactor loop.

Given the following code prompt and failing test, implement the functions to pass the tests.  The CODE section below should NOT include the test code.

{functions_section}

# FILENAME: {filename}

# PROMPT:
{prompt}

{examples}

# TESTS:
{tests}

# FAILED TESTS MESSAGE:
{test_errors}

# CODE (excluding tests):
""".lstrip()


ERROR_PROMPT = """
You are a developer who strictly follows test-driven development best practices and uses the Red-Green-Refactor loop.

You are provided the following prompt and code which raises the following error,
The CORRECTED CODE section should only provide the complete corrected code.  Include any descriptions in comments.

{functions_section}

# FILENAME: {filename}

# PROMPT:
{prompt}

{examples}

Running the code raises the following error, please only the corrected code.  Include any descriptions in comments.

# ERROR:
{error}

# FAILING CODE:
{code}

# CORRECTED CODE:
""".lstrip()

ERROR_PROMPT_OLD = """
Running the code raises the following error, please only the corrected code.  Include any descriptions in comments.

# ERROR:
{error}

# FAILING CODE:
{code}

# CORRECTED CODE:
""".lstrip()
