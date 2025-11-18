# src/main.py
import os
from typing import Dict
from collections import defaultdict

from src.auth.github_app import GitHubAppAuth
from src.analysis.code_analyzer import PythonAnalyzer
from src.agent.clone_manager import CloneManager
from src.agent.refactor_engine import RefactorEngine
from src.utils.json_utils import JSONUtils

class CodeRefactorApp:
    """
    Orchestrates the process of authenticating with GitHub, cloning repositories,
    analyzing code for refactoring opportunities, and applying refactorings.
    It leverages various components like GitHubAppAuth, PythonAnalyzer,
    CloneManager, and RefactorEngine to provide an automated code refactoring workflow.
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
        """
        Processes a specified GitHub repository by cloning it, analyzing its code,
        and applying suggested refactorings.

        Args:
            owner (str): The owner of the GitHub repository.
            repo_name (str): The name of the repository.
            branch (str, optional): The branch to process. Defaults to 'main'.

        Returns:
            Dict: A dictionary indicating the processing status and results.
                  On success, returns {'status': 'success', 'suggestions': List[Dict]}.
                  On error, returns {'status': 'error', 'message': str}.
        """
        try:
            # Clone repository
            repo_path = self.clone_manager.clone_repository(owner, repo_name, branch)
            if not repo_path:
                return {'status': 'error', 'message': 'Clone failed'}
            
            # Analyze code
            all_suggestions = self.analyzer.analyze(repo_path)
            
            # Group suggestions by file path to apply refactorings dynamically
            suggestions_by_file = defaultdict(list)
            if all_suggestions:
                for suggestion in all_suggestions:
                    # Assuming each suggestion object contains a 'file_path' relative to repo_path
                    if 'file_path' in suggestion:
                        file_abs_path = os.path.join(repo_path, suggestion['file_path'])
                        suggestions_by_file[file_abs_path].append(suggestion)
            
            # Apply refactorings
            if suggestions_by_file:
                for file_path, suggestions_for_file in suggestions_by_file.items():
                    self.refactor_engine.apply_suggestions(file_path, suggestions_for_file)
            
            return {'status': 'success', 'suggestions': all_suggestions}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}