"""
Text Processing and Token Chunking Utilities
Cleans raw text strings and handles sentence-boundary text chunking.
"""

import re
import html2text
from typing import List
from src.utils.logger import get_logger

logger = get_logger()

def clean_and_format_html(html_content: str) -> str:
    """Converts unstructured raw HTML message sections into clean markdown format."""
    if not html_content:
        return ""
    try:
        converter = html2text.HTML2Text()
        converter.ignore_links = False
        converter.ignore_images = True
        converter.ignore_emphasis = False
        return converter.handle(html_content).strip()
    except Exception as e:
        logger.warning(f"html2text parser hit an exception: {e}. Falling back to regex filter.")
        # Fail-safe regex tag scrubber
        return re.sub(r'<[^>]*>', ' ', html_content).strip()

def chunk_text_by_boundary(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """
    Splits text strings into overlapping semantic chunks.
    Attempts to preserve sentence boundaries to avoid splitting critical details.
    """
    if not text or len(text) <= chunk_size:
        return [text] if text else []

    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        
        # If we aren't at the end of the text, try to find a natural sentence boundary
        if end < text_length:
            # Look backwards up to 150 characters for a period sentence boundary
            boundary = text.rfind('.', end - 150, end)
            if boundary != -1:
                end = boundary + 1  # Include the period in the current chunk

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
            
        start = end - overlap
        
    return chunks