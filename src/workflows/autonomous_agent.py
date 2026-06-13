"""
Autonomous Workspace Orchestration Layer
Instantiates the ReAct brain framework and binds all primary Google tool handles natively.
"""

from typing import Dict, Any, List
from src.agents.base_agent import BaseWorkspaceAgent
from src.api.gmail_client import GmailAPIClient
from src.api.calendar_client import CalendarAPIClient
from src.api.tasks_client import TasksAPIClient
from src.memory.vector_store import PersistentVectorStore
from src.memory.email_storage import EmailStorageCache
from src.utils.logger import get_logger

logger = get_logger()

class AutonomousWorkspaceAgent:
    """High-level system orchestrator registering capabilities and handling query entries."""
    
    def __init__(self):
        # 1. Initialize our functional core sub-clients
        self.gmail = GmailAPIClient()
        self.calendar = CalendarAPIClient()
        self.tasks = TasksAPIClient()
        self.vdb = PersistentVectorStore()
        self.cache = EmailStorageCache()
        
        # 2. Instantiate our core reasoning agent brain loop
        self.agent_brain = BaseWorkspaceAgent()
        
        # 3. Formally link and register our localized workspace tools
        self._wire_capabilities_matrix()
        logger.info("Autonomous Workspace Agent successfully initialized and ready for execution.")

    def _wire_capabilities_matrix(self):
        """Maps functional workspace tool signatures directly into our agent brain framework."""
        
        # Tool 1: Semantic Email Lookup (RAG Memory Engine Access)
        self.agent_brain.register_workspace_tool(
            name="search_emails_rag",
            func=self.vdb.query_semantic_matches,
            description="PRIMARY tool for searching emails. Checks our persistent vector storage for conceptually matched email text snippets. Use this first for any historical workspace lookups.",
            parameter_definitions="query: str (The search term concept), max_results: int (Optional, default is 5)"
        )
        
        # Tool 2: Full Document Ingestion (Local Cache Body Fetch)
        self.agent_brain.register_workspace_tool(
            name="get_email_details",
            func=self.cache.get_full_email,
            description="Retrieves the full, raw text content of a cached email. Use this immediately AFTER locate actions find a promising target email ID.",
            parameter_definitions="email_id: str (The unique alphabetical identifier string code fetched from search results)"
        )
        
        # Tool 3: Live Inbox Fetch (Gmail API Live Fallback Channel)
        self.agent_brain.register_workspace_tool(
            name="search_emails_live_gmail",
            func=self.gmail.search_messages,
            description="FALLBACK tool. Queries live messages from Gmail API. Use only if semantic search fails, or if you need extremely fresh messages from today.",
            parameter_definitions="query: str (Gmail syntax search parameters string like 'from:professor'), max_results: int"
        )
        
        # Tool 4: Schedule Timeline Reading (Calendar Tracker Channel)
        self.agent_brain.register_workspace_tool(
            name="get_upcoming_calendar_events",
            func=self.calendar.get_upcoming_events,
            description="Fetches a sorted list index of your upcoming calendar appointments.",
            parameter_definitions="max_results: int (Optional constraint parameter tracking timeline elements count)"
        )
        
        # Tool 5: Calendar Injections (Calendar Write Mutation Channel)
        self.agent_brain.register_workspace_tool(
            name="create_calendar_event",
            func=self.calendar.create_event,
            description="Creates a new scheduled event on your calendar coordinate timeline. High-risk write action.",
            parameter_definitions="summary: str (Title name), start_iso: str (RFC3339 text timestamp format), end_iso: str (End RFC3339 text timestamp), description: str"
        )
        
        # Tool 6: Tasks BACKLOG Injection (Tasks Write Mutation Channel)
        self.agent_brain.register_workspace_tool(
            name="create_reminder_task",
            func=self.tasks.create_task,
            description="Appends a fresh structured tracker item line inside your primary Google Tasks list.",
            parameter_definitions="title: str (Task text summary heading), notes: str (Optional descriptive context lines), due_iso: str (Optional RFC3339 deadline date string)"
        )

    async def run_query(self, query_string: str) -> Dict[str, Any]:
        """Entry gateway forwarding natural phrases directly into our core reasoning cycle loop."""
        return await self.agent_brain.execute_reasoning_cycle(user_query=query_string)