"""
Voice Manager for handling speech-to-text and text-to-speech interactions.
"""

import os
import logging
import numpy as np
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import pyttsx3
from typing import Optional, Dict, Any, Generator, AsyncGenerator
from pathlib import Path
import asyncio
from .wake_word import WakeWordDetector
from .activity_detector import VoiceActivityDetector

class VoiceManager:
    """Manages voice interactions including speech recognition and synthesis."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the voice manager."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.recognizer = sr.Recognizer()
        self.is_listening = False
        
        # Initialize text-to-speech engine
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 150)  # Speed of speech
        self.tts_engine.setProperty('volume', 1.0)  # Volume (0.0 to 1.0)
        
        # Create data directory if it doesn't exist
        self.data_dir = os.path.abspath(os.path.join(os.getcwd(), "data", "voice"))
        os.makedirs(self.data_dir, exist_ok=True)
        self.logger.info(f"Voice data directory: {self.data_dir}")
        
        # Initialize wake word detector
        try:
            self.wake_word_detector = WakeWordDetector(
                model_path=config.get("wake_word_model_path", "models/wake_word"),
                wake_word=config.get("wake_word", "hey jarvis")
            )
        except Exception as e:
            self.logger.warning(f"Failed to initialize wake word detector: {str(e)}")
            self.wake_word_detector = None
        
        # Initialize voice activity detector
        try:
            self.activity_detector = VoiceActivityDetector(
                threshold=config.get("voice_activity_threshold", 0.01),
                silence_duration=config.get("silence_duration", 1.0),
                min_speech_duration=config.get("min_speech_duration", 0.3)
            )
        except Exception as e:
            self.logger.warning(f"Failed to initialize voice activity detector: {str(e)}")
            self.activity_detector = None
        
        # List available audio devices
        self._list_audio_devices()
        
    def _list_audio_devices(self):
        """List available audio devices for debugging."""
        try:
            devices = sd.query_devices()
            self.logger.info("Available audio devices:")
            for i, device in enumerate(devices):
                self.logger.info(f"[{i}] {device['name']} (inputs: {device['max_input_channels']}, outputs: {device['max_output_channels']})")
                
            # Set default device if not specified
            default_device = sd.query_devices(kind='input')
            self.logger.info(f"Using default input device: {default_device['name']}")
        except Exception as e:
            self.logger.error(f"Error listing audio devices: {str(e)}")
            
    async def initialize(self):
        """Initialize the voice components."""
        self.logger.info("Initializing voice manager...")
        try:
            # Adjust for ambient noise
            with sr.Microphone() as source:
                self.logger.info("Adjusting for ambient noise... Please wait.")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
            self.logger.info("Voice manager initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize voice manager: {str(e)}")
            raise
            
    async def listen_for_wake_word(self) -> AsyncGenerator[bool, None]:
        """Listen for wake word and yield True when detected."""
        async for detected in self.wake_word_detector.start_detecting():
            if detected:
                yield True
                
    async def record_audio(self, duration: float = 5.0) -> str:
        """Record audio for a specified duration and save to a file."""
        try:
            self.logger.info(f"Recording audio for {duration} seconds...")
            
            # Get default input device info
            device_info = sd.query_devices(kind='input')
            samplerate = int(device_info['default_samplerate'])
            channels = min(1, device_info['max_input_channels'])
            
            self.logger.info(f"Recording with: {device_info['name']} at {samplerate}Hz with {channels} channel(s)")
            
            # Record audio
            recording = sd.rec(
                int(samplerate * duration),
                samplerate=samplerate,
                channels=channels,
                dtype='float32',
                blocking=True
            )
            
            # Normalize audio
            recording = np.nan_to_num(recording)
            recording = np.clip(recording, -1.0, 1.0)
            
            # Save to a file in the data directory
            audio_file_path = os.path.join(self.data_dir, "recording.wav")
            self.logger.info(f"Saving audio to: {audio_file_path}")
            
            # Save to file
            sf.write(audio_file_path, recording, samplerate)
            
            # Verify file was created
            if os.path.exists(audio_file_path):
                file_size = os.path.getsize(audio_file_path)
                self.logger.info(f"Audio file created successfully: {audio_file_path} (size: {file_size} bytes)")
                if file_size == 0:
                    raise Exception("Audio file is empty. No audio was recorded.")
            else:
                raise Exception(f"Failed to create audio file: {audio_file_path}")
                
            return audio_file_path
            
        except Exception as e:
            self.logger.error(f"Error recording audio: {str(e)}")
            raise
            
    async def record_with_activity_detection(self) -> AsyncGenerator[bytes, None]:
        """Record audio with voice activity detection."""
        async for is_speaking, audio_data in self.activity_detector.start_detecting():
            if is_speaking:
                yield audio_data
                
    async def speech_to_text(self, audio_file: str) -> str:
        """Convert speech to text using Google's speech recognition."""
        try:
            if not os.path.exists(audio_file):
                self.logger.error(f"Audio file not found: {audio_file}")
                return ""
                
            file_size = os.path.getsize(audio_file)
            self.logger.info(f"Transcribing audio file: {audio_file} (size: {file_size} bytes)")
            
            if file_size == 0:
                self.logger.error("Audio file is empty")
                return ""
                
            # Use speech recognition
            with sr.AudioFile(audio_file) as source:
                audio = self.recognizer.record(source)
                
            # Try multiple recognition engines
            try:
                # First try Google's speech recognition
                text = self.recognizer.recognize_google(audio)
            except sr.UnknownValueError:
                self.logger.warning("Google Speech Recognition could not understand audio")
                try:
                    # Fallback to Sphinx
                    text = self.recognizer.recognize_sphinx(audio)
                except:
                    self.logger.warning("Sphinx could not understand audio")
                    return ""
            except sr.RequestError as e:
                self.logger.error(f"Could not request results from speech recognition service: {str(e)}")
                return ""
                
            self.logger.info(f"Transcription result: {text}")
            return text
            
        except Exception as e:
            self.logger.error(f"Error in speech-to-text: {str(e)}")
            return ""
            
    async def text_to_speech(self, text: str) -> None:
        """Convert text to speech using pyttsx3."""
        try:
            self.logger.info(f"Converting text to speech: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            self.logger.error(f"Error in text-to-speech: {str(e)}")
            
    async def shutdown(self) -> None:
        """Shutdown voice components."""
        try:
            if self.wake_word_detector:
                await self.wake_word_detector.close()
            if self.activity_detector:
                await self.activity_detector.close()
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")
            raise 