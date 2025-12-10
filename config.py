"""Configuration module for Azure AI Avatar application"""
import os
from dataclasses import dataclass, field
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class Config:
    """Configuration class to store all application settings"""
    
    # Azure Speech Service - from environment
    speech_key: str = field(default_factory=lambda: os.getenv('AZURE_SPEECH_KEY', ''))
    speech_region: str = field(default_factory=lambda: os.getenv('AZURE_SPEECH_REGION', 'westus2'))
    private_endpoint: Optional[str] = field(default_factory=lambda: os.getenv('AZURE_SPEECH_PRIVATE_ENDPOINT'))
    use_private_endpoint: bool = field(default_factory=lambda: os.getenv('USE_PRIVATE_ENDPOINT', 'false').lower() == 'true')
    
    # Azure OpenAI Service - from environment
    openai_endpoint: str = field(default_factory=lambda: os.getenv('AZURE_OPENAI_ENDPOINT', ''))
    openai_key: str = field(default_factory=lambda: os.getenv('AZURE_OPENAI_KEY', ''))
    openai_deployment: str = field(default_factory=lambda: os.getenv('AZURE_OPENAI_DEPLOYMENT', ''))
    openai_api_version: str = field(default_factory=lambda: os.getenv('AZURE_OPENAI_API_VERSION', '2023-06-01-preview'))
    
    # Azure Cognitive Search (for On Your Data) - from environment
    cog_search_endpoint: Optional[str] = field(default_factory=lambda: os.getenv('AZURE_SEARCH_ENDPOINT'))
    cog_search_key: Optional[str] = field(default_factory=lambda: os.getenv('AZURE_SEARCH_KEY'))
    cog_search_index: Optional[str] = field(default_factory=lambda: os.getenv('AZURE_SEARCH_INDEX'))
    enable_search: bool = field(default_factory=lambda: os.getenv('ENABLE_AZURE_SEARCH', 'true').lower() == 'true')
    
    # STT / TTS Settings - from environment
    stt_locales: List[str] = field(default_factory=lambda: os.getenv('STT_LOCALES', 'en-US,de-DE,es-ES,fr-FR,it-IT,ja-JP,ko-KR,zh-CN').split(','))
    tts_voice: str = field(default_factory=lambda: os.getenv('TTS_VOICE', 'en-US-AvaMultilingualNeural'))
    
    # Avatar Settings - from environment
    avatar_character: str = field(default_factory=lambda: os.getenv('AVATAR_CHARACTER', 'lisa'))
    avatar_style: str = field(default_factory=lambda: os.getenv('AVATAR_STYLE', 'casual'))
    avatar_background_color: str = field(default_factory=lambda: os.getenv('AVATAR_BACKGROUND_COLOR', '#FFFFFFFF'))
    
    # Conversation Settings - from environment
    continuous_conversation: bool = field(default_factory=lambda: os.getenv('CONTINUOUS_CONVERSATION', 'false').lower() == 'true')
    enable_quick_reply: bool = field(default_factory=lambda: os.getenv('ENABLE_QUICK_REPLY', 'false').lower() == 'true')
    
    # System
    system_prompt: str = field(default_factory=lambda: os.getenv('SYSTEM_PROMPT', 'You are an AI assistant that helps people find information.'))
    
    # WebRTC Configuration
    ice_server_url: str = field(default_factory=lambda: os.getenv('ICE_SERVER_URL', ''))
    ice_server_username: str = field(default_factory=lambda: os.getenv('ICE_SERVER_USERNAME', ''))
    ice_server_credential: str = field(default_factory=lambda: os.getenv('ICE_SERVER_CREDENTIAL', ''))
    
    def validate(self) -> bool:
        """Validate that required configuration is present"""
        if not self.speech_key:
            raise ValueError("AZURE_SPEECH_KEY is required in .env file")
        if not self.speech_region:
            raise ValueError("AZURE_SPEECH_REGION is required in .env file")
        if not self.openai_endpoint:
            raise ValueError("AZURE_OPENAI_ENDPOINT is required in .env file")
        if not self.openai_key:
            raise ValueError("AZURE_OPENAI_KEY is required in .env file")
        if not self.openai_deployment:
            raise ValueError("AZURE_OPENAI_DEPLOYMENT is required in .env file")
        return True
    
    def get_speech_endpoint(self) -> str:
        """Get the speech service endpoint"""
        if self.use_private_endpoint and self.private_endpoint:
            return self.private_endpoint
        return f"https://{self.speech_region}.api.cognitive.microsoft.com"
    
    def get_tts_websocket_url(self) -> str:
        """Get the TTS WebSocket URL"""
        if self.use_private_endpoint and self.private_endpoint:
            endpoint = self.private_endpoint.replace("https://", "")
            return f"wss://{endpoint}/tts/cognitiveservices/websocket/v1?enableTalkingAvatar=true"
        return f"wss://{self.speech_region}.tts.speech.microsoft.com/cognitiveservices/websocket/v1?enableTalkingAvatar=true"
    
    def get_stt_websocket_url(self) -> str:
        """Get the STT WebSocket URL"""
        return f"wss://{self.speech_region}.stt.speech.microsoft.com/speech/universal/v2"
    
    def get_avatar_token_url(self) -> str:
        """Get the avatar relay token URL"""
        if self.use_private_endpoint and self.private_endpoint:
            endpoint = self.private_endpoint.replace("https://", "")
            return f"https://{endpoint}/tts/cognitiveservices/avatar/relay/token/v1"
        return f"https://{self.speech_region}.tts.speech.microsoft.com/cognitiveservices/avatar/relay/token/v1"
    
    def to_dict(self) -> dict:
        """Convert config to dictionary for display"""
        return {
            "Speech Region": self.speech_region,
            "Avatar Character": self.avatar_character,
            "Avatar Style": self.avatar_style,
            "TTS Voice": self.tts_voice,
            "OpenAI Deployment": self.openai_deployment,
            "Search Enabled": self.enable_search,
            "Private Endpoint": self.use_private_endpoint
        }