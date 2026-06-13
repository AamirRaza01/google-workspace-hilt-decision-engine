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
        Forces Gemini to return structured, type-safe data matching a Pydantic class.
        Cleans the generated schema to prevent 400 INVALID_ARGUMENT errors.
        """
        try:
            # 1. Generate the raw schema dictionary from Pydantic
            raw_schema = response_schema.model_json_schema()
            
            # 2. Deeply clean the dictionary to strip out API-breaking keys
            cleaned_schema = self._clean_schema_keys(raw_schema)
            
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=cleaned_schema,
                temperature=0.1,
            )
            
            response = self.client.models.generate_content(
                model=self.settings.gemini_model,
                contents=prompt,
                config=config
            )
            
            return response_schema.model_validate_json(response.text)
        except Exception as e:
            logger.error(f"Error during Gemini structured schema parsing: {e}")
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