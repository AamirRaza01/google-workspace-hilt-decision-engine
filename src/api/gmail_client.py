"""
Gmail API Native Client Wrapper
Handles search queries, live inbox sweeps, message data hydration, and text extraction.
"""

import base64
from typing import List, Dict, Any, Optional
from googleapiclient.discovery import build
from src.api.google_auth import GoogleAuthManager
from src.utils.logger import get_logger

logger = get_logger()

class GmailAPIClient:
    """Communicator interface interacting directly with user Gmail mailboxes."""
    
    def __init__(self):
        self.auth_manager = GoogleAuthManager()
        self._service = None

    @property
    def service(self):
        """Lazy loader initializing resource service when required."""
        if self._service is None:
            creds = self.auth_manager.get_credentials()
            self._service = build('gmail', 'v1', credentials=creds)
        return self._service

    def search_messages(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Queries user message indicators matching raw Gmail filtering expressions."""
        try:
            results = self.service.users().messages().list(
                userId='me', q=query, maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Gmail search query '{query}' yielded {len(messages)} matching records.")
            return messages
        except Exception as e:
            logger.error(f"Failed pulling message lists from Gmail API: {e}")
            return []

    def get_message_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves and fully decodes a singular email document structure from disk."""
        try:
            msg = self.service.users().messages().get(
                userId='me', id=message_id, format='full'
            ).execute()
            
            parsed_email = {
                'id': msg['id'],
                'thread_id': msg['threadId'],
                'snippet': msg.get('snippet', ''),
                'subject': '', 'from': '', 'to': '', 'date': '',
                'body_text': ''
            }
            
            # Hydrate headers cleanly
            headers = msg.get('payload', {}).get('headers', [])
            for h in headers:
                name = h['name'].lower()
                if name == 'subject': parsed_email['subject'] = h['value']
                elif name == 'from': parsed_email['from'] = h['value']
                elif name == 'to': parsed_email['to'] = h['value']
                elif name == 'date': parsed_email['date'] = h['value']

            # Extract full string text out of nested mime payloads safely
            payload = msg.get('payload', {})
            parsed_email['body_text'] = self._extract_body_content(payload)
            return parsed_email
        except Exception as e:
            logger.error(f"Error fetching granular message details for {message_id}: {e}")
            return None

    def _extract_body_content(self, payload: Dict[str, Any]) -> str:
        """Recursively parses email message pieces to decode nested data bodies."""
        if 'parts' in payload:
            text_accumulator = ""
            for part in payload['parts']:
                if part.get('mimeType') == 'text/plain':
                    data = part.get('body', {}).get('data', '')
                    if data:
                        text_accumulator += base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
                elif 'parts' in part:
                    text_accumulator += self._extract_body_content(part)
            return text_accumulator
        else:
            data = payload.get('body', {}).get('data', '')
            if data and payload.get('mimeType') == 'text/plain':
                return base64.urlsafe_b64decode(data).decode('utf-8', errors='ignore')
        return ""