"""
Automated Email Indexing Service
Periodically pulls live messages from Gmail, generates summaries, 
and synchronizes text assets with rich metadata into ChromaDB.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, List
from src.config.settings import get_settings
from src.utils.logger import get_logger
from src.api.gmail_client import GmailAPIClient
from src.api.gemini_client import GeminiClient
from src.memory.vector_store import PersistentVectorStore
from src.memory.email_storage import EmailStorageCache
from src.utils.text_processing import chunk_text_by_boundary

logger = get_logger()

class EmailIndexerService:
    """Manages full pipeline flows transforming live Gmail records into indexed vector formats."""
    
    def __init__(self):
        self.settings = get_settings()
        self.gmail_client = GmailAPIClient()
        self.gemini_client = GeminiClient()
        self.vector_store = PersistentVectorStore()
        self.email_storage = EmailStorageCache()

    async def generate_email_summary(self, subject: str, body_text: str) -> str:
        try:
            if not body_text:
                return f"Email regarding: {subject}"
                
            prompt = f"""Summarize the core message of this email into a maximum of 2 sentences. Be concise and focus on dates, deadlines, or actionable constraints.

            Subject: {subject}
            Body Content:
            {body_text[:2500]}"""
            
            system_instruction = "You are an expert executive assistant. Write brief, informative email summaries."
            summary = self.gemini_client.generate_response(contents=prompt, system_instruction=system_instruction)
            return summary.strip()
        except Exception as e:
            logger.error(f"Failed to calculate AI summary: {e}")
            return f"Subject: {subject} (Full text cached)"

    def auto_categorize_email(self, subject: str, body_text: str) -> str:
        """Classifies emails into specific semantic categories to aid downstream agent filters."""
        text_dump = f"{subject} {body_text}".lower()
        
        if any(w in text_dump for w in ['placement', 'recruitment', 'job', 'interview', 'hiring', 'shortlist', 'career']):
            return 'placement'
        elif any(w in text_dump for w in ['exam', 'assignment', 'lecture', 'quiz', 'course', 'grade', 'btp', 'thesis', 'professor']):
            return 'academic'
        elif any(w in text_dump for w in ['meeting', 'calendar', 'zoom', 'schedule', 'sync', 'teams']):
            return 'meeting'
        elif any(w in text_dump for w in ['deadline', 'project', 'task', 'milestone', 'git', 'repo']):
            return 'work'
        return 'general'

    async def synchronize_recent_emails(self, days_back: int = 7, max_emails: int = 20) -> Dict[str, Any]:
        """
        Sweeps your active Gmail account for recent messages, filters out 
        already-indexed IDs, and saves new emails to your RAG memory.
        """
        logger.info(f"Initiating mailbox sync sweep over the last {days_back} days...")
        
        # Formulate Gmail search expression parameter query string
        target_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y/%m/%d')
        gmail_query = f"after:{target_date}"
        
        # Pull raw message references from the mailbox
        message_list = self.gmail_client.search_messages(query=gmail_query, max_results=max_emails)
        if not message_list:
            logger.info("Sync complete. Zero new messages found to synchronize.")
            return {"fetched": 0, "indexed": 0, "skipped": 0}

        indexed_count = 0
        skipped_count = 0
        
        for idx, msg_ref in enumerate(message_list, 1):
            email_id = msg_ref['id']
            
            # De-duplication check: Skip if this specific email_id already exists in local storage
            if self.email_storage.get_full_email(email_id):
                skipped_count += 1
                continue
                
            # Fetch and decode full message details
            email_details = self.gmail_client.get_message_details(email_id)
            if not email_details:
                continue

            logger.info(f"Processing message [{idx}/{len(message_list)}]: {email_details['subject'][:40]}...")
            
            # Generate AI summary and metadata tags
            summary_text = await self.generate_email_summary(email_details['subject'], email_details['body_text'])
            category_tag = self.auto_categorize_email(email_details['subject'], email_details['body_text'])
            
            # Cache the full un-chunked document body for later retrieval by the agent
            email_record = {
                'subject': email_details['subject'],
                'from': email_details['from'],
                'to': email_details['to'],
                'date': email_details['date'],
                'body_text': email_details['body_text'],
                'thread_id': email_details['thread_id']
            }
            self.email_storage.cache_email_record(email_id, email_record)
            
            # Break the text into chunks and save them to the vector store
            text_chunks = chunk_text_by_boundary(email_details['body_text'], chunk_size=1000, overlap=150)
            for chunk in text_chunks:
                chunk_metadata = {
                    "subject": email_details['subject'],
                    "from": email_details['from'],
                    "date": email_details['date'],
                    "category": category_tag,
                    "summary": summary_text
                }
                self.vector_store.add_email_chunk(email_id, chunk, chunk_metadata)
                
            indexed_count += 1
            # Rate-limiting cushion 
            await asyncio.sleep(1.0)
            
        logger.info(f"Sync complete. Newly indexed: {indexed_count} emails. Skipped: {skipped_count} copies.")
        return {"fetched": len(message_list), "indexed": indexed_count, "skipped": skipped_count}