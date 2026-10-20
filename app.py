

import ast
import streamlit as st

from repair import repair_code
from validator import validate_function
from logic_repair import propose_logic_repair
from agents.coordinator import Coordinator
if "repair_history" not in st.session_state:
    st.session_state.repair_history = []


def analyze_code(source_code: str) -> dict:
    """Check whether Python source code is syntactically valid."""

    try:
        tree = ast.parse(source_code)
    except SyntaxError as error:
        return {
            "valid": False,
            "message": error.msg,
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
        "message": "No syntax errors detected.",
        "line": None,
        "functions": functions,
    }


# -------------------- APP HEADER --------------------

st.set_page_config(
    page_title="AI Code Repair",
    page_icon="🛠️",
)

st.title("AI Code Repair System")
st.write("Analyze, repair, and validate Python code.")


# -------------------- CODE INPUT --------------------

default_code = """def multiply(a, b):
    return a + b
"""

source_code = st.text_area(
    "Paste Python code",
    value=default_code,
    height=220,
)


# -------------------- SYNTAX ANALYSIS --------------------

st.divider()
st.subheader("1. Python Syntax Analysis")

if st.button("Analyze Code"):
    if not source_code.strip():
        st.warning("Please enter some Python code.")
    else:
        result = analyze_code(source_code)

        if result["valid"]:
            st.success(result["message"])
            st.write("Functions found:", result["functions"])
        else:
            st.error(
                f"Syntax error on line {result['line']}: "
                f"{result['message']}"
            )


# -------------------- AUTOMATIC SYNTAX REPAIR --------------------

st.divider()
st.subheader("2. Automatic Syntax Repair")

if st.button("Try to Repair Code"):
    repair_result = repair_code(source_code)

    if repair_result["success"]:
        st.success("A syntax repair was applied.")
        st.code(
            repair_result["repaired_code"],
            language="python",
        )

        for change in repair_result["changes"]:
            st.write("- ", change)
    else:
        st.warning(
            "No supported repair was found. "
            "The code may need a different fix."
        )


# -------------------- TEST-BASED BUG DETECTION --------------------

st.divider()
st.subheader("3. Test-Based Bug Detection")

function_name = st.text_input(
    "Function name to test",
    value="multiply",
    key="function_name",
)

st.subheader("Custom Test Cases")

test_input = st.text_area(
    "Enter test cases as JSON",
    value='''[
    {"args": [2, 3], "expected": 6},
    {"args": [4, 5], "expected": 20},
    {"args": [0, 7], "expected": 0}
]''',
    height=150,
    key="custom_test_cases",
)

try:
    test_cases = __import__("json").loads(test_input)

    if not isinstance(test_cases, list):
        raise ValueError("Test cases must be a JSON list.")

    if not all(
        isinstance(case, dict)
        and isinstance(case.get("args"), list)
        and "expected" in case
        for case in test_cases
    ):
        raise ValueError(
            'Each test must contain "args" (a list) '
            'and "expected".'
        )

    st.success(f"{len(test_cases)} test cases loaded.")

except (ValueError, TypeError) as error:
    test_cases = []
    st.error(f"Invalid test cases: {error}")

st.write("Example tests for multiply(a, b):")
st.json(test_cases)

if st.button("Run Tests"):
    if not function_name.strip():
        st.warning("Enter a function name.")
    else:
        result = validate_function(
            source_code,
            function_name.strip(),
            test_cases,
        )

        if result["passed"] is True:
            st.success(result["message"])
        elif result["passed"] is False:
            st.error(result["message"])
        else:
            st.info(result["message"])

        if result.get("results"):
            st.write("Individual test results:")
            st.json(result["results"])


# -------------------- AUTOMATIC LOGIC-BUG REPAIR --------------------

st.divider()
st.subheader("4. Automatic Logic-Bug Repair")

if st.button("Propose Logic Repair"):
    proposal = propose_logic_repair(
        source_code,
        function_name.strip(),
    )

    if proposal["success"]:
        st.info(proposal["message"])
        st.code(
            proposal["repaired_code"],
            language="python",
        )

        st.write(
            "Use the Multi-Agent Code Repair section below "
            "to validate a proposed repair through the agents."
        )
    else:
        st.warning(proposal["message"])


# -------------------- MULTI-AGENT CODE REPAIR --------------------

st.divider()
st.header("5. Multi-Agent Code Repair")

st.write(
    "Run the Analyzer, Repair, and Validator agents "
    "through the Coordinator."
)


if st.button("Run Multi-Agent Repair"):
    if not function_name.strip():
        st.warning("Enter a function name.")
    else:
        coordinator = Coordinator()

        result = coordinator.run(
            source_code=source_code,
            function_name=function_name.strip(),
            test_cases=test_cases,
        )

        st.session_state.repair_history.append({
            "function": function_name.strip(),
            "original_code": source_code,
            "repair": result.get("repair"),
            "validation": result.get("validation"),
            "success": result.get("success", False),
            "stage": result.get("stage", "unknown"),
        })

        st.subheader("Analysis")
        st.json(result.get("analysis", {}))

        st.subheader("Repair Proposal")
        repair = result.get("repair")

        if repair:
            st.write("Strategy:", repair.get("strategy"))
            st.write("Message:", repair.get("message"))
            st.code(
                repair.get("code", repair.get("repaired_code", "")),
                language="python",
            )
        else:
            st.info("No repair was proposed.")

        st.subheader("Validation")
        validation = result.get("validation")

        if validation:
            st.write(validation.get("message", ""))
            st.json(validation.get("results", []))
        else:
            st.info("Validation was not completed.")

        if result.get("success"):
            st.success("Multi-agent workflow completed successfully!")
        else:
            st.warning(
                f"Workflow did not complete successfully. "
                f"Current stage: {result.get('stage', 'unknown')}"
            )


        st.subheader("Analysis")
        st.json(result.get("analysis", {}))

        st.subheader("Repair Proposal")
        repair = result.get("repair")

        if repair and repair.get("success"):
            st.write("Strategy:", repair.get("strategy"))
            st.write("Message:", repair.get("message"))
            st.code(
                repair.get("code", ""),
                language="python",
            )
        elif repair:
            st.warning(
                repair.get("message", "No repair was proposed.")
            )
        else:
            st.info("The repair agent did not return a proposal.")

        st.subheader("Validation")
        validation = result.get("validation")

        if validation:
            st.write(validation.get("message", ""))
            st.json(validation.get("results", []))
        else:
            st.info("Validation was not completed.")

        if result.get("success"):
            st.success("All validation tests passed!")
        else:
            st.warning(
                "The workflow did not complete successfully. "
                f"Current stage: {result.get('stage', 'unknown')}"
            )
          
# -------------------- MULTI-AGENT CODE REPAIR --------------------

st.divider()
st.header("5. Multi-Agent Code Repair")

st.write(
    "Run the Analyzer, Repair, and Validator agents "
    "through the Coordinator."
)

function_name = st.text_input(
    "Function name to test",
    value="multiply",
    key="multi_agent_function_name",
)

# Custom test cases
st.subheader("Custom Test Cases")

number_of_tests = st.number_input(
    "Number of test cases",
    min_value=1,
    max_value=10,
    value=3,
    step=1,
    key="custom_test_count",
)

test_cases = []

for i in range(int(number_of_tests)):
    st.write(f"Test Case {i + 1}")

    col1, col2, col3 = st.columns(3)

    with col1:
        arg1 = st.number_input(
            f"Argument 1 — Test {i + 1}",
            value=2 if i == 0 else 0,
            key=f"arg1_{i}",
        )

    with col2:
        arg2 = st.number_input(
            f"Argument 2 — Test {i + 1}",
            value=3 if i == 0 else 0,
            key=f"arg2_{i}",
        )

    with col3:
        expected = st.number_input(
            f"Expected output — Test {i + 1}",
            value=6 if i == 0 else 0,
            key=f"expected_{i}",
        )

    test_cases.append({
        "args": [arg1, arg2],
        "expected": expected,
    })


if st.button("Run Multi-Agent Repair", key="run_multi_agent_repair"):
    if not function_name.strip():
        st.warning("Enter a function name.")
    else:
        coordinator = Coordinator()

        result = coordinator.run(
            source_code=source_code,
            function_name=function_name.strip(),
            test_cases=test_cases,
        )

        # Save run to session history
        st.session_state.repair_history.append({
            "function": function_name.strip(),
            "original_code": source_code,
            "repair": result.get("repair"),
            "validation": result.get("validation"),
            "success": result.get("success", False),
            "stage": result.get("stage", "unknown"),
        })

        st.subheader("Analysis")
        st.json(result.get("analysis", {}))

        st.subheader("Repair Proposal")
        repair = result.get("repair")

        if repair and repair.get("success"):
            st.write("Strategy:", repair.get("strategy"))
            st.write("Message:", repair.get("message"))
            st.code(
                repair.get("code", ""),
                language="python",
            )
        elif repair:
            st.warning(
                repair.get("message", "No repair was proposed.")
            )
        else:
            st.info("No repair was proposed.")

        st.subheader("Validation")
        validation = result.get("validation")

        if validation:
            st.write(validation.get("message", ""))
            st.json(validation.get("results", []))
        else:
            st.info("Validation was not completed.")

        if result.get("success"):
            st.success("All validation tests passed!")
        else:
            st.warning(
                "Workflow did not complete successfully. "
                f"Stage: {result.get('stage', 'unknown')}"
            )


# -------------------- REPAIR HISTORY --------------------

st.divider()
st.header("Repair History")

if st.session_state.repair_history:
    for index, item in enumerate(
        reversed(st.session_state.repair_history),
        start=1,
    ):
        with st.expander(
            f"Run {index} — "
            f"{'Passed' if item['success'] else 'Not passed'}"
        ):
            st.write("Function:", item["function"])
            st.write("Stage:", item["stage"])

            st.subheader("Original code")
            st.code(item["original_code"], language="python")

            if item["repair"]:
                st.subheader("Repair proposal")
                st.json(item["repair"])

            if item["validation"]:
                st.subheader("Validation results")
                st.json(item["validation"])
else:
    st.info("No multi-agent runs recorded yet.")
