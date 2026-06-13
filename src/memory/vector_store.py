"""
ChromaDB Persistent Vector Store Manager
Explicitly handles vector generations natively using the free Google GenAI SDK 
and inserts raw embedding lists into the collection layout.
"""

import uuid
import chromadb
from typing import List, Dict, Any, Optional
from google import genai
from src.config.settings import get_settings
from src.utils.logger import get_logger

logger = get_logger()

class PersistentVectorStore:
    """Handles raw vector calculations and ChromaDB similarity search storage operations."""
    
    def __init__(self):
        self.settings = get_settings()
        
        self.client = genai.Client(
            api_key=self.settings.gemini_api_key,
        )
        self.model_target = "gemini-embedding-001"
        
        # Initialize native persistent Chroma client
        self.chroma_client = chromadb.PersistentClient(path=self.settings.chroma_persist_directory)
        
        # Create a clean collection without adding an internal embedding function
        self.collection = self.chroma_client.get_or_create_collection(
            name=self.settings.chroma_collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info(f"ChromaDB initialized. Active collection contains {self.collection.count()} elements.")

    def _get_embedding_vector(self, text: str) -> List[float]:
        """Directly requests raw float vector strings from Google's cloud server."""
        try:
            response = self.client.models.embed_content(
                model=self.model_target,
                contents=text
            )
            return response.embeddings[0].values
        except Exception as e:
            logger.error(f"Native Gemini cloud embedding calculation hit an issue: {e}")
            raise e

    def add_email_chunk(self, email_id: str, text_chunk: str, metadata: Dict[str, Any]):
        """Injects text data chunks along with pre-calculated raw vector arrays into ChromaDB."""
        try:
            doc_id = f"chunk_{email_id}_{uuid.uuid4().hex[:8]}"
            
            # Pre-calculate the embedding vector natively inside our wrapper code
            calculated_vector = self._get_embedding_vector(text_chunk)
            
            sanitized_metadata = {
                "email_id": email_id,
                "subject": str(metadata.get("subject", "")),
                "from": str(metadata.get("from", "")),
                "date": str(metadata.get("date", "")),
                "chunk_preview": text_chunk[:150]
            }
            
            # Explicitly pass the pre-computed raw vector array directly to the database
            self.collection.add(
                embeddings=[calculated_vector],
                documents=[text_chunk],
                metadatas=[sanitized_metadata],
                ids=[doc_id]
            )
            logger.debug(f"Indexed pre-computed vector space node for email ID: {email_id}")
        except Exception as e:
            logger.error(f"Failed inserting manual vector into collection: {e}")

    def query_semantic_matches(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """Queries database records using manual vector representations for maximum control."""
        try:
            if self.collection.count() == 0:
                return []

            # Pre-calculate the search text query vector natively
            query_vector = self._get_embedding_vector(query)

            # Query the database collection using the computed float coordinate layout
            results = self.collection.query(
                query_embeddings=[query_vector],
                n_results=max_results
            )
            
            formatted_matches = []
            if results and results.get('documents') and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    formatted_matches.append({
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 1.0
                    })
            return formatted_matches
        except Exception as e:
            logger.error(f"Manual vector query verification error: {e}")
            return []

    def clear_all_vector_data(self):
        """Resets the vector database data paths smoothly to isolate runtime changes."""
        try:
            self.chroma_client.delete_collection(name=self.settings.chroma_collection_name)
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.settings.chroma_collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("Vector collection cleared successfully.")
        except Exception as e:
            logger.error(f"Failed resetting vector storage space collection: {e}")