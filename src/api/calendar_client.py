"""
Google Calendar Service Client Layer
Manages agenda sweeps, schedule timelines, and event creation parameters.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from googleapiclient.discovery import build
from src.api.google_auth import GoogleAuthManager
from src.utils.logger import get_logger

logger = get_logger()

class CalendarAPIClient:
    """Manages raw resource operations interacting directly with Google Calendar data schemas."""
    
    def __init__(self):
        self.auth_manager = GoogleAuthManager()
        self._service = None

    @property
    def service(self):
        if self._service is None:
            creds = self.auth_manager.get_credentials()
            self._service = build('calendar', 'v3', credentials=creds)
        return self._service

    def get_upcoming_events(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """Pulls list index summaries tracks following chronologically sorted timeline items."""
        try:
            now_iso = datetime.utcnow().isoformat() + 'Z'  # Requires absolute UTC timestamps
            events_result = self.service.events().list(
                calendarId='primary', timeMin=now_iso,
                maxResults=max_results, singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            logger.info(f"Retrieved {len(events)} upcoming calendar schedule items successfully.")
            return events
        except Exception as e:
            logger.error(f"Failed querying timeline views from Calendar API: {e}")
            return []

    def create_event(self, summary: str, start_iso: str, end_iso: str, description: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Appends a new structural appointment entry to your calendar coordinates."""
        try:
            event_body = {
                'summary': summary,
                'description': description or '',
                'start': {'dateTime': start_iso, 'timeZone': 'UTC'},
                'end': {'dateTime': end_iso, 'timeZone': 'UTC'}
            }
            created_event = self.service.events().insert(
                calendarId='primary', body=event_body
            ).execute()
            
            logger.info(f"Successfully recorded calendar event! Identifier code: {created_event.get('id')}")
            return created_event
        except Exception as e:
            logger.error(f"Failed injecting mutation event into Google Calendar: {e}")
            return None