"""
Google Tasks Service Connect Core
Interacts natively with task tracking collections and item state updates.
"""

from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from src.api.google_auth import GoogleAuthManager
from src.utils.logger import get_logger

logger = get_logger()

class TasksAPIClient:
    """Drives workspace reminder tracking mechanics directly over Google Tasks API schemas."""
    
    def __init__(self):
        self.auth_manager = GoogleAuthManager()
        self._service = None

    @property
    def service(self):
        if self._service is None:
            creds = self.auth_manager.get_credentials()
            self._service = build('tasks', 'v1', credentials=creds)
        return self._service

    def _get_default_list_id(self) -> str:
        """Resolves target fallback identity pointing to active user primary collections."""
        lists = self.service.tasklists().list().execute()
        items = lists.get('items', [])
        return items[0]['id'] if items else "@default"

    def list_pending_tasks(self, max_results: int = 20) -> List[Dict[str, Any]]:
        """Queries list trackers containing outstanding uncompleted action items."""
        try:
            list_id = self._get_default_list_id()
            results = self.service.tasks().list(
                tasklist=list_id, maxResults=max_results, showCompleted=False
            ).execute()
            
            tasks = results.get('items', [])
            logger.info(f"Discovered {len(tasks)} outstanding task list entries.")
            return tasks
        except Exception as e:
            logger.error(f"Failed pulling assignment arrays from Tasks API: {e}")
            return []

    def create_task(self, title: str, notes: Optional[str] = None, due_iso: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Appends fresh structured action rows back down to your tracking metrics."""
        try:
            list_id = self._get_default_list_id()
            task_body = {'title': title, 'notes': notes or ''}
            if due_iso:
                task_body['due'] = due_iso  # Expects RFC3339 formatted text timestamps
                
            created_task = self.service.tasks().insert(
                tasklist=list_id, body=task_body
            ).execute()
            
            logger.info(f"Recorded fresh task tracking node: {created_task.get('id')}")
            return created_task
        except Exception as e:
            logger.error(f"Failed creating tracking entries inside Google Tasks: {e}")
            return None