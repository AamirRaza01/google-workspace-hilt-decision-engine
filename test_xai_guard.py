""" Integration test checking independent Explainable AI risk metric evaluations """
import sys
import asyncio
from src.utils.logger import setup_logger
from src.xai.guard import XAIGuard

async def test_governance_guard():
    setup_logger()
    print("="*80)
    print("🛡️  EXPLAINABLE AI (XAI) GOVERNANCE SYSTEM AUDIT INTEGRATION TESTS")
    print("="*80)
    
    guard = XAIGuard()
    
    # Define a high-risk mutation write task anomaly scenario to check guard sensitivity
    user_request = "Set up a sync appointment for tomorrow at 10 AM with Professor regarding my BTP."
    proposed_tool = "create_calendar_event"
    proposed_args = {
        "summary": "BTP Sync Review Meeting",
        "start_iso": "2026-06-14T10:00:00Z",
        # Notice an entry error parameter: Agent set the end time to be identical to start time (0 minute duration!)
        "end_iso": "2026-06-14T10:00:00Z",
        "description": "Autonomous calendar entry regarding undergraduate thesis sync."
    }
    
    print(f"\n[Test Item] User Request: \"{user_request}\"")
    print(f"Agent Proposed Tool: {proposed_tool}")
    print(f"Agent Parameters:    {proposed_args}")
    print("\nRunning independent verification check...")
    
    audit_report = await guard.audit_proposed_action(
        user_query=user_request,
        tool_name=proposed_tool,
        parameters=proposed_args
    )
    
    # Formulate a beautiful reporting telemetry view
    print("\n" + "="*70)
    print("🛡️  XAI RISK MANAGEMENT TELEMETRY RECONSTRUCTION REPORT")
    print("="*70)
    print(f"Calculated Confidence Score: {audit_report.confidence_score * 100:.1f}%")
    print(f"Action Classification:       {audit_report.action_classification}")
    print(f"Calculated Risk Threshold:   {audit_report.risk_level}")
    print("-" * 70)
    print(f"AI System Reasoning:\n{audit_report.reasoning}")
    print("-" * 70)
    print(f"Calculated System Impact:\n{audit_report.potential_impact}")
    if audit_report.alternative_suggestions:
        print("-" * 70)
        print(f"Corrective Suggestions Provided:\n{audit_report.alternative_suggestions}")
    print("="*70)

if __name__ == "__main__":
    asyncio.run(test_governance_guard())