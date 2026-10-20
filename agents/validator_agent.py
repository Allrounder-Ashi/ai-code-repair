
from validator import validate_function


class ValidatorAgent:
    """Validates proposed code repairs using test cases."""

    def run(
        self,
        source_code: str,
        function_name: str,
        test_cases: list[dict],
    ) -> dict:
        return validate_function(
            source_code,
            function_name,
            test_cases,
        )
