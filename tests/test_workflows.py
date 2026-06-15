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
        self.workflow_file = "commands.yml"

    def load_workflow(self):
        filepath = os.path.join(self.workflows_dir, self.workflow_file)
        self.assertTrue(os.path.exists(filepath), f"{self.workflow_file} does not exist")

        with open(filepath, "r") as f:
            return yaml.safe_load(f)

    def test_consolidated_command_workflow_is_valid(self):
        data = self.load_workflow()

        self.assertIsNotNone(data, f"{self.workflow_file} is empty")
        self.assertTrue(True in data or "on" in data, f"{self.workflow_file} is missing 'on' trigger")
        self.assertIn("jobs", data, f"{self.workflow_file} is missing 'jobs' section")
        self.assertEqual(
            {"triage", "reprex", "duplicate", "issue-fix"},
            set(data["jobs"].keys())
        )

    def test_issue_commands_are_defined_in_one_workflow(self):
        workflow_files = sorted(
            filename for filename in os.listdir(self.workflows_dir)
            if filename.endswith((".yml", ".yaml"))
        )

        self.assertEqual([self.workflow_file], workflow_files)

    def test_report_only_jobs_have_limited_permissions_and_tools(self):
        data = self.load_workflow()

        for job_name in ["triage", "reprex", "duplicate"]:
            job = data["jobs"][job_name]
            self.assertEqual("read", job["permissions"]["contents"])
            self.assertEqual("write", job["permissions"]["issues"])
            self.assertNotIn("pull-requests", job["permissions"])
            self.assertIn("timeout-minutes", job)
            self.assertIn("concurrency", job)

            claude_step = next(step for step in job["steps"] if step.get("uses", "").startswith("anthropics/"))
            self.assertIn('--allowedTools "Bash,Read"', claude_step["with"]["claude_args"])
            self.assertNotIn("Write", claude_step["with"]["claude_args"])
            self.assertNotIn("Edit", claude_step["with"]["claude_args"])

    def test_issue_fix_job_has_write_permissions_and_test_command(self):
        data = self.load_workflow()
        job = data["jobs"]["issue-fix"]

        self.assertEqual("write", job["permissions"]["contents"])
        self.assertEqual("write", job["permissions"]["issues"])
        self.assertEqual("write", job["permissions"]["pull-requests"])
        self.assertIn("timeout-minutes", job)
        self.assertIn("concurrency", job)

        claude_step = next(step for step in job["steps"] if step.get("uses", "").startswith("anthropics/"))
        self.assertIn('--allowedTools "Bash,Read,Write,Edit"', claude_step["with"]["claude_args"])
        self.assertIn("python3 -m unittest discover -s tests", claude_step["with"]["prompt"])

    def test_command_filters_do_not_match_prefixed_commands(self):
        data = self.load_workflow()

        for command, job in data["jobs"].items():
            expression = job["if"]
            slash_command = f"/{command}"
            self.assertIn(f"github.event.comment.body == '{slash_command}'", expression)
            self.assertIn(f"startsWith(github.event.comment.body, '{slash_command} ')", expression)
            self.assertNotIn(f"startsWith(github.event.comment.body, '{slash_command}')", expression)

if __name__ == "__main__":
    unittest.main()
