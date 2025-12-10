"""Azure Avatar Service - Handles TTS and Avatar synthesis"""
import azure.cognitiveservices.speech as speechsdk
from typing import Optional, List
from config import Config
import html
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AvatarService:
    """Service for managing Azure Avatar and TTS"""
    
    def __init__(self, config: Config):
        """
        Initialize Avatar Service
        
        Args:
            config: Configuration object with Azure credentials
        """
        self.config = config
        self.speech_config = None
        self.avatar_synthesizer = None
        self.is_speaking = False
        self.spoken_text_queue: List[str] = []
        
        self._initialize_speech_config()
    
    def _initialize_speech_config(self):
        """Initialize Azure Speech SDK configuration"""
        try:
            if self.config.use_private_endpoint and self.config.private_endpoint:
                endpoint_url = self.config.get_tts_websocket_url()
                self.speech_config = speechsdk.SpeechConfig(
                    subscription=self.config.speech_key,
                    endpoint=endpoint_url
                )
            else:
                self.speech_config = speechsdk.SpeechConfig(
                    subscription=self.config.speech_key,
                    region=self.config.speech_region
                )
            
            # Set the voice
            self.speech_config.speech_synthesis_voice_name = self.config.tts_voice
            
            logger.info("Speech config initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing speech config: {e}")
            raise
    
    def create_avatar_synthesizer(self) -> bool:
        """
        Create avatar synthesizer with avatar configuration
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create avatar config
            avatar_config = speechsdk.avatarsynthesizer.AvatarConfig(
                character=self.config.avatar_character,
                style=self.config.avatar_style
            )
            
            # Create avatar synthesizer
            self.avatar_synthesizer = speechsdk.avatarsynthesizer.AvatarSynthesizer(
                speech_config=self.speech_config,
                avatar_config=avatar_config
            )
            
            logger.info(f"Avatar synthesizer created: {self.config.avatar_character} - {self.config.avatar_style}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating avatar synthesizer: {e}")
            return False
    
    def speak(self, text: str, voice: Optional[str] = None, ending_silence_ms: int = 0) -> bool:
        """
        Synthesize speech with avatar
        
        Args:
            text: Text to speak
            voice: Optional voice override
            ending_silence_ms: Milliseconds of silence at the end
            
        Returns:
            bool: True if successful, False otherwise
        """
        if self.is_speaking:
            self.spoken_text_queue.append(text)
            return True
        
        return self._speak_next(text, voice, ending_silence_ms)
    
    def _speak_next(self, text: str, voice: Optional[str] = None, ending_silence_ms: int = 0) -> bool:
        """
        Internal method to speak the next item
        
        Args:
            text: Text to speak
            voice: Optional voice override
            ending_silence_ms: Milliseconds of silence at the end
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not text or not text.strip():
                return False
            
            voice_name = voice or self.config.tts_voice
            
            # Create SSML
            ssml = self._create_ssml(text, voice_name, ending_silence_ms)
            
            self.is_speaking = True
            
            # Use regular speech synthesizer if avatar not available
            if self.avatar_synthesizer:
                result = self.avatar_synthesizer.speak_ssml_async(ssml).get()
            else:
                audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
                synthesizer = speechsdk.SpeechSynthesizer(
                    speech_config=self.speech_config,
                    audio_config=audio_config
                )
                result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                logger.info(f"Speech synthesized successfully: {text[:50]}...")
                
                # Speak next in queue if any
                if self.spoken_text_queue:
                    next_text = self.spoken_text_queue.pop(0)
                    self._speak_next(next_text, voice, ending_silence_ms)
                else:
                    self.is_speaking = False
                    
                return True
                
            elif result.reason == speechsdk.ResultReason.Canceled:
                cancellation = result.cancellation_details
                logger.error(f"Speech synthesis canceled: {cancellation.reason}")
                if cancellation.reason == speechsdk.CancellationReason.Error:
                    logger.error(f"Error details: {cancellation.error_details}")
                self.is_speaking = False
                return False
                
        except Exception as e:
            logger.error(f"Error in speak: {e}")
            self.is_speaking = False
            return False
    
    def _create_ssml(self, text: str, voice: str, ending_silence_ms: int = 0) -> str:
        """
        Create SSML for speech synthesis
        
        Args:
            text: Text to speak
            voice: Voice name
            ending_silence_ms: Milliseconds of silence at the end
            
        Returns:
            str: SSML string
        """
        # HTML encode the text
        encoded_text = html.escape(text)
        
        # Base SSML
        ssml = f"""<speak version='1.0' xmlns='http://www.w3.org/2001/10/synthesis'
                     xmlns:mstts='http://www.w3.org/2001/mstts'
                     xml:lang='en-US'>
                  <voice name='{voice}'>
                    <mstts:ttsembedding>
                      <mstts:leadingsilence-exact value='0'/>
                      {encoded_text}"""
        
        # Add ending silence if specified
        if ending_silence_ms > 0:
            ssml += f"\n                      <break time='{ending_silence_ms}ms' />"
        
        ssml += """
                    </mstts:ttsembedding>
                  </voice>
                </speak>"""
        
        return ssml
    
    def stop_speaking(self) -> bool:
        """
        Stop current speech synthesis
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.spoken_text_queue.clear()
            
            if self.avatar_synthesizer:
                # Azure SDK doesn't have a direct stop method for avatar
                # We clear the queue and mark as not speaking
                self.is_speaking = False
                logger.info("Stopped speaking")
                return True
            
            self.is_speaking = False
            return True
            
        except Exception as e:
            logger.error(f"Error stopping speech: {e}")
            return False
    
    def disconnect(self):
        """Disconnect and cleanup resources"""
        try:
            self.stop_speaking()
            
            if self.avatar_synthesizer:
                # Close the synthesizer
                del self.avatar_synthesizer
                self.avatar_synthesizer = None
            
            logger.info("Avatar service disconnected")
            
        except Exception as e:
            logger.error(f"Error disconnecting: {e}")