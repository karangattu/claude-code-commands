import os
import unittest
import yaml

class TestReusableWorkflow(unittest.TestCase):
    def setUp(self):
        self.workflows_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            ".github",
            "workflows"
        )

    def load_workflow(self, filename):
        filepath = os.path.join(self.workflows_dir, filename)
        self.assertTrue(os.path.exists(filepath), f"{filename} does not exist")
        with open(filepath, "r") as f:
            return yaml.safe_load(f)

    def test_reusable_workflow_is_valid(self):
        data = self.load_workflow("commands.yml")

        self.assertIsNotNone(data)
        self.assertTrue(True in data or "on" in data)
        self.assertIn("jobs", data)
        self.assertEqual(
            {"triage", "reprex", "duplicate", "issue-fix"},
            set(data["jobs"].keys())
        )

    def _get_on(self, data):
        return data.get(True) or data.get("on")

    def test_reusable_workflow_declares_inputs(self):
        data = self.load_workflow("commands.yml")
        inputs = self._get_on(data)["workflow_call"]["inputs"]

        self.assertIn("command", inputs)
        self.assertEqual("choice", inputs["command"]["type"])
        self.assertEqual(
            {"triage", "reprex", "duplicate", "issue-fix"},
            set(inputs["command"]["options"])
        )
        self.assertIn("issue_number", inputs)
        self.assertIn("comment_id", inputs)
        self.assertIn("prompt_suffix", inputs)
        self.assertIn("model", inputs)
        self.assertIn("max_turns", inputs)
        self.assertIn("runner", inputs)

    def test_reusable_workflow_declares_secrets(self):
        data = self.load_workflow("commands.yml")
        secrets = self._get_on(data)["workflow_call"]["secrets"]

        self.assertIn("anthropic_api_key", secrets)
        self.assertIn("claude_code_oauth_token", secrets)
        self.assertIn("app_id", secrets)
        self.assertIn("app_private_key", secrets)

        for name, secret in secrets.items():
            self.assertFalse(secret.get("required", False),
                             f"secret {name} should not be required")

    def test_report_only_jobs_have_limited_permissions_and_tools(self):
        data = self.load_workflow("commands.yml")

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

    def test_issue_fix_job_has_write_permissions_and_tools(self):
        data = self.load_workflow("commands.yml")
        job = data["jobs"]["issue-fix"]

        self.assertEqual("write", job["permissions"]["contents"])
        self.assertEqual("write", job["permissions"]["issues"])
        self.assertEqual("write", job["permissions"]["pull-requests"])
        self.assertIn("timeout-minutes", job)
        self.assertIn("concurrency", job)

        claude_step = next(step for step in job["steps"] if step.get("uses", "").startswith("anthropics/"))
        self.assertIn('--allowedTools "Bash,Read,Write,Edit"', claude_step["with"]["claude_args"])

    def test_job_conditions_match_command_input(self):
        data = self.load_workflow("commands.yml")

        for command, job in data["jobs"].items():
            self.assertIn(f"inputs.command == '{command}'", job["if"])

    def test_jobs_use_inputs_not_github_event(self):
        data = self.load_workflow("commands.yml")

        for command, job in data["jobs"].items():
            for step in job["steps"]:
                if "with" in step and "prompt" in step["with"]:
                    self.assertIn("inputs.issue_number", step["with"]["prompt"])
                    self.assertNotIn("github.event.issue.number", step["with"]["prompt"])

    def test_caller_workflow_exists(self):
        filepath = os.path.join(self.workflows_dir, "claude-commands.yml")
        self.assertTrue(os.path.exists(filepath))

        data = self.load_workflow("claude-commands.yml")
        self.assertTrue(True in data or "on" in data)
        on_block = self._get_on(data)
        self.assertIn("issue_comment", on_block)
        self.assertIn("jobs", data)
        self.assertIn("parse", data["jobs"])

    def test_caller_dispatches_to_reusable(self):
        data = self.load_workflow("claude-commands.yml")

        for command in ["triage", "reprex", "duplicate", "issue-fix"]:
            job = data["jobs"][command]
            self.assertIn("uses", job)
            self.assertIn("commands.yml", job["uses"])
            self.assertIn("secrets", job)

    def test_caller_does_not_use_secrets_inherit(self):
        data = self.load_workflow("claude-commands.yml")

        for command in ["triage", "reprex", "duplicate", "issue-fix"]:
            job = data["jobs"][command]
            self.assertNotEqual("inherit", job.get("secrets"))

    def test_example_caller_exists(self):
        filepath = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "examples",
            "caller.yml"
        )
        self.assertTrue(os.path.exists(filepath))

        with open(filepath, "r") as f:
            data = yaml.safe_load(f)

        self.assertTrue(True in data or "on" in data)
        on_block = data.get(True) or data.get("on")
        self.assertIn("issue_comment", on_block)
        self.assertIn("jobs", data)

        for command in ["triage", "reprex", "duplicate", "issue-fix"]:
            job = data["jobs"][command]
            self.assertIn("your-org/claude-code-commands", job["uses"])
            self.assertNotEqual("inherit", job.get("secrets"))


if __name__ == "__main__":
    unittest.main()
