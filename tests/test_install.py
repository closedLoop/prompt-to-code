import unittest
from subprocess import run


class TestInstall(unittest.TestCase):
    def test_prompt_to_code_is_installed(self):
        import prompt_to_code

        self.assertIsNotNone(prompt_to_code)

    def test_prompt_to_code_module(self):
        run(["python", "-m", "prompt_to_code", "--help"])

    def test_prompt_to_code_entrypoint(self):
        run(["prompt_to_code", "--help"])
