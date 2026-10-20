
from agents.coordinator import Coordinator

test_cases = [
    {"args": [2, 3], "expected": 6},
    {"args": [4, 5], "expected": 20},
    {"args": [0, 7], "expected": 0},
]

source_code = """
def multiply(a, b):
    return a + b
"""

coordinator = Coordinator()
result = coordinator.run(
    source_code,
    "multiply",
    test_cases,
)

print("Success:", result["success"])
print("Stage:", result["stage"])
print("Repair:", result["repair"])
print("Validation:", result["validation"])
