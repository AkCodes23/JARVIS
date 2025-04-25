"""
Voice activity detection module for Jarvis.
"""

import logging
import numpy as np
import pyaudio
from typing import Optional, Generator, Tuple

class VoiceActivityDetector:
    """Detects voice activity in audio input."""
    
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        format: int = pyaudio.paInt16,
        threshold: float = 0.01,
        silence_duration: float = 1.0,
        min_speech_duration: float = 0.3
    ):
        """Initialize voice activity detector."""
        self.logger = logging.getLogger(__name__)
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = format
        self.threshold = threshold
        self.silence_duration = silence_duration
        self.min_speech_duration = min_speech_duration
        
        # Initialize audio
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
        # State variables
        self.is_speaking = False
        self.silence_frames = 0
        self.speech_frames = 0
        self.silence_threshold = int(silence_duration * sample_rate / chunk_size)
        self.min_speech_frames = int(min_speech_duration * sample_rate / chunk_size)
        
    async def start_detecting(self) -> Generator[Tuple[bool, bytes], None, None]:
        """Start detecting voice activity in audio input."""
        try:
            # Open audio stream
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.logger.info("Started voice activity detection")
            
            # Process audio chunks
            while True:
                data = self.stream.read(self.chunk_size)
                audio_data = np.frombuffer(data, dtype=np.int16)
                
                # Calculate audio level
                level = np.abs(audio_data).mean() / 32768.0  # Normalize to [0, 1]
                
                # Update state
                if level > self.threshold:
                    self.silence_frames = 0
                    self.speech_frames += 1
                    
                    if not self.is_speaking and self.speech_frames >= self.min_speech_frames:
                        self.is_speaking = True
                        self.logger.info("Speech detected")
                        
                else:
                    self.speech_frames = 0
                    self.silence_frames += 1
                    
                    if self.is_speaking and self.silence_frames >= self.silence_threshold:
                        self.is_speaking = False
                        self.logger.info("Speech ended")
                        
                yield self.is_speaking, data
                
        except Exception as e:
            self.logger.error(f"Failed to start voice activity detection: {e}")
            raise
        finally:
            self.stop_detecting()
            
    def stop_detecting(self) -> None:
        """Stop voice activity detection."""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
                self.logger.info("Stopped voice activity detection")
                
        except Exception as e:
            self.logger.error(f"Failed to stop voice activity detection: {e}")
            raise
            
    async def close(self) -> None:
        """Close audio resources."""
        try:
            self.stop_detecting()
            self.audio.terminate()
            
        except Exception as e:
            self.logger.error(f"Failed to close audio resources: {e}")
            raise 