from manyhats.agent import AgentMachine
from manyhats.ee.fantasy_sports_agent import FantasySportsAgent

from .coders import TDDCoderAgent
from .trivia import LMGTFY, Guessing, Trivia

AGENTS = {
    "general": AgentMachine,
    "trivia": Trivia,
    "search": LMGTFY,
    "guess": Guessing,
    "coder": TDDCoderAgent,
    "sports": FantasySportsAgent,
}
