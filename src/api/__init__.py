"""API Integrations and Singleton Connection Clients for external services"""

from .google_auth import GoogleAuthManager
from .gemini_client import GeminiClient
from .gmail_client import GmailAPIClient
from .calendar_client import CalendarAPIClient
from .tasks_client import TasksAPIClient

__all__ = [
    "GoogleAuthManager",
    "GeminiClient",
    "GmailAPIClient",
    "CalendarAPIClient",
    "TasksAPIClient"
]