"""
Wake word detection module for Jarvis.
"""

import logging
import json
import wave
import pyaudio
import numpy as np
from pathlib import Path
from typing import Optional, Dict, Any, Generator
import vosk
import torch
import torchaudio
import os
import urllib.request
import zipfile
import shutil

class WakeWordDetector:
    """Detects wake words in audio input."""
    
    def __init__(
        self,
        model_path: str = "models/wake_word",
        wake_word: str = "hey jarvis",
        sample_rate: int = 16000,
        channels: int = 1,
        chunk_size: int = 1024,
        format: int = pyaudio.paInt16
    ):
        """Initialize wake word detector."""
        self.logger = logging.getLogger(__name__)
        self.wake_word = wake_word.lower()
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = format
        
        # Initialize audio
        self.audio = pyaudio.PyAudio()
        self.stream = None
        
        # Load Vosk model
        self.model_path = Path(model_path)
        if not self.model_path.exists() or not any(self.model_path.iterdir()):
            self.logger.warning(f"Wake word model not found at: {model_path}")
            self.logger.info("Downloading Vosk model...")
            self._download_vosk_model()
            
        self.model = vosk.Model(str(self.model_path))
        self.recognizer = vosk.KaldiRecognizer(self.model, sample_rate)
        
    def _download_vosk_model(self):
        """Download and extract the Vosk model."""
        try:
            # Create model directory if it doesn't exist
            self.model_path.mkdir(parents=True, exist_ok=True)
            
            # Download the model
            model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
            zip_path = self.model_path / "model.zip"
            
            self.logger.info(f"Downloading model from {model_url}...")
            urllib.request.urlretrieve(model_url, zip_path)
            
            # Extract the model
            self.logger.info("Extracting model...")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(self.model_path)
            
            # Move files from the extracted directory to the model directory
            extracted_dir = next(self.model_path.glob("vosk-model-small-en-us-*"))
            for item in extracted_dir.iterdir():
                shutil.move(str(item), str(self.model_path))
            
            # Clean up
            shutil.rmtree(extracted_dir)
            zip_path.unlink()
            
            self.logger.info("Model downloaded and extracted successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to download model: {str(e)}")
            raise RuntimeError("Failed to download wake word model. Please download it manually from https://alphacephei.com/vosk/models")
        
    async def start_detecting(self) -> Generator[bool, None, None]:
        """Start detecting wake word in audio input."""
        try:
            # Open audio stream
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.logger.info("Started wake word detection")
            
            # Process audio chunks
            while True:
                data = self.stream.read(self.chunk_size)
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    text = result.get("text", "").lower()
                    
                    if self.wake_word in text:
                        self.logger.info(f"Wake word detected: {text}")
                        yield True
                    else:
                        yield False
                        
        except Exception as e:
            self.logger.error(f"Failed to start wake word detection: {e}")
            raise
        finally:
            self.stop_detecting()
            
    def stop_detecting(self) -> None:
        """Stop wake word detection."""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
                self.logger.info("Stopped wake word detection")
                
        except Exception as e:
            self.logger.error(f"Failed to stop wake word detection: {e}")
            raise
            
    async def close(self) -> None:
        """Close audio resources."""
        try:
            self.stop_detecting()
            self.audio.terminate()
            
        except Exception as e:
            self.logger.error(f"Failed to close audio resources: {e}")
            raise 