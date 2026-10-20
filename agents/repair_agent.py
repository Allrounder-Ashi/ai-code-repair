

from repair import repair_code
from logic_repair import propose_logic_repair


class RepairAgent:
    """Coordinates supported syntax and logic repair strategies."""

    def run(
        self,
        source_code: str,
        function_name: str = "multiply",
    ) -> dict:

        syntax_result = repair_code(source_code)

        if syntax_result["success"]:
            return {
                "success": True,
                "code": syntax_result["repaired_code"],
                "strategy": "syntax_repair",
                "message": syntax_result["changes"],
            }

        logic_result = propose_logic_repair(
            source_code,
            function_name,
        )

        if logic_result["success"]:
            return {
                "success": True,
                "code": logic_result["repaired_code"],
                "strategy": "logic_repair",
                "message": logic_result["message"],
            }

        return {
            "success": False,
            "code": source_code,
            "strategy": None,
            "message": "No supported repair was found.",
        }
