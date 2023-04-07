from prompt_to_code.agent import run as run_agent
from prompt_to_code.config import PromptToCodeConfig


def test_build_weather_app():
    """Test the build weather app tool."""
    # setup
    config = PromptToCodeConfig()
    config.output_directory = "./outputs/python-library2"

    run_agent(
        "create a new python library called myweather that scrapes the web for weather using https://www.weather.gov.  Create a requirements.txt file with any dependencies and a setup.py so that the library can be uploaded to pypi and a README.md"
    )


test_build_weather_app()
