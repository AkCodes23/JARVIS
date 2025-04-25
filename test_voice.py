import asyncio
from core.brain.brain import JarvisBrain

async def test_voice_interaction():
    # Initialize Jarvis
    brain = JarvisBrain()
    await brain.start()
    
    print("Testing voice interaction with Jarvis...")
    print("Jarvis will introduce itself and then listen for your input.")
    print("Please speak after Jarvis's introduction.")
    
    # Test voice interaction
    response = await brain.process_voice_input(duration=5.0)
    print(f"Jarvis's response: {response}")
    
    # Shutdown
    await brain.shutdown()

if __name__ == "__main__":
    asyncio.run(test_voice_interaction()) 