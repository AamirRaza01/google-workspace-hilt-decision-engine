""" Automated verification harness cross-checking live Workspace Client integration lines """
import sys
from src.utils.logger import setup_logger
from src.api.gmail_client import GmailAPIClient
from src.api.calendar_client import CalendarAPIClient
from src.api.tasks_client import TasksAPIClient

def main():
    setup_logger()
    print("="*80)
    print("🔍 VERIFYING WORKSPACE TOOL CORE INTERFACE CHANNELS")
    print("="*80)
    
    try:
        print("\n1. Testing Gmail Connector...")
        gmail = GmailAPIClient()
        messages = gmail.search_messages(query="after:2025/01/01", max_results=2)
        print(f"   ✅ Gmail integration alive! (Pulled sample batch size: {len(messages)})")
        
        print("\n2. Testing Calendar Connector...")
        calendar = CalendarAPIClient()
        events = calendar.get_upcoming_events(max_results=2)
        print(f"   ✅ Calendar integration alive! (Pulled timeline list count: {len(events)})")
        
        print("\n3. Testing Tasks Connector...")
        tasks = TasksAPIClient()
        todo = tasks.list_pending_tasks(max_results=2)
        print(f"   ✅ Tasks integration alive! (Pulled backlog elements: {len(todo)})")
        
        print("\n" + "="*80)
        print("🚀 ALL COMPONENT TOOLS INITIALIZED WITHOUT ARCHITECTURAL FAULTS!")
        print("="*80)
    except Exception as e:
        print(f"\n❌ Operational failure tracked: {e}")
        print("Please check authorization parameters and active Google project console API status.")
        print("="*80)

if __name__ == "__main__":
    main()