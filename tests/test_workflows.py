import os
import unittest
import yaml

class TestGitHubWorkflows(unittest.TestCase):
    def setUp(self):
        self.workflows_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            ".github",
            "workflows"
        )
        self.required_files = ["triage.yml", "issue-fix.yml", "duplicate.yml", "reprex.yml"]

    def test_workflow_files_exist_and_are_valid(self):
        for filename in self.required_files:
            filepath = os.path.join(self.workflows_dir, filename)
            self.assertTrue(os.path.exists(filepath), f"{filename} does not exist")

            with open(filepath, "r") as f:
                data = yaml.safe_load(f)

            self.assertIsNotNone(data, f"{filename} is empty")
            self.assertTrue(True in data or "on" in data, f"{filename} is missing 'on' trigger")
            self.assertIn("jobs", data, f"{filename} is missing 'jobs' section")

if __name__ == "__main__":
    unittest.main()
