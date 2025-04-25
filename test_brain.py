import asyncio
from core.brain.brain import JarvisBrain

async def test_questions(brain):
    questions = [
        "What is the capital of France?",
        "Can you help me write a simple Python function to calculate factorial?",
        "What are the main differences between Python and JavaScript?",
        "Explain quantum computing in simple terms.",
        "What's the weather like today?"
    ]
    
    for question in questions:
        print(f"\nQuestion: {question}")
        response = await brain.process_input(question)
        print(f"Response: {response}")
        print("-" * 80)

async def main():
    # Initialize JarvisBrain
    brain = JarvisBrain()
    
    try:
        # Start the brain
        await brain.start()
        
        # Test basic greeting
        print("\nTesting basic greeting:")
        response = await brain.process_input("Hello Jarvis")
        print(f"Response: {response}")
        
        # Test various questions
        print("\nTesting various questions:")
        await test_questions(brain)
        
        # Get memory summary
        memory_summary = brain.get_memory_summary()
        print(f"\nMemory Summary: {memory_summary}")
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        # Shutdown the brain
        await brain.shutdown()

if __name__ == "__main__":
    asyncio.run(main()) 