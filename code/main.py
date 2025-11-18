# src/main.py
import os
from typing import Dict

from src.auth.github_app import GitHubAppAuth
from src.analysis.code_analyzer import PythonAnalyzer
from src.agent.clone_manager import CloneManager
from src.agent.refactor_engine import RefactorEngine


class CodeRefactorApp:
    """
    CodeRefactorApp is the main application class for orchestrating
    GitHub repository authentication, cloning, code analysis, and
    automated refactoring. It provides an interface to process
    repositories and apply suggested code improvements.
    """
    def __init__(self):
        self.auth = GitHubAppAuth()
        self.analyzer = None
        self.clone_manager = None
        self.refactor_engine = RefactorEngine()


    def initialize(self) -> bool:
        """Initialize the application"""
        if not self.auth.authenticate():
            return False

        self.analyzer = PythonAnalyzer(self.auth)
        self.clone_manager = CloneManager(self.auth.client)
        return True

    def process_repository(self, owner: str, repo_name: str, branch: str = 'main') -> Dict:
        """Process a repository and return results"""
        if not self.analyzer or not self.clone_manager:
            return {'status': 'error', 'message': 'Application not initialized. Call initialize() first.'}

        try:
            repo_path = self.clone_manager.clone_repository(owner, repo_name, branch)
            if not repo_path:
                return {'status': 'error', 'message': 'Clone failed'}

            suggestions = self.analyzer.analyze(repo_path)

            if suggestions:
                # Note: Current implementation assumes suggestions are intended for 'main.py'.
                # If PythonAnalyzer can produce suggestions for multiple files, this logic
                # needs to be generalized to iterate over suggestions per file.
                self.refactor_engine.apply_suggestions(
                    os.path.join(repo_path, 'main.py'),
                    suggestions
                )

            return {'status': 'success', 'suggestions': suggestions}
        except Exception as e:
            # For production, consider logging the full traceback and catching more specific exceptions.
            return {'status': 'error', 'message': f"An unexpected error occurred: {type(e).__name__} - {str(e)}"}
