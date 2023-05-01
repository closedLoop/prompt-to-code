import unittest

from manyhats.agents.trivia import LMGTFY
from manyhats.dashboard import render_dashboard


class TestManyHats(unittest.TestCase):
    def test_trivia_agent(self):
        # This should be a test that runs a trivia agent
        # This agent tries to answer questions by searching the web
        # and optionally asking for help from a human for clarification
        # and conduct reasoning or calculations to answer the question
        # This agent should be able to answer questions like:
        # "What is the capital of France?"

        self.assertTrue(True)


if __name__ == "__main__":
    # unittest.main()
    output = render_dashboard(
        LMGTFY(), task="With which game is Santosh Trophy associated?"
    )
    print(output)
