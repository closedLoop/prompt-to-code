from distutils.core import setup

with open("./prompt_to_code/version.py") as f:
    VERSION = f.read().split("=")[1].strip().strip('"')

setup(
    name="prompt_to_code",
    version=VERSION,
    description="generate code from a prompt from a CLI",
    author="Sean Kruzel, ClosedLoop Technologies, LLC",
    author_email="sean.kruzel@closedloop.tech",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    package_data={
        "": ["*.txt", "*.rst", "*.md", "*.csv"],
    },
    packages=["prompt_to_code"],
    entry_points={
        "console_scripts": [
            "p2c=prompt_to_code.__main__:main",
            "prompt-to-code=prompt_to_code.__main__:main",
        ],
    },
)
