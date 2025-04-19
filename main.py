"""
Main entry point for Jarvis Voice Assistant.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import core components
from core.brain import JarvisBrain
from voice.listener import VoiceListener
from voice.speaker import VoiceSpeaker

def main():
    """Main entry point for the Jarvis assistant."""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("data/logs/jarvis.log", mode='a')
        ]
    )
    
    logger = logging.getLogger("jarvis.main")
    logger.info("Starting Jarvis Voice Assistant...")
    
    try:
        # Initialize the brain
        brain = JarvisBrain()
        
        # Welcome message
        logger.info("Jarvis initialized. Say the wake word or press Enter to start.")
        
        # In a real implementation, this would be more sophisticated
        # For now, simple text input/output for testing
        while True:
            try:
                user_input = input("You: ")
                if user_input.lower() == "exit":
                    break
                
                response = brain.process_input(user_input)
                print(f"Jarvis: {response}")
                
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Error processing input: {str(e)}")
        
        # Clean shutdown
        brain.shutdown()
        logger.info("Jarvis shut down successfully.")
        
    except Exception as e:
        logger.error(f"Error initializing Jarvis: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
