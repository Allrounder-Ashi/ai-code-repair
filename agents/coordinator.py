

from agents.analyzer_agent import AnalyzerAgent
from agents.repair_agent import RepairAgent
from agents.validator_agent import ValidatorAgent


class Coordinator:
    """Coordinates analysis, repair, and validation."""

    def __init__(self):
        self.analyzer = AnalyzerAgent()
        self.repairer = RepairAgent()
        self.validator = ValidatorAgent()

    def run(self, source_code, function_name, test_cases):
        analysis = self.analyzer.run(source_code)

        if not analysis["valid"]:
            return {
                "success": False,
                "stage": "analysis",
                "analysis": analysis,
                "repair": None,
                "validation": None,
            }

        repair = self.repairer.run(source_code, function_name)

        if not repair["success"]:
            return {
                "success": False,
                "stage": "repair",
                "analysis": analysis,
                "repair": repair,
                "validation": None,
            }

        validation = self.validator.run(
            repair["code"],
            function_name,
            test_cases,
        )

        return {
            "success": validation["passed"] is True,
            "stage": "complete",
            "analysis": analysis,
            "repair": repair,
            "validation": validation,
        }
