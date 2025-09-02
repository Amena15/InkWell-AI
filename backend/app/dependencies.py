from fastapi import Depends
from typing import Generator
from app.services.github_service import GitHubService

def get_github_service() -> Generator[GitHubService, None, None]:
    """Dependency that provides GitHubService instance."""
    github_service = GitHubService()
    try:
        yield github_service
    finally:
        # Cleanup if needed
        pass
