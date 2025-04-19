"""
Speech recognition module for Jarvis.
Handles converting speech to text.
"""

import logging
from typing import Optional, Callable, Dict, Any

class VoiceListener:
    """Handles speech-to-text conversion for Jarvis."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the voice listener with configuration."""
        self.logger = logging.getLogger("jarvis.voice.listener")
        self.config = config.get("voice", {})
        self.stt_provider = self.config.get("stt_provider", "whisper_local")
        self.wake_word = self.config.get("wake_word", "jarvis")
        self.enable_wake_word = self.config.get("enable_wake_word", True)
        
        self.logger.info(f"Initializing Voice Listener with provider: {self.stt_provider}")
        
        # Initialize specific provider
        self._initialize_provider()
    
    def _initialize_provider(self):
        """Initialize the chosen STT provider."""
        if self.stt_provider == "whisper_local":
            # Import here to avoid loading model unless needed
            try:
                import whisper
                self.model = whisper.load_model("base")
                self.logger.info("Whisper model loaded successfully")
            except ImportError:
                self.logger.error("Failed to import whisper. Please install it with 'pip install openai-whisper'")
                raise
        elif self.stt_provider == "google":
            try:
                import speech_recognition as sr
                self.recognizer = sr.Recognizer()
                self.logger.info("Google STT initialized")
            except ImportError:
                self.logger.error("Failed to import speech_recognition. Please install it.")
                raise
        else:
            self.logger.warning(f"Unsupported STT provider: {self.stt_provider}")
            raise ValueError(f"Unsupported STT provider: {self.stt_provider}")
    
    def listen(self, timeout: Optional[int] = None, phrase_time_limit: Optional[int] = None) -> Optional[str]:
        """
        Listen for speech and convert to text.
        
        Args:
            timeout: Time in seconds to wait before giving up
            phrase_time_limit: Maximum length of phrase to capture
            
        Returns:
            Transcribed text or None if nothing detected
        """
        self.logger.info("Listening for speech...")
        
        if self.stt_provider == "whisper_local":
            return self._listen_whisper(timeout, phrase_time_limit)
        elif self.stt_provider == "google":
            return self._listen_google(timeout, phrase_time_limit)
        else:
            self.logger.error(f"Unsupported STT provider: {self.stt_provider}")
            return None
    
    def _listen_whisper(self, timeout: Optional[int], phrase_time_limit: Optional[int]) -> Optional[str]:
        """Use Whisper for speech recognition."""
        import pyaudio
        import numpy as np
        import wave
        from tempfile import NamedTemporaryFile
        import os
        
        # Record audio to temporary file
        with NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
            temp_filename = temp_file.name
        
        # Audio recording parameters
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 1
        RATE = 16000
        
        # TODO: Implement wake word detection if enabled
        
        # Record audio (simplified version)
        p = pyaudio.PyAudio()
        stream = p.open(format=FORMAT,
                       channels=CHANNELS,
                       rate=RATE,
                       input=True,
                       frames_per_buffer=CHUNK)
        
        self.logger.info("Recording...")
        frames = []
        
        # Record for a fixed duration for this example
        # In a real implementation, this would be more sophisticated
        for i in range(0, int(RATE / CHUNK * (phrase_time_limit or 5))):
            data = stream.read(CHUNK)
            frames.append(data)
        
        self.logger.info("Recording finished")
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Save the audio file
        wf = wave.open(temp_filename, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()
        
        # Transcribe with Whisper
        try:
            result = self.model.transcribe(temp_filename)
            text = result["text"].strip()
            self.logger.info(f"Transcribed: {text}")
            
            # Clean up temp file
            os.unlink(temp_filename)
            
            return text
        except Exception as e:
            self.logger.error(f"Error transcribing audio: {str(e)}")
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
            return None
    
    def _listen_google(self, timeout: Optional[int], phrase_time_limit: Optional[int]) -> Optional[str]:
        """Use Google Speech Recognition."""
        import speech_recognition as sr
        
        r = self.recognizer
        with sr.Microphone() as source:
            self.logger.info("Adjusting for ambient noise...")
            r.adjust_for_ambient_noise(source)
            self.logger.info("Listening...")
            
            try:
                audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                self.logger.info("Audio captured, recognizing...")
                
                text = r.recognize_google(audio)
                self.logger.info(f"Recognized: {text}")
                return text
            except sr.WaitTimeoutError:
                self.logger.info("No speech detected within timeout")
                return None
            except sr.UnknownValueError:
                self.logger.info("Could not understand audio")
                return None
            except sr.RequestError as e:
                self.logger.error(f"Error requesting results from Google: {str(e)}")
                return None
