

import ast
from logic_repair import propose_logic_repair
from validator import validate_function


def test_valid_python_code_parses():
    source_code = """
def multiply(a, b):
    return a * b
"""
    ast.parse(source_code)


def test_invalid_python_code_is_detected():
    source_code = "def multiply(a, b)\n    return a * b"
    try:
        ast.parse(source_code)
    except SyntaxError:
        pass
    else:
        raise AssertionError("Invalid Python code was not detected")


def test_addition_can_be_changed_to_multiplication():
    source_code = """def calculate(a, b):
    return a + b
"""
    result = propose_logic_repair(source_code, "calculate")
    assert result["success"] is True
    assert "return a * b" in result["repaired_code"]


def test_missing_function_is_rejected():
    source_code = """def calculate(a, b):
    return a + b
"""
    result = propose_logic_repair(source_code, "multiply")
    assert result["success"] is False
    assert result["repaired_code"] == source_code


def test_unsupported_operator_is_rejected():
    source_code = """def calculate(a, b):
    return a - b
"""
    result = propose_logic_repair(source_code, "calculate")
    assert result["success"] is False
    assert result["repaired_code"] == source_code


def test_repaired_multiplication_produces_correct_result():
    source_code = """def calculate(a, b):
    return a + b
"""
    result = propose_logic_repair(source_code, "calculate")

    assert result["success"] is True

    namespace = {}
    exec(result["repaired_code"], namespace)

    assert namespace["calculate"](3, 4) == 12
    assert namespace["calculate"](5, 6) == 30
    assert namespace["calculate"](7, 8) == 56


def test_original_addition_behavior_would_fail_multiplication_cases():
    source_code = """def calculate(a, b):
    return a + b
"""
    namespace = {}
    exec(source_code, namespace)

    assert namespace["calculate"](3, 4) != 12
    assert namespace["calculate"](5, 6) != 30

def test_validator_checks_expected_outputs():
    repaired_code = """def multiply(a, b):
    return a * b
"""
    test_cases = [
        {"args": [3, 4], "expected": 12},
        {"args": [5, 6], "expected": 30},
        {"args": [7, 8], "expected": 56},
    ]

    result = validate_function(
        repaired_code,
        "multiply",
        test_cases,
    )

    assert result["passed"] is True
    assert result["message"] == "All tests passed."
    assert len(result["results"]) == 3
    assert all(item["passed"] for item in result["results"])




