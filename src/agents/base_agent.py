"""
Base ReAct (Reasoning + Acting) Agent Core
Autonomously coordinates tool invocation pipelines and protects state transitions 
via the integrated Explainable AI (XAI) Governance Layer.
"""

import json
import asyncio
from typing import Dict, Any, List, Callable
from src.api.gemini_client import GeminiClient
from src.config.settings import get_settings
from src.utils.logger import get_logger
from src.agents.schemas import AgentDecision
from src.xai.guard import XAIGuard

logger = get_logger()

class BaseWorkspaceAgent:
    """Core reasoning engine processing multi-turn workspace tool loops with XAI validation gates."""
    
    def __init__(self):
        self.settings = get_settings()
        self.gemini_client = GeminiClient()
        self.xai_guard = XAIGuard()  # 🛡️ Integrate our custom safety auditor
        self.tools_registry: Dict[str, Dict[str, Any]] = {}

    def register_workspace_tool(self, name: str, func: Callable, description: str, parameter_definitions: str):
        """Binds a localized python execution method wrapper into the agent's action capability array."""
        self.tools_registry[name] = {
            "function": func,
            "description": description,
            "parameters_help": parameter_definitions
        }
        logger.info(f"Dynamically registered executable agent tool: '{name}'")

    def _compile_tools_prompt_payload(self) -> str:
        """Assembles a structured index map of all live tool descriptions."""
        payload_lines = []
        for name, meta in self.tools_registry.items():
            payload_lines.append(f"- Tool Name: '{name}'\n  Capabilities: {meta['description']}\n  Expected Signature: {meta['parameters_help']}\n")
        return "\n".join(payload_lines)

    def _display_terminal_xai_report(self, tool_name: str, params: dict, report: Any):
        """Prints a highly scannable, clean CLI auditing dashboard block."""
        # ANSI terminal color formatting codes for Windows terminal highlight support
        color = "\033[92m"  # Green base
        if report.risk_level == "HIGH":
            color = "\033[91m"  # Red alert
        elif report.risk_level == "MEDIUM":
            color = "\033[93m"  # Yellow warning
        reset = "\033[0m"

        print("\n" + "="*80)
        print(f"🛡️  XAI AUDIT SECURITY REPORT: [{color}{report.risk_level}{reset} Risk]")
        print("="*80)
        print(f"Proposed Invoke: {tool_name}")
        print(f"Arguments:       {json.dumps(params)}")
        print(f"Classification:  {report.action_classification}")
        print(f"Confidence:      {report.confidence_score * 100:.1f}%")
        print("-" * 80)
        print(f"System Reasoning:\n{report.reasoning}")
        print("-" * 80)
        print(f"Calculated Impact:\n{report.potential_impact}")
        if report.alternative_suggestions:
            print("-" * 80)
            print(f"Suggested Corrective Path:\n{report.alternative_suggestions}")
        print("="*80 + "\n")

    async def execute_reasoning_cycle(self, user_query: str, max_turns: int = 6) -> Dict[str, Any]:
        """Runs the main ReAct loop, forcing high-risk mutations to pass manual HITL verification gates."""
        logger.info(f"Initializing autonomous reasoning loop for request: '{user_query}'")
        
        execution_history: List[Dict[str, Any]] = []
        current_turn = 0
        
        while current_turn < max_turns:
            current_turn += 1
            logger.info(f"Starting agent reasoning execution turn [{current_turn}/{max_turns}]...")
            
            # Formulate history logs context string
            history_accumulator = []
            for past_turn in execution_history:
                history_accumulator.append(
                    f"Turn {past_turn['turn']} Thought: {past_turn['thought']}\n"
                    f"Action Taken: Invoked tool '{past_turn['tool']}' with parameters {past_turn['params']}\n"
                    f"Resulting Observation: {json.dumps(past_turn['observation'])}\n"
                )
            history_trace_str = "\n".join(history_accumulator) if history_accumulator else "No previous tool execution turns have been run yet."

            planner_prompt = f"""You are the central nervous system of an intelligent Google Workspace Agent.
Your objective is to completely fulfill the user's intended request by selecting appropriate tools step-by-step, analyzing results, and outputting a comprehensive response.

User Target Request: "{user_query}"

=========================================================
LIVE ACTIONABLE TOOL SELECTION MATRIX
=========================================================
{self._compile_tools_prompt_payload()}

=========================================================
HISTORICAL RUNTIME TRACE OBSERVATIONS
=========================================================
{history_trace_str}

=========================================================
CRITICAL EXECUTION POLICIES
=========================================================
1. If the user query requires reading recent email data, ALWAYS use 'search_emails_rag' FIRST to gather context.
2. If the semantic results yield a promising match indicator, capture its 'email_id' and invoke 'get_email_details' exactly ONCE to review the full content.
3. Review your Historical Trace log carefully. DO NOT call the exact same tool with the exact same argument parameters repeatedly.
4. Stop executing immediately and return 'final_answer' once you have gathered sufficient metrics to fully resolve the user's query.

Determine your immediate next decision. You must respond strictly in structural JSON format matching the requested schema definition.
"""
            decision: AgentDecision = self.gemini_client.generate_structured_output(
                prompt=planner_prompt,
                response_schema=AgentDecision
            )
            
            # Flow Route 1: Synthesize final answer
            if decision.action == "final_answer":
                logger.info("Agent concluded the loop natively. Formulating final response summary.")
                return {
                    "answer": decision.final_output,
                    "history": execution_history,
                    "turns_utilized": current_turn,
                    "completed": True
                }
                
            # Flow Route 2: Intercept tool call with XAI
            if decision.action == "use_tool":
                t_name = decision.tool_name
                t_params = decision.parameters or {}
                
                # 🚀 Intercept: Fetch structured safety profile report from our XAI Guard module
                audit_report = await self.xai_guard.audit_proposed_action(
                    user_query=user_query,
                    tool_name=t_name,
                    parameters=t_params
                )
                
                # Render the clean dashboard directly on screen
                self._display_terminal_xai_report(t_name, t_params, audit_report)
                
                # 🛡️ HUMAN-IN-THE-LOOP (HITL) INTERCEPT GATE
                # If the action mutates state (writes data) OR falls below our safety index floor, demand verification
                should_execute = True
                if audit_report.action_classification == "MUTATION" or audit_report.risk_level in ["HIGH", "MEDIUM"]:
                    print(f"⚠️  [SECURITY GATE INTERCEPT] The agent is requesting permission to execute an action.")
                    user_input = input("   Do you authorize this execution sequence? (Type 'yes' or 'y' to confirm): ").strip().lower()
                    
                    if user_input not in ['yes', 'y']:
                        logger.warning(f"Execution blocked by human controller during turn {current_turn}!")
                        observation_result = "Execution Denied by User. The system controller blocked this action. Attempt an alternative strategy or ask for input parameters."
                        should_execute = False
                
                # Execute tool if verification gate clears
                if should_execute:
                    if t_name not in self.tools_registry:
                        observation_result = f"Error: The tool target '{t_name}' does not exist inside our registered index matrix."
                        logger.error(observation_result)
                    else:
                        try:
                            target_callable = self.tools_registry[t_name]["function"]
                            if asyncio.iscoroutinefunction(target_callable):
                                observation_result = await target_callable(**t_params)
                            else:
                                observation_result = target_callable(**t_params)
                        except Exception as e:
                            observation_result = f"Exception encountered during tool execution stream: {str(e)}"
                            logger.error(observation_result)

                # Append to runtime trace memory
                execution_history.append({
                    "turn": current_turn,
                    "thought": decision.thought,
                    "tool": t_name,
                    "params": t_params,
                    "observation": observation_result
                })
                
        return {
            "answer": "I reached my execution cycle limits before synthesizing a clean workspace answer.",
            "history": execution_history,
            "turns_utilized": current_turn,
            "completed": False
        }