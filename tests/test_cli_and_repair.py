from pathlib import Path
import subprocess
import sys
import unittest


PROJECT_PATH = Path(__file__).resolve().parents[1]
FIXTURE_PATH = PROJECT_PATH / "tests" / "fixtures"


class SignalGardenSmokeTests(unittest.TestCase):
    def run_command(self, args, cwd=PROJECT_PATH):
        return subprocess.run(
            [sys.executable, *args],
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_validate_accepts_sample_vault(self):
        result = self.run_command(
            [
                "signal_garden.py",
                "validate",
                "--vault",
                str(FIXTURE_PATH / "sample_vault"),
                "--config",
                str(FIXTURE_PATH / "sample_areas.json"),
            ]
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Failures: 0", result.stdout)

    def test_repair_source_frontmatter_reports_needed_repairs(self):
        result = self.run_command(
            [
                "signal_garden.py",
                "repair",
                "--vault",
                str(FIXTURE_PATH / "repair_vault"),
            ]
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Needs Repair.md: would repair", result.stdout)
        self.assertIn("source frontmatter: would repair 1 note(s)", result.stdout)


if __name__ == "__main__":
    unittest.main()
