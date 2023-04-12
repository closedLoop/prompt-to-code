import ast
import hashlib
from collections import defaultdict

import networkx as nx

from prompt_to_code.agents.agent_tdd import AvailableMethods


class FunctionExtractor(ast.NodeVisitor):
    def __init__(
        self,
        source_lines,
        file_name=None,
        branch=None,
        usages: dict[str, dict[str, list[tuple[str, int]]]] | None = None,
    ):
        super().__init__()
        self.function_data: list[AvailableMethods] = []
        self.source_lines = source_lines
        self.file_name = file_name
        self.branch = branch
        self.usages = usages

    def visit_FunctionDef(self, node):
        name = node.name
        args = [arg.arg for arg in node.args.args]
        kwargs = [
            (arg.arg, ast.literal_eval(arg.default)) for arg in node.args.kwonlyargs
        ]
        return_type = getattr(node.returns, "id", None)

        start_line = node.lineno - 1
        end_line = node.body[0].lineno - 1
        function_source = (
            "".join(self.source_lines[start_line:end_line]) + "    ...".strip()
        )

        start_line = node.lineno - 1
        end_line = node.end_lineno
        function_code = "".join(self.source_lines[start_line:end_line]).strip()
        code_hash = hashlib.md5(function_code.encode("utf-8")).hexdigest()
        # todo add embedding

        self.function_data.append(
            AvailableMethods(
                name=name,
                definition=function_source,
                description=None,
                parameters=(args, kwargs),
                return_type=return_type,
                file_name=self.file_name,
                branch=self.branch,
                code_hash=code_hash,
                embedding=None,
                usages=self.usages.get(name, {}),
            )
        )
        self.generic_visit(node)


class FunctionCallGraph(ast.NodeVisitor):
    def __init__(self):
        self.graph = defaultdict(
            lambda: {"called_after": set(), "called_inside": set()}
        )
        self.called_functions = []

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name):
            function_name = node.func.id
            if self.called_functions:
                # Add edges for called_after and called_inside relationships
                self.graph[function_name]["called_after"].add(self.called_functions[-1])
                self.graph[self.called_functions[-1]]["called_inside"].add(
                    function_name
                )

            # Update the list of called functions
            self.called_functions.append(function_name)

        # Visit child nodes
        self.generic_visit(node)

    def visit_FunctionDef(self, node):
        # Reset the list of called functions when entering a new function
        self.called_functions = []
        self.generic_visit(node)


def create_function_call_graph(content):
    tree = ast.parse(content)
    visitor = FunctionCallGraph()
    visitor.visit(tree)

    G = nx.DiGraph()
    for function_name, function_data in visitor.graph.items():
        for called_function in function_data["called_after"]:
            if (function_name, called_function) in G.edges:
                G[function_name][called_function]["weight"] += 1
            else:
                G.add_edge(
                    function_name, called_function, label="called_after", weight=1
                )
    return G


def build_usages_from_graph(G):
    return {
        node: {
            "before": [
                (n[0], n[1]["weight"])
                for n in sorted(
                    G[node].items(), key=lambda x: x[1]["weight"], reverse=True
                )
            ],
            "after": [
                (n[0], n[2]["weight"])
                for n in sorted(
                    G.in_edges(node, data=True),
                    key=lambda x: x[2]["weight"],
                    reverse=True,
                )
            ],
        }
        for node in G.nodes
    }


def extract_function_definitions(content) -> tuple[list[AvailableMethods], nx.DiGraph]:
    G = create_function_call_graph(content)
    usages = build_usages_from_graph(G)

    source_lines = content.splitlines(True)
    tree = ast.parse(content)
    extractor = FunctionExtractor(
        source_lines, file_name=None, branch=None, usages=usages
    )
    extractor.visit(tree)

    return extractor.function_data, G


if __name__ == "__main__":
    # Replace 'your_python_file.py' with the path to the Python file you want to process
    file_path = "prompt_to_code/agents/basic_linear.py"

    with open(file_path) as file:
        content = file.read()
    data, G = extract_function_definitions(content)

    # networkx plot of function_call_graph
    import matplotlib.pyplot as plt

    plt.figure(figsize=(20, 20))
    nx.draw(G, with_labels=True, node_size=1000, font_size=10)

    # save figure
    plt.savefig("function_call_graph.png")
