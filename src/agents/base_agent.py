"""
Base ReAct (Reasoning + Acting) Agent Core
Autonomously coordinates tool invocation pipelines and collects execution observations.
"""

import json
import asyncio
from typing import Dict, Any, List, Callable
from src.api.gemini_client import GeminiClient
from src.config.settings import get_settings
from src.utils.logger import get_logger
from src.agents.schemas import AgentDecision

logger = get_logger()

class BaseWorkspaceAgent:
    """Core reasoning engine processing multi-turn workspace tool execution loops."""
    
    def __init__(self):
        self.settings = get_settings()
        self.gemini_client = GeminiClient()
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
        """Assembles a highly readable, structured dictionary index mapping of all live tool descriptions."""
        payload_lines = []
        for name, meta in self.tools_registry.items():
            payload_lines.append(f"- Tool Name: '{name}'\n  Capabilities: {meta['description']}\n  Expected Signature: {meta['parameters_help']}\n")
        return "\n".join(payload_lines)

    async def execute_reasoning_cycle(self, user_query: str, max_turns: int = 6) -> Dict[str, Any]:
        """Runs the main ReAct loop: thinks, selects tools, records observations, and synthesizes answers."""
        logger.info(f"Initializing autonomous reasoning loop for request: '{user_query}'")
        
        execution_history: List[Dict[str, Any]] = []
        current_turn = 0
        
        while current_turn < max_turns:
            current_turn += 1
            logger.info(f"Starting agent reasoning execution turn [{current_turn}/{max_turns}]...")
            
            # Build up the contextual historical trace log string
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
            3. Review your Historical Trace log carefully. DO NOT call the exact same tool with the exact same argument parameters repeatedly. If a tool comes back empty, try a different strategy or conclude with a clean final answer.
            4. Stop executing immediately and return 'final_answer' once you have gathered sufficient metrics to fully resolve the user's query.

            Determine your immediate next decision. You must respond strictly in structural JSON format matching the requested schema definition.
            """
            # Request a structured Pydantic schema return directly from our Gemini Client
            decision: AgentDecision = self.gemini_client.generate_structured_output(
                prompt=planner_prompt,
                response_schema=AgentDecision
            )
            
            logger.info(f"Agent Turn Thought: \"{decision.thought}\"")
            
            # Flow Route 1: The agent is ready to conclude and return its final answer
            if decision.action == "final_answer":
                logger.info("Agent concluded the loop natively. Formulating final response summary.")
                return {
                    "answer": decision.final_output,
                    "history": execution_history,
                    "turns_utilized": current_turn,
                    "completed": True
                }
                
            # Flow Route 2: The agent decided it needs to run a local workspace tool
            if decision.action == "use_tool":
                t_name = decision.tool_name
                t_params = decision.parameters or {}
                
                logger.info(f"Agent requested tool execution pass: targetting '{t_name}' using args: {t_params}")
                
                if t_name not in self.tools_registry:
                    observation_result = f"Error: The tool target '{t_name}' does not exist inside our registered index matrix."
                    logger.error(observation_result)
                else:
                    try:
                        # Fetch the function reference wrapper from the tools registry map
                        target_callable = self.tools_registry[t_name]["function"]
                        
                        # Dynamically unpack the JSON parameters straight into the method execution call
                        if asyncio.iscoroutinefunction(target_callable):
                            observation_result = await target_callable(**t_params)
                        else:
                            observation_result = target_callable(**t_params)
                    except Exception as e:
                        observation_result = f"Exception encountered during tool execution stream: {str(e)}"
                        logger.error(observation_result)

                # Commit this entire turn loop's analytical execution trace record back into the state machine
                execution_history.append({
                    "turn": current_turn,
                    "thought": decision.thought,
                    "tool": t_name,
                    "params": t_params,
                    "observation": observation_result
                })
                
        # Fallback termination edge case if loop max iterations bounds get breached
        return {
            "answer": "I reached my execution cycle limits before synthesizing a clean workspace answer. Please refine your query parameters.",
            "history": execution_history,
            "turns_utilized": current_turn,
            "completed": False
        }