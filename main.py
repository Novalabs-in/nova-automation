import os
import sys
import ast
import subprocess
import re

class RepositoryAutomator:
    """
    Nova Automation Utility
    Maintains clean, standardized, and repeatable workspace configurations.
    """
    def get_current_branch(self, repo_path="."):
        # 1. Attempt to read from .git/HEAD directly to avoid subprocess overhead
        git_dir = os.path.join(repo_path, ".git")
        head_file = os.path.join(git_dir, "HEAD")
        if os.path.isdir(git_dir) and os.path.isfile(head_file):
            try:
                with open(head_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if content.startswith("ref:"):
                    return content.split("ref:")[-1].strip().split("/")[-1]
                return content  # Detached HEAD SHA
            except Exception:
                pass
        
        # 2. Fall back to calling git CLI
        try:
            res = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=repo_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )
            return res.stdout.strip()
        except Exception:
            return None

    def check_branch_naming(self, repo_path="."):
        branch = self.get_current_branch(repo_path)
        if not branch:
            # Not in a git repo or git is not initialized
            print("⚠ Branch standards: Skipping (No git repository or HEAD ref detected).")
            return True
        
        # Standard prefixes: main, master, feature/*, bugfix/*, hotfix/*, release/*, patch-*
        allowed_patterns = [
            r"^main$",
            r"^master$",
            r"^feature/.*",
            r"^bugfix/.*",
            r"^hotfix/.*",
            r"^release/.*",
            r"^patch-.*"
        ]
        
        for pattern in allowed_patterns:
            if re.match(pattern, branch):
                print(f"✔ Branch standards passed (Branch name: '{branch}').")
                return True
                
        print(f"✘ Branch standards failed: Branch name '{branch}' does not match standard naming conventions.")
        print("  Expected prefixes: feature/, bugfix/, hotfix/, release/, patch-, main, master")
        return False

    def lint_python_files(self, repo_path="."):
        print("--- Linting Python Files ---")
        success = True
        py_files_checked = 0
        
        for root, dirs, files in os.walk(repo_path):
            # Skip hidden and dependency directories
            dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("venv", ".venv", "node_modules", "__pycache__")]
            
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    py_files_checked += 1
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        ast.parse(content, filename=file_path)
                    except SyntaxError as e:
                        print(f"✘ Linting failed: SyntaxError in {file_path}:{e.lineno} - {e.msg}")
                        success = False
                    except Exception as e:
                        print(f"⚠ Linting warning: Could not read {file_path} - {e}")
        
        if py_files_checked == 0:
            print("✔ Lint rules verified: No Python files found to lint.")
        elif success:
            print(f"✔ Lint rules verified: All {py_files_checked} Python files passed syntax check.")
        
        return success

    def check_dependencies(self, repo_path="."):
        req_file = os.path.join(repo_path, "requirements.txt")
        if not os.path.isfile(req_file):
            print("✔ Dependencies verified: No requirements.txt found.")
            return True
            
        print("--- Verifying Dependencies ---")
        success = True
        
        try:
            with open(req_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except Exception as e:
            print(f"✘ Dependencies failed: Could not read requirements.txt - {e}")
            return False
            
        for line in lines:
            line = line.strip()
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            
            # Simple package name extractor (e.g. requests>=2.31.0 -> requests)
            # Match package name at beginning, ignoring specifiers
            match = re.match(r"^([a-zA-Z0-9_\-]+)", line)
            if not match:
                continue
                
            pkg_name = match.group(1).replace("-", "_")
            try:
                # Try to import the package
                __import__(pkg_name)
            except ImportError:
                # Let's check using importlib.metadata if present (Python 3.8+)
                try:
                    from importlib.metadata import version
                    version(pkg_name.replace("_", "-"))
                except Exception:
                    print(f"✘ Dependencies check failed: Package '{line}' is not installed in the current environment.")
                    success = False
                    
        if success:
            print("✔ Dependencies verified: All defined packages are installed.")
        return success

    def automate_checks(self, repo_path="."):
        print("--- Running Nova Repo Automation Checks ---")
        branch_ok = self.check_branch_naming(repo_path)
        lint_ok = self.lint_python_files(repo_path)
        deps_ok = self.check_dependencies(repo_path)
        
        print("\n--- Final Summary ---")
        if branch_ok and lint_ok and deps_ok:
            print("✔ All checks passed successfully.")
            return True
        else:
            print("✘ Some repository checks failed. Please fix the issues reported above.")
            return False

if __name__ == "__main__":
    automator = RepositoryAutomator()
    sys.exit(0 if automator.automate_checks() else 1)
