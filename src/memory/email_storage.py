"""
Full Email Document Storage Cache
Persists un-chunked email records locally for full-text recovery.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from src.utils.logger import get_logger

logger = get_logger()

class EmailStorageCache:
    """Manages raw JSON document dumps for full-text reconstructions."""
    
    def __init__(self, runtime_path: str = "data/email_full_cache.json"):
        self.storage_path = Path(runtime_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache: Dict[str, Any] = self._load_cache_from_disk()

    def _load_cache_from_disk(self) -> Dict[str, Any]:
        """Loads cached text assets seamlessly into memory cache maps."""
        try:
            if self.storage_path.exists():
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Failed to read raw email cache from disk: {e}")
            return {}

    def save_cache_to_disk(self):
        """Commits memory storage maps back to local runtime files safely."""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed writing email cache tracking lines down to disk: {e}")

    def cache_email_record(self, email_id: str, email_payload: Dict[str, Any]):
        """Caches full un-chunked document bodies before indexing pipelines run."""
        self._cache[email_id] = {
            'id': email_id,
            'subject': email_payload.get('subject', ''),
            'from': email_payload.get('from', ''),
            'to': email_payload.get('to', ''),
            'date': email_payload.get('date', ''),
            'body_text': email_payload.get('body_text', ''),
            'thread_id': email_payload.get('thread_id', '')
        }
        self.save_cache_to_disk()
        logger.debug(f"Cached full email body metadata cleanly for ID: {email_id}")

    def get_full_email(self, email_id: str) -> Optional[Dict[str, Any]]:
        """Recovers entire original text content block for agent synthesis actions."""
        return self._cache.get(email_id)