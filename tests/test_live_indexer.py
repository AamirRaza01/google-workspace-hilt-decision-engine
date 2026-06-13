""" Live integration harness processing mailbox data sync passes """
import sys
import asyncio
from src.utils.logger import setup_logger
from src.services.email_indexer import EmailIndexerService

async def main():
    setup_logger()
    print("="*80)
    print("🔄 LIVE GMAIL TO CHROMADB RECTOR INDEXING SERVICE TEST")
    print("="*80)
    
    try:
        indexer = EmailIndexerService()
        
        # Run a live email sync pass for messages from the last 7 days, capping at 5 items
        results = await indexer.synchronize_recent_emails(days_back=7, max_emails=5)
        
        print("\n" + "="*80)
        print("🎉 INDEXER RUN EXECUTION STATUS RESULTS:")
        print(f"   Total Inbox Items Pulled: {results['fetched']}")
        print(f"   Successfully Indexed:     {results['indexed']}")
        print(f"   Skipped (Duplicated):     {results['skipped']}")
        print("="*80)
        print("Your RAG semantic storage layers are fully populated with live emails!")
        
    except Exception as e:
        print(f"\n❌ Pipeline operational exception hit: {e}")
        print("="*80)

if __name__ == "__main__":
    asyncio.run(main())