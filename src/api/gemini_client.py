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
        Crucial for reliable tool-calling parsing and UI JSON telemetry delivery.
        """
        try:
            config = types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=response_schema,
                temperature=0.1,  # Strict determinism for schema adherence
            )
            
            response = self.client.models.generate_content(
                model=self.settings.gemini_model,
                contents=prompt,
                config=config
            )
            
            # Rehydrate the JSON string back into the verified Pydantic model instance
            return response_schema.model_validate_json(response.text)
        except Exception as e:
            logger.error(f"Error during Gemini structured schema parsing: {e}")
            raise e