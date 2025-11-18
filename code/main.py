# src/main.py
from src.auth.github_app import GitHubAppAuth
from src.analysis.code_analyzer import PythonAnalyzer
from src.agent.clone_manager import CloneManager
from src.agent.refactor_engine import RefactorEngine
from src.utils.json_utils import JSONUtils

class CodeRefactorApp:
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
        try:
            # Clone repository
            repo_path = self.clone_manager.clone_repository(owner, repo_name, branch)
            if not repo_path:
                return {'status': 'error', 'message': 'Clone failed'}
            
            # Analyze code
            suggestions = self.analyzer.analyze(repo_path)
            
            # Apply refactorings
            if suggestions:
                self.refactor_engine.apply_suggestions(
                    os.path.join(repo_path, 'main.py'),
                    suggestions
                )
            
            return {'status': 'success', 'suggestions': suggestions}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}