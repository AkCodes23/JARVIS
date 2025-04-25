import asyncio
import logging
from core.brain.brain import JarvisBrain

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_voice_llm():
    brain = None
    try:
        # Initialize Jarvis
        brain = JarvisBrain()
        await brain.start()
        
        print("\nStarting voice interaction with Jarvis...")
        print("Jarvis will introduce itself and then listen for your input.")
        print("Please speak after Jarvis's introduction.")
        print("Say 'thank you' to end the conversation.")
        
        # Initial introduction
        introduction = "Hi, I am Jarvis. What can I do for you today?"
        await brain.voice_manager.text_to_speech(introduction)
        
        # Conversation loop
        while True:
            # Record audio
            audio_file = await brain.voice_manager.record_audio(duration=5.0)
            
            # Convert speech to text
            text = await brain.voice_manager.speech_to_text(audio_file)
            if not text:
                continue
                
            # Check if user wants to end the conversation
            if "thank you" in text.lower():
                farewell = "You're welcome! Have a great day!"
                await brain.voice_manager.text_to_speech(farewell)
                break
                
            # Process the text input
            response = await brain.process_input(text)
            print(f"\nJarvis's response: {response}")
            
            # Convert response to speech
            await brain.voice_manager.text_to_speech(response)
        
    except Exception as e:
        logger.error(f"Error in voice interaction test: {str(e)}", exc_info=True)
    finally:
        if brain:
            await brain.shutdown()

if __name__ == "__main__":
    asyncio.run(test_voice_llm()) 