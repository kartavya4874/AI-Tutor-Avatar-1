"""
Utility functions for Azure AI Avatar application
"""
import re
import html
import logging
from typing import List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

def html_encode(text: str) -> str:
    """
    HTML encode text for safe use in SSML
    
    Args:
        text: Text to encode
        
    Returns:
        str: HTML encoded text
    """
    return html.escape(text)

def remove_doc_references(text: str) -> str:
    """
    Remove document reference markers like [doc1], [doc2] from text
    
    Args:
        text: Text containing document references
        
    Returns:
        str: Text with references removed
    """
    return re.sub(r'\[doc\d+\]', '', text).strip()

def split_into_sentences(text: str, punctuations: Optional[List[str]] = None) -> List[str]:
    """
    Split text into sentences based on punctuation marks
    
    Args:
        text: Text to split
        punctuations: List of sentence-ending punctuation marks
        
    Returns:
        List[str]: List of sentences
    """
    if punctuations is None:
        punctuations = ['.', '?', '!', ':', ';', '。', '？', '！', '：', '；']
    
    sentences = []
    current_sentence = ""
    
    for char in text:
        current_sentence += char
        if char in punctuations:
            sentences.append(current_sentence.strip())
            current_sentence = ""
    
    # Add remaining text as a sentence
    if current_sentence.strip():
        sentences.append(current_sentence.strip())
    
    return sentences

def format_timestamp(dt: Optional[datetime] = None) -> str:
    """
    Format datetime as readable string
    
    Args:
        dt: Datetime object (uses current time if None)
        
    Returns:
        str: Formatted timestamp
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def validate_azure_endpoint(endpoint: str) -> bool:
    """
    Validate Azure endpoint URL format
    
    Args:
        endpoint: Endpoint URL to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not endpoint:
        return False
    
    # Should start with https://
    if not endpoint.startswith("https://"):
        return False
    
    # Should contain azure domain
    azure_domains = [
        ".openai.azure.com",
        ".cognitiveservices.azure.com",
        ".search.windows.net",
        ".speech.microsoft.com"
    ]
    
    return any(domain in endpoint for domain in azure_domains)

def sanitize_input(text: str, max_length: int = 5000) -> str:
    """
    Sanitize user input text
    
    Args:
        text: Text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        str: Sanitized text
    """
    if not text:
        return ""
    
    # Remove control characters except newline and tab
    text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', '', text)
    
    # Trim whitespace
    text = text.strip()
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length]
        logger.warning(f"Input truncated to {max_length} characters")
    
    return text

def format_chat_message(role: str, content: str, timestamp: Optional[datetime] = None) -> dict:
    """
    Format a chat message for display
    
    Args:
        role: Message role (user/assistant/system)
        content: Message content
        timestamp: Message timestamp
        
    Returns:
        dict: Formatted message
    """
    return {
        "role": role,
        "content": content,
        "timestamp": format_timestamp(timestamp)
    }

def extract_code_blocks(text: str) -> List[dict]:
    """
    Extract code blocks from markdown-formatted text
    
    Args:
        text: Text containing code blocks
        
    Returns:
        List[dict]: List of code blocks with language and content
    """
    pattern = r'```(\w+)?\n(.*?)```'
    matches = re.finditer(pattern, text, re.DOTALL)
    
    code_blocks = []
    for match in matches:
        language = match.group(1) or 'text'
        code = match.group(2).strip()
        code_blocks.append({
            'language': language,
            'code': code
        })
    
    return code_blocks

def estimate_speaking_time(text: str, words_per_minute: int = 150) -> float:
    """
    Estimate speaking time for given text
    
    Args:
        text: Text to estimate
        words_per_minute: Average speaking rate
        
    Returns:
        float: Estimated time in seconds
    """
    word_count = len(text.split())
    minutes = word_count / words_per_minute
    return minutes * 60

def get_language_from_locale(locale: str) -> str:
    """
    Extract language code from locale string
    
    Args:
        locale: Locale string (e.g., 'en-US', 'fr-FR')
        
    Returns:
        str: Language code (e.g., 'en', 'fr')
    """
    return locale.split('-')[0] if '-' in locale else locale

def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size (e.g., '1.5 MB')
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def create_avatar_config_summary(config) -> dict:
    """
    Create a summary of avatar configuration
    
    Args:
        config: Configuration object
        
    Returns:
        dict: Configuration summary
    """
    return {
        "Speech Region": config.speech_region,
        "Avatar Character": config.avatar_character,
        "Avatar Style": config.avatar_style,
        "TTS Voice": config.tts_voice,
        "OpenAI Deployment": config.openai_deployment,
        "STT Locales": ", ".join(config.stt_locales),
        "Data Sources Enabled": len(getattr(config, 'data_sources', [])) > 0
    }

class MessageBuffer:
    """Buffer for accumulating streaming message chunks"""
    
    def __init__(self, sentence_punctuations: Optional[List[str]] = None):
        """
        Initialize message buffer
        
        Args:
            sentence_punctuations: Punctuation marks that end sentences
        """
        self.buffer = ""
        self.complete_sentences = []
        self.punctuations = sentence_punctuations or ['.', '?', '!', ':', ';']
    
    def add_chunk(self, chunk: str) -> List[str]:
        """
        Add a chunk to buffer and return complete sentences
        
        Args:
            chunk: Text chunk to add
            
        Returns:
            List[str]: Complete sentences found
        """
        self.buffer += chunk
        sentences = []
        
        # Check if buffer ends with sentence punctuation
        if self.buffer and self.buffer[-1] in self.punctuations:
            sentences.append(self.buffer)
            self.complete_sentences.append(self.buffer)
            self.buffer = ""
        
        return sentences
    
    def flush(self) -> Optional[str]:
        """
        Get remaining buffer content
        
        Returns:
            Optional[str]: Remaining text or None
        """
        if self.buffer:
            text = self.buffer
            self.complete_sentences.append(text)
            self.buffer = ""
            return text
        return None
    
    def get_all(self) -> str:
        """
        Get all accumulated text
        
        Returns:
            str: Complete text
        """
        return "".join(self.complete_sentences)
    
    def clear(self):
        """Clear the buffer"""
        self.buffer = ""
        self.complete_sentences = []

def log_api_call(service: str, endpoint: str, status: str, duration_ms: Optional[float] = None):
    """
    Log API call for debugging and monitoring
    
    Args:
        service: Service name (e.g., 'Azure OpenAI', 'Speech')
        endpoint: API endpoint called
        status: Call status ('success' or 'error')
        duration_ms: Duration in milliseconds
    """
    log_msg = f"[{service}] {endpoint} - {status}"
    if duration_ms:
        log_msg += f" ({duration_ms:.2f}ms)"
    
    if status == "success":
        logger.info(log_msg)
    else:
        logger.error(log_msg)