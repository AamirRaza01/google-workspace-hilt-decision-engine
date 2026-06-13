""" Verification harness checking autonomous agent loop reasoning capabilities """
import sys
import asyncio
from src.utils.logger import setup_logger
from src.workflows.autonomous_agent import AutonomousWorkspaceAgent

async def run_integration_test():
    setup_logger()
    print("="*80)
    print("🤖 AUTONOMOUS REACT ENGINE REASONING & TOOL CALL INTEGRATION TESTS")
    print("="*80)
    
    # Instantiate our complete operational agent setup wrapper
    orchestrator = AutonomousWorkspaceAgent()
    
    # We will pass a query related to the pre-placement text we indexed in Phase 3
    test_phrase = "Check my placement emails and tell me what algorithm questions I need to study for tomorrow."
    print(f"\nUser Intent Input: '{test_phrase}'")
    print("Forwarding to agent loop architecture...")
    
    response = await orchestrator.run_query(test_phrase)
    
    print("\n" + "="*80)
    print("🚨 AGENT LOOP RESPONSE PROFILE EXECUTION SUMMARY")
    print("="*80)
    print(f"Turns Utilized:   {response['turns_utilized']}")
    print(f"Completion State: {response['completed']}")
    print(f"\nFinal AI Answer:\n{response['answer']}")
    print("-" * 80)
    print("Tool Invocation Execution Paths Traversed:")
    for turn in response['history']:
        print(f"  - Turn {turn['turn']} selected tool: '{turn['tool']}' using args: {turn['params']}")
    print("="*80)

if __name__ == "__main__":
    asyncio.run(run_integration_test())