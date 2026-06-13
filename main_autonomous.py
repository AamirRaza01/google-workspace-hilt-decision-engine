"""
Explainable & Risk-Aware Workspace Agent - Primary Main CLI Entry Point
Runs an interactive turn loop providing full system transparency reports natively.
"""

import sys
import asyncio
from pathlib import Path

# Explicit project root alignment hook
sys.path.insert(0, str(Path(__file__).parent))

from src.utils.logger import setup_logger, get_logger
from src.config.settings import get_settings
from src.workflows.autonomous_agent import AutonomousWorkspaceAgent
from src.services.email_indexer import EmailIndexerService

# Setup global logger configurations
setup_logger()
logger = get_logger()

async def interactive_terminal_loop():
    """Starts a responsive console turn cycle providing deep auditing transparency hooks."""
    print("=" * 80)
    print("🛡️  EXPLAINABLE AI (XAI) & RISK-AWARE GOOGLE WORKSPACE AGENT CORE")
    print("=" * 80)
    print("\nBooting underlying workspace connection matrix engines...")
    
    # Initialize our system clients from scratch
    agent = AutonomousWorkspaceAgent()
    indexer = EmailIndexerService()
    settings = get_settings()
    
    print("✓ All connection managers initialized successfully!")
    print("\n📋 INTERACTIVE CONSOLE COMMAND CODES:")
    print("  - [Natural Query]  -> Type anything naturalmente (e.g. 'Check my emails')")
    print("  - sync             -> Trigger incremental background scan over last 7 days")
    print("  - stats            -> Fetch ChromaDB memory collection vectors and indices")
    print("  - clear            -> Clear current transient conversation history bounds")
    print("  - quit             -> Close application boundaries safely")
    print("\n" + "=" * 80)

    while True:
        try:
            print("\n")
            user_input = input("\033[94mYou:\033[0m ").strip()
            
            if not user_input:
                continue
                
            # Handle manual operational override commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Deactivating workspace session. Goodbye!")
                break
                
            elif user_input.lower() == 'sync':
                print("\n🔄 Running direct Gmail to ChromaDB semantic index sync pass...")
                stats = await indexer.synchronize_recent_emails(days_back=7, max_emails=10)
                print(f"✓ Sync Complete! Indexed: {stats['indexed']} items | Skipped: {stats['skipped']}")
                continue
                
            elif user_input.lower() == 'stats':
                print("\n📊 LOCAL DATABASE RUNTIME QUANTUM:")
                print(f"  - Active Collection Vector Count:  {agent.vdb.collection.count()} elements")
                print(f"  - Target Gemini Ingestion Model: {settings.gemini_model}")
                continue
                
            elif user_input.lower() == 'clear':
                print("\n✓ Resetting transient local state vectors.")
                continue

            # Process query
            print("\n🤔 Agent is building reasoning execution graphs...")
            response = await agent.run_query(user_input)
            
            print(f"\n🤖 \033[96mAgent Final Resolution:\033[0m {response['answer']}")
            print(f"💭 Turns Expended: {response['turns_utilized']}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Deactivating workspace session. Goodbye!")
            break
        except Exception as e:
            logger.error(f"Uncaught cycle exception tracked inside root main thread loop: {e}")
            print(f"\n❌ Execution Error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(interactive_terminal_loop())
    except Exception as fatal_err:
        logger.critical(f"System crashed during main runtime configuration: {fatal_err}")
        sys.exit(1)