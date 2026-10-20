
import ast


def repair_code(source_code: str) -> dict:
    """
    Repair a small set of common Python syntax errors.
    This is a rule-based baseline, not a general AI repair engine.
    """

    candidates = [
        # Common mistake: missing colon after a function definition
        (
            lambda line: line.lstrip().startswith("def ")
            and line.rstrip().endswith(")")
            and not line.rstrip().endswith(":"),
            lambda line: line.rstrip() + ":",
            "Added a missing colon to a function definition.",
        ),
        # Common mistake: missing colon after if/for/while
        (
            lambda line: line.lstrip().startswith(("if ", "for ", "while "))
            and line.rstrip().endswith((")", "True", "False"))
            and not line.rstrip().endswith(":"),
            lambda line: line.rstrip() + ":",
            "Added a missing colon to a control statement.",
        ),
    ]

    lines = source_code.splitlines()
    changes = []

    for index, line in enumerate(lines):
        for matches, fix, explanation in candidates:
            if matches(line):
                original = lines[index]
                lines[index] = fix(line)
                candidate = "\n".join(lines)

                try:
                    ast.parse(candidate)
                    changes.append(explanation)
                    return {
                        "success": True,
                        "repaired_code": candidate,
                        "changes": changes,
                    }
                except SyntaxError:
                    lines[index] = original

    return {
        "success": False,
        "repaired_code": source_code,
        "changes": [],
    }
