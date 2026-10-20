
import ast


def propose_logic_repair(source_code: str, function_name: str) -> dict:
    """
    Propose a narrowly targeted arithmetic-operator repair.
    Supports simple return expressions using + or *.
    """
    try:
        tree = ast.parse(source_code)
    except SyntaxError as error:
        return {
            "success": False,
            "repaired_code": source_code,
            "message": f"Cannot repair invalid syntax: {error.msg}",
        }

    target = next(
        (
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and node.name == function_name
        ),
        None,
    )

    if target is None:
        return {
            "success": False,
            "repaired_code": source_code,
            "message": f"Function '{function_name}' was not found.",
        }

    if len(target.body) != 1 or not isinstance(target.body[0], ast.Return):
        return {
            "success": False,
            "repaired_code": source_code,
            "message": "This repair strategy supports only a simple return expression.",
        }

    expression = target.body[0].value

    if not isinstance(expression, ast.BinOp):
        return {
            "success": False,
            "repaired_code": source_code,
            "message": "No supported arithmetic expression was found.",
        }

    if isinstance(expression.op, ast.Add):
        old_operator, new_operator = "+", "*"
    elif isinstance(expression.op, ast.Mult):
        old_operator, new_operator = "*", "+"
    else:
        return {
            "success": False,
            "repaired_code": source_code,
            "message": "No supported operator replacement was found.",
        }

    lines = source_code.splitlines()
    start = target.lineno - 1
    end = target.end_lineno
    replaced = False

    for index in range(start, end):
        line = lines[index]
        if old_operator in line and "return" in line:
            lines[index] = line.replace(old_operator, new_operator, 1)
            replaced = True
            break

    if not replaced:
        return {
            "success": False,
            "repaired_code": source_code,
            "message": "Could not safely locate the operator in source text.",
        }

    candidate = "\n".join(lines)

    try:
        ast.parse(candidate)
    except SyntaxError:
        return {
            "success": False,
            "repaired_code": source_code,
            "message": "The proposed repair did not pass syntax validation.",
        }

    return {
        "success": True,
        "repaired_code": candidate,
        "message": f"Proposed replacing '{old_operator}' with '{new_operator}'.",
    }

 