
import unittest
from unittest.mock import patch, MagicMock

# Import functions from visualizer.py
from visualizer import (
    parse_config,
    get_commits,
    get_commit_parents,
    generate_mermaid_code,
    output_result
)

class TestGitVisualizer(unittest.TestCase):

    def test_parse_config(self):
        with patch("builtins.open", unittest.mock.mock_open(read_data="graphviz_path,repo_path,output_path,target_file")):
            graphviz_path, repo_path, output_path, target_file = parse_config("config.csv")
            self.assertEqual(graphviz_path, "graphviz_path")
            self.assertEqual(repo_path, "repo_path")
            self.assertEqual(output_path, "output_path")
            self.assertEqual(target_file, "target_file")

    @patch("subprocess.run")
    def test_get_commits(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="commit1\\ncommit2\\ncommit3")
        commits = get_commits("repo_path", "target_file")
        self.assertEqual(commits, ["commit1\\ncommit2\\ncommit3"])  # Expected in chronological order

    @patch("subprocess.run")
    def test_get_commit_parents(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="commit1 parent1 parent2")
        parents = get_commit_parents("repo_path", "commit1")
        self.assertEqual(parents, ["parent1", "parent2"])

    def test_generate_mermaid_code(self):
        with patch("visualizer.get_commit_parents") as mock_get_commit_parents:
            mock_get_commit_parents.side_effect = lambda repo_path, commit: {
                "commit3": ["commit2"],
                "commit2": ["commit1"],
                "commit1": []
            }[commit]
            mermaid_code = generate_mermaid_code(["commit1", "commit2", "commit3"], "repo_path")
            expected_code = "graph TD\\ncommit1 --> commit2\\ncommit2 --> commit3"
            self.assertIn(expected_code, mermaid_code)

    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    def test_output_result(self, mock_open):
        output_result("graph TD\\nA-->B", "output.md")
        mock_open.assert_called_once_with("output.md", "w")
        mock_open().write.assert_called_once_with("```mermaid\\ngraph TD\\nA-->B\\n```")

if __name__ == "__main__":
    unittest.main()

