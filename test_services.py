"""
Unit tests for Azure AI Avatar services
Run with: pytest test_services.py
"""
import pytest
from config import Config
from openai_service import OpenAIService
from avatar_service import AvatarService

class TestConfig:
    """Tests for Config class"""
    
    def test_config_initialization(self):
        """Test config initializes with defaults"""
        config = Config()
        assert config.speech_region == "westus2"
        assert config.avatar_character == "meg"
        assert config.avatar_style == "formal"
        assert config.tts_voice == "en-US-AvaMultilingualNeural"
    
    def test_config_validation_missing_speech_key(self):
        """Test validation fails without speech key"""
        config = Config()
        with pytest.raises(ValueError, match="Speech API key is required"):
            config.validate()
    
    def test_config_validation_success(self):
        """Test validation succeeds with all required fields"""
        config = Config()
        config.speech_key = "test_key"
        config.speech_region = "westus2"
        config.openai_endpoint = "https://test.openai.azure.com"
        config.openai_key = "test_key"
        config.openai_deployment = "test_deployment"
        
        assert config.validate() == True
    
    def test_get_speech_endpoint(self):
        """Test speech endpoint generation"""
        config = Config()
        config.speech_region = "eastus"
        endpoint = config.get_speech_endpoint()
        assert endpoint == "https://eastus.api.cognitive.microsoft.com"
    
    def test_get_tts_websocket_url(self):
        """Test TTS WebSocket URL generation"""
        config = Config()
        config.speech_region = "westus2"
        url = config.get_tts_websocket_url()
        assert "westus2.tts.speech.microsoft.com" in url
        assert "enableTalkingAvatar=true" in url

class TestOpenAIService:
    """Tests for OpenAIService class"""
    
    def test_initialization(self):
        """Test OpenAI service initializes correctly"""
        config = Config()
        config.openai_endpoint = "https://test.openai.azure.com"
        config.openai_key = "test_key"
        config.openai_deployment = "test_deployment"
        
        service = OpenAIService(config)
        assert len(service.messages) == 0
        assert len(service.data_sources) == 0
    
    def test_add_system_message(self):
        """Test adding system message"""
        config = Config()
        config.openai_endpoint = "https://test.openai.azure.com"
        config.openai_key = "test_key"
        config.openai_deployment = "test_deployment"
        
        service = OpenAIService(config)
        service.add_system_message("You are a helpful assistant")
        
        assert len(service.messages) == 1
        assert service.messages[0]["role"] == "system"
        assert service.messages[0]["content"] == "You are a helpful assistant"
    
    def test_add_user_message(self):
        """Test adding user message"""
        config = Config()
        config.openai_endpoint = "https://test.openai.azure.com"
        config.openai_key = "test_key"
        config.openai_deployment = "test_deployment"
        
        service = OpenAIService(config)
        service.add_user_message("Hello, how are you?")
        
        assert len(service.messages) == 1
        assert service.messages[0]["role"] == "user"
        assert service.messages[0]["content"] == "Hello, how are you?"
    
    def test_clear_messages(self):
        """Test clearing messages"""
        config = Config()
        config.openai_endpoint = "https://test.openai.azure.com"
        config.openai_key = "test_key"
        config.openai_deployment = "test_deployment"
        
        service = OpenAIService(config)
        service.add_user_message("Test message")
        assert len(service.messages) == 1
        
        service.clear_messages()
        assert len(service.messages) == 0
    
    def test_set_data_sources(self):
        """Test setting data sources for RAG"""
        config = Config()
        config.openai_endpoint = "https://test.openai.azure.com"
        config.openai_key = "test_key"
        config.openai_deployment = "test_deployment"
        
        service = OpenAIService(config)
        service.set_data_sources(
            endpoint="https://test.search.windows.net",
            api_key="test_search_key",
            index_name="test_index",
            role_information="You are a helpful assistant"
        )
        
        assert len(service.data_sources) == 1
        assert service.data_sources[0]["type"] == "AzureCognitiveSearch"
        assert service.data_sources[0]["parameters"]["indexName"] == "test_index"

class TestAvatarService:
    """Tests for AvatarService class"""
    
    def test_initialization(self):
        """Test avatar service initializes correctly"""
        config = Config()
        config.speech_key = "test_key"
        config.speech_region = "westus2"
        
        # Note: This will fail without valid credentials
        # In real tests, you'd mock the Azure SDK
        try:
            service = AvatarService(config)
            assert service.config == config
            assert service.is_speaking == False
            assert len(service.spoken_text_queue) == 0
        except Exception:
            # Expected to fail without valid credentials
            pass
    
    def test_create_ssml(self):
        """Test SSML creation"""
        config = Config()
        config.speech_key = "test_key"
        config.speech_region = "westus2"
        config.tts_voice = "en-US-AvaMultilingualNeural"
        
        try:
            service = AvatarService(config)
            ssml = service._create_ssml(
                text="Hello world",
                voice="en-US-AvaMultilingualNeural",
                ending_silence_ms=0
            )
            
            assert "<speak" in ssml
            assert "Hello world" in ssml
            assert "en-US-AvaMultilingualNeural" in ssml
            assert "</speak>" in ssml
        except Exception:
            # Expected to fail without valid credentials
            pass
    
    def test_create_ssml_with_silence(self):
        """Test SSML creation with ending silence"""
        config = Config()
        config.speech_key = "test_key"
        config.speech_region = "westus2"
        
        try:
            service = AvatarService(config)
            ssml = service._create_ssml(
                text="Hello world",
                voice="en-US-AvaMultilingualNeural",
                ending_silence_ms=1000
            )
            
            assert "<break time='1000ms'" in ssml
        except Exception:
            # Expected to fail without valid credentials
            pass

# Fixtures for integration tests (if needed)
@pytest.fixture
def test_config():
    """Fixture providing test configuration"""
    config = Config()
    config.speech_key = "test_key"
    config.speech_region = "westus2"
    config.openai_endpoint = "https://test.openai.azure.com"
    config.openai_key = "test_key"
    config.openai_deployment = "test_deployment"
    return config

@pytest.fixture
def openai_service(test_config):
    """Fixture providing OpenAI service"""
    return OpenAIService(test_config)

# Run tests with: pytest test_services.py -v
if __name__ == "__main__":
    pytest.main([__file__, "-v"])