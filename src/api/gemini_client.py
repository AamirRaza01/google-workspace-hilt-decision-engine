"""
Google Gemini GenAI Core Client
Handles lightning-fast text generations and structured JSON schema outputs
using the modern official free-tier Google GenAI SDK.
"""

from typing import List, Dict, Any, Type
from pydantic import BaseModel
from google import genai
from google.genai import types
from src.config.settings import get_settings
from src.utils.logger import get_logger

logger = get_logger()

class GeminiClient:
    """Core LLM communicator for ReAct planning and Explainable AI guard rails."""
    
    def __init__(self):
        self.settings = get_settings()
        if not self.settings.gemini_api_key:
            logger.error("GEMINI_API_KEY is completely missing from your .env configuration file!")
        
        # Initialize the official unified GenAI Client
        self.client = genai.Client(api_key=self.settings.gemini_api_key)
        logger.info(f"Gemini Client initialized successfully using model: {self.settings.gemini_model}")

    def generate_response(self, contents: str | List[Any], system_instruction: str = None) -> str:
        """Standard free-tier text generation for thoughts and conversations."""
        try:
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2,  # Keep responses predictable and analytical
            )
            
            response = self.client.models.generate_content(
                model=self.settings.gemini_model,
                contents=contents,
                config=config
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error during Gemini text generation: {e}")
            raise e

    def generate_structured_output(self, prompt: str, response_schema: Type[BaseModel]) -> BaseModel:
        """
        Bypasses the restrictive schema endpoint to avoid 429 errors.
        Prompts Gemini for raw JSON text and validates it against Pydantic natively.
        """
        try:
            # Inject explicit instructions into the prompt to guarantee pure JSON text back
            json_instruction_prompt = f"""{prompt}

CRITICAL: Your response must be a single, valid JSON object matching the keys specified below. 
Do not include markdown blocks like ```json ... ```. Do not include any extra text outside the JSON.

Expected Keys: {list(response_schema.model_fields.keys())}
"""
            # Call standard text generation (which has high free-tier quotas)
            response = self.client.models.generate_content(
                model=self.settings.gemini_model,
                contents=json_instruction_prompt,
                config=types.GenerateContentConfig(temperature=0.1)
            )
            
            clean_text = response.text.strip()
            
            # Defensive step: Strip markdown code block wrappers if the model accidentally includes them
            if clean_text.startswith("```"):
                lines = clean_text.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                clean_text = "\n".join(lines).strip()

            # Load the text as a dictionary and validate against our Pydantic model
            import json
            parsed_dict = json.loads(clean_text, strict=False)
            return response_schema.model_validate(parsed_dict)
                
        except Exception as e:
            logger.error(f"Text-based JSON parsing or validation failed: {e}")
            # Fallback block: Return a valid empty object to prevent the engine from crashing mid-loop
            raise e

    def _clean_schema_keys(self, schema: Any) -> Any:
        """Recursively removes 'additionalProperties' and titles from schema definitions."""
        if isinstance(schema, dict):
            # Drop keys that conflict with Gemini's strict OpenAPI validator
            cleaned = {k: self._clean_schema_keys(v) for k, v in schema.items() 
                       if k not in ["additionalProperties", "title"]}
            return cleaned
        elif isinstance(schema, list):
            return [self._clean_schema_keys(item) for item in schema]
        return schema