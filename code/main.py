# src/main.py
import os
from typing import Dict

from src.auth.github_app import GitHubAppAuth
from src.analysis.code_analyzer import PythonAnalyzer, AnalysisError
from src.agent.clone_manager import CloneManager, CloneError
from src.agent.refactor_engine import RefactorEngine, RefactorError


class CodeRefactorApp:
    """App that integrates GitHub authentication, code analysis, repository cloning, and refactoring capabilities."""
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
        if self.analyzer is None or self.clone_manager is None:
            raise RuntimeError("CodeRefactorApp is not initialized. Call .initialize() first.")
        try:
            repo_path = self.clone_manager.clone_repository(owner, repo_name, branch)
            if not repo_path:
                return {'status': 'error', 'message': 'Clone failed'}

            suggestions = self.analyzer.analyze(repo_path)

            if suggestions:
                for file_relative_path, file_suggestions in suggestions.items():
                    target_file_path = os.path.join(repo_path, file_relative_path)
                    self.refactor_engine.apply_suggestions(target_file_path, file_suggestions)

            return {'status': 'success', 'suggestions': suggestions}
        except (CloneError, AnalysisError, RefactorError) as e:
            return {'status': 'error', 'message': str(e)}