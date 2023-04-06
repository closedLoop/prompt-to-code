import unittest

from prompt_to_code.config import PromptToCodeConfig
from prompt_to_code.logger import LoggerConfig


class TestConfig(unittest.TestCase):
    def test_prompt_to_code_configs(self):
        config = PromptToCodeConfig()
        self.assertIsInstance(
            config.logging, LoggerConfig, msg="config.logging is not a LoggerConfig"
        )
