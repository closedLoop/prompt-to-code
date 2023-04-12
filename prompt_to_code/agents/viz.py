from pathlib import Path

from prompt_to_code.agents.agent_tdd import TDDMachine


def build_machine_images(doc_path: str | Path = "./docs/images/"):
    doc_path = Path(doc_path)

    sm = TDDMachine()
    sm._graph().write_png(doc_path / "readme_agent_tdd.png")


if __name__ == "__main__":
    build_machine_images()
