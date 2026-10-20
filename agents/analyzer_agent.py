
import ast


class AnalyzerAgent:
    """Analyzes Python syntax and identifies defined functions."""

    def run(self, source_code: str) -> dict:
        try:
            tree = ast.parse(source_code)
        except SyntaxError as error:
            return {
                "valid": False,
                "error": error.msg,
                "line": error.lineno,
                "functions": [],
            }

        functions = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        return {
            "valid": True,
            "error": None,
            "line": None,
            "functions": functions,
        }
