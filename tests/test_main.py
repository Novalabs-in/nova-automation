import os
import pytest
from unittest.mock import MagicMock, patch
from main import RepositoryAutomator

def test_repositoryautomator_instantiation():
    # Verify that the class RepositoryAutomator is inspectable and loadable
    automator = RepositoryAutomator()
    assert automator is not None

def test_check_branch_naming_valid():
    automator = RepositoryAutomator()
    with patch.object(automator, 'get_current_branch', return_value="feature/add-tests"):
        assert automator.check_branch_naming() is True

    with patch.object(automator, 'get_current_branch', return_value="main"):
        assert automator.check_branch_naming() is True

    with patch.object(automator, 'get_current_branch', return_value="patch-123"):
        assert automator.check_branch_naming() is True

def test_check_branch_naming_invalid():
    automator = RepositoryAutomator()
    with patch.object(automator, 'get_current_branch', return_value="my_custom_branch"):
        assert automator.check_branch_naming() is False

    with patch.object(automator, 'get_current_branch', return_value="feature"):
        # Matches "^feature/.*", so "feature" alone doesn't match
        assert automator.check_branch_naming() is False

def test_check_branch_naming_no_git():
    automator = RepositoryAutomator()
    with patch.object(automator, 'get_current_branch', return_value=None):
        assert automator.check_branch_naming() is True

def test_lint_python_files_valid(tmp_path):
    # Setup valid python file in temp directory
    valid_file = tmp_path / "valid.py"
    valid_file.write_text("def my_func():\n    return 42\n", encoding="utf-8")
    
    automator = RepositoryAutomator()
    assert automator.lint_python_files(repo_path=str(tmp_path)) is True

def test_lint_python_files_invalid(tmp_path):
    # Setup invalid python file in temp directory
    invalid_file = tmp_path / "invalid.py"
    invalid_file.write_text("def my_func(\n    return 42\n", encoding="utf-8") # SyntaxError
    
    automator = RepositoryAutomator()
    assert automator.lint_python_files(repo_path=str(tmp_path)) is False

def test_check_dependencies_no_file(tmp_path):
    automator = RepositoryAutomator()
    assert automator.check_dependencies(repo_path=str(tmp_path)) is True

def test_check_dependencies_valid(tmp_path):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("pytest\n# some comment\n", encoding="utf-8")
    
    automator = RepositoryAutomator()
    # pytest is installed in this test environment
    assert automator.check_dependencies(repo_path=str(tmp_path)) is True

def test_check_dependencies_invalid(tmp_path):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("this-package-does-not-exist-at-all-xyz>=1.0.0\n", encoding="utf-8")
    
    automator = RepositoryAutomator()
    assert automator.check_dependencies(repo_path=str(tmp_path)) is False

def test_automate_checks_all_pass(tmp_path):
    automator = RepositoryAutomator()
    with patch.object(automator, 'check_branch_naming', return_value=True), \
         patch.object(automator, 'lint_python_files', return_value=True), \
         patch.object(automator, 'check_dependencies', return_value=True):
        assert automator.automate_checks(repo_path=str(tmp_path)) is True

def test_automate_checks_some_fail(tmp_path):
    automator = RepositoryAutomator()
    with patch.object(automator, 'check_branch_naming', return_value=True), \
         patch.object(automator, 'lint_python_files', return_value=False), \
         patch.object(automator, 'check_dependencies', return_value=True):
        assert automator.automate_checks(repo_path=str(tmp_path)) is False
