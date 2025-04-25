import asyncio
import logging
import os
from core.voice.manager import VoiceManager

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_voice_recording():
    voice_manager = None
    try:
        # Initialize voice manager
        voice_manager = VoiceManager({})
        await voice_manager.initialize()
        
        print("\nStarting voice recording test...")
        print("Please speak into your microphone when recording starts.")
        print("Recording will last for 5 seconds.")
        input("Press Enter to start recording...")
        
        # Record audio
        audio_file = await voice_manager.record_audio(duration=5.0)
        
        # Verify audio file exists and has content
        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return
            
        file_size = os.path.getsize(audio_file)
        if file_size == 0:
            logger.error("Audio file is empty")
            return
            
        logger.info(f"Audio file created: {audio_file} (size: {file_size} bytes)")
        
        # Convert to text
        text = await voice_manager.speech_to_text(audio_file)
        print(f"\nTranscribed text: {text}")
        
        if text:
            print("\nPlaying back response...")
            await voice_manager.text_to_speech("I heard you say: " + text)
        else:
            print("\nNo text was transcribed from the audio.")
        
    except Exception as e:
        logger.error(f"Error in voice recording test: {str(e)}", exc_info=True)
    finally:
        if voice_manager:
            await voice_manager.shutdown()

if __name__ == "__main__":
    asyncio.run(test_voice_recording()) 