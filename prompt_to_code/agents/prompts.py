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

You are provided the following function definitions, prompt and code.  The code when executed raises the following error,
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
```{language}
{code}
```

Correct the failing code that raised the error by making only the smallest changes possible to the code.
Use references to function and filenames above where possible and do not implement new functions unless absolutly required.
Only provide clean, executable code where any descriptions are in comments.

# CORRECTED CODE:
```{language}
""".lstrip()
