
import ast
import json
import subprocess
import sys
from logic_repair import propose_logic_repair



def validate_function(
    source_code: str,
    function_name: str,
    test_cases: list[dict],
) -> dict:
    """Validate a function using input/output test cases."""

    try:
        tree = ast.parse(source_code)
    except SyntaxError as error:
        return {
            "passed": False,
            "message": f"Syntax error on line {error.lineno}: {error.msg}",
            "results": [],
        }

    functions = {
        node.name
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
    }

    if function_name not in functions:
        return {
            "passed": False,
            "message": f"Function '{function_name}' was not found.",
            "results": [],
        }

    # Keep this initial version limited to ordinary function definitions.
    runner = f"""
import json
import sys

namespace = {{}}
exec(compile(sys.stdin.read(), "<submitted_code>", "exec"), namespace)

payload = json.loads(sys.argv[1])
fn = namespace[payload["function_name"]]
results = []

for case in payload["test_cases"]:
    try:
        actual = fn(*case["args"])
        results.append({{
            "expected": case["expected"],
            "actual": actual,
            "passed": actual == case["expected"],
        }})
    except Exception as error:
        results.append({{
            "expected": case["expected"],
            "actual": f"{{type(error).__name__}}: {{error}}",
            "passed": False,
        }})

print(json.dumps(results))
"""

    payload = {
        "function_name": function_name,
        "test_cases": test_cases,
    }

    try:
        process = subprocess.run(
            [
                sys.executable,
                "-I",
                "-c",
                runner,
                json.dumps(payload),
            ],
            input=source_code,
            capture_output=True,
            text=True,
            timeout=3,
        )

        if process.returncode != 0:
            return {
                "passed": False,
                "message": "Test execution failed.",
                "results": [],
            }

        results = json.loads(process.stdout)

    except subprocess.TimeoutExpired:
        return {
            "passed": False,
            "message": "Tests exceeded the 3-second time limit.",
            "results": [],
        }
    except (json.JSONDecodeError, OSError):
        return {
            "passed": False,
            "message": "Could not process test results.",
            "results": [],
        }

    all_passed = all(item["passed"] for item in results)

    return {
        "passed": all_passed,
        "message": (
            "All tests passed."
            if all_passed
            else "One or more tests failed."
        ),
        "results": results,
    }

