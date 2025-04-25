import sounddevice as sd
import soundfile as sf
import numpy as np
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def record_audio(duration=5, output_file="test_recording.wav", sample_rate=16000):
    """Record audio using sounddevice and save to a WAV file."""
    try:
        logger.info(f"Starting audio recording for {duration} seconds")
        print(f"Recording for {duration} seconds...")
        
        # Record audio
        recording = sd.rec(
            int(duration * sample_rate),
            samplerate=sample_rate,
            channels=1,
            dtype=np.int16
        )
        sd.wait()  # Wait until recording is finished
        print("Recording finished.")
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Save as WAV file
        logger.info(f"Saving audio to: {output_file}")
        sf.write(output_file, recording, sample_rate)
        
        # Verify file was created
        if os.path.exists(output_file):
            logger.info(f"Audio file created successfully: {output_file}")
            print(f"Audio saved to: {output_file}")
            return output_file
        else:
            logger.error(f"Failed to create audio file: {output_file}")
            print(f"Error: Failed to create audio file: {output_file}")
            return None
            
    except Exception as e:
        logger.error(f"Error recording audio: {str(e)}")
        print(f"Error: {str(e)}")
        return None

if __name__ == "__main__":
    try:
        # Set output file path
        output_file = os.path.join("data", "voice", "test_recording.wav")
        
        # Record audio
        record_audio(output_file=output_file)
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        print(f"Error: {str(e)}") 