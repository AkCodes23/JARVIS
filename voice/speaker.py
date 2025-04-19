"""
Text-to-speech module for Jarvis.
Handles converting text to speech.
"""

import logging
from typing import Dict, Any, Optional

class VoiceSpeaker:
    """Handles text-to-speech conversion for Jarvis."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the voice speaker with configuration."""
        self.logger = logging.getLogger("jarvis.voice.speaker")
        self.config = config.get("voice", {})
        self.tts_provider = self.config.get("tts_provider", "local")
        self.voice_id = self.config.get("voice_id", "default")
        self.rate = self.config.get("rate", 1.0)
        self.volume = self.config.get("volume", 1.0)
        
        self.logger.info(f"Initializing Voice Speaker with provider: {self.tts_provider}")
        
        # Initialize specific provider
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the chosen TTS provider."""
        if self.tts_provider == "local":
            try:
                import pyttsx3
                self.engine = pyttsx3.init()
                self.engine.setProperty('rate', int(self.engine.getProperty('rate') * self.rate))
                self.engine.setProperty('volume', self.volume)
                
                # Set voice if specified
                if self.voice_id != "default":
                    voices = self.engine.getProperty('voices')
                    for voice in voices:
                        if self.voice_id in voice.id:
                            self.engine.setProperty('voice', voice.id)
                            break
                
                self.logger.info("Local TTS engine initialized")
            except ImportError:
                self.logger.error("Failed to import pyttsx3. Please install it.")
                raise
        elif self.tts_provider == "elevenlabs":
            try:
                import elevenlabs
                # Set API key from environment
                import os
                api_key = os.getenv("ELEVENLABS_API_KEY")
                if not api_key:
                    self.logger.warning("ELEVENLABS_API_KEY not found in environment variables")
                else:
                    elevenlabs.set_api_key(api_key)
                self.logger.info("ElevenLabs TTS initialized")
            except ImportError:
                self.logger.error("Failed to import elevenlabs. Please install it.")
                raise
        else:
            self.logger.warning(f"Unsupported TTS provider: {self.tts_provider}")
            raise ValueError(f"Unsupported TTS provider: {self.tts_provider}")
    
    def speak(self, text: str, block: bool = True) -> None:
        """
        Convert text to speech and play it.
        
        Args:
            text: The text to speak
            block: Whether to block until speech is complete
        """
        if not text:
            return
            
        self.logger.info(f"Speaking: {text[:50]}...")
        
        if self.tts_provider == "local":
            self._speak_local(text, block)
        elif self.tts_provider == "elevenlabs":
            self._speak_elevenlabs(text)
        else:
            self.logger.error(f"Unsupported TTS provider: {self.tts_provider}")
    
    def _speak_local(self, text: str, block: bool) -> None:
        """Use local TTS engine (pyttsx3)."""
        try:
            if block:
                self.engine.say(text)
                self.engine.runAndWait()
            else:
                # Start in a new thread for non-blocking
                import threading
                def speak_thread():
                    self.engine.say(text)
                    self.engine.runAndWait()
                
                thread = threading.Thread(target=speak_thread)
                thread.daemon = True
                thread.start()
        except Exception as e:
            self.logger.error(f"Error in local TTS: {str(e)}")
    
    def _speak_elevenlabs(self, text: str) -> None:
        """Use ElevenLabs for TTS."""
        try:
            import elevenlabs
            import threading
            
            def speak_thread():
                audio = elevenlabs.generate(
                    text=text,
                    voice=self.voice_id,
                    model="eleven_multilingual_v1"
                )
                elevenlabs.play(audio)
            
            thread = threading.Thread(target=speak_thread)
            thread.daemon = True
            thread.start()
        except Exception as e:
            self.logger.error(f"Error in ElevenLabs TTS: {str(e)}")
