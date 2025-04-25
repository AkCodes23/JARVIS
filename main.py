"""
Main entry point for Jarvis Voice Assistant.
"""

import os
import sys
import logging
import asyncio
import signal
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import core components
from core.brain import JarvisBrain
from core.voice.manager import VoiceManager
from core.llm.manager import LLMManager
from core.memory.manager import MemoryManager
from core.rag.manager import RAGManager
from core.agent.manager import AgentManager
from core.tools.manager import ToolManager

def setup_directories():
    """Create necessary directories if they don't exist."""
    directories = [
        "data/logs",
        "data/voice",
        "data/conversation",
        "models/wake_word",
        "models/nlp",
        "models/llm",
        "models/rag"
    ]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def setup_logging():
    """Set up logging configuration."""
    log_dir = Path("data/logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Set up file handler for all logs
    file_handler = logging.FileHandler(log_dir / "jarvis.log", mode='a')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.addHandler(file_handler)
    
    # Set up component-specific loggers
    loggers = {
        "jarvis.main": logging.INFO,  # Show all main logs
        "jarvis.voice": logging.WARNING,  # Only show voice warnings/errors
        "jarvis.llm": logging.WARNING,  # Only show LLM warnings/errors
        "jarvis.memory": logging.WARNING,  # Only show memory warnings/errors
        "jarvis.rag": logging.WARNING,  # Only show RAG warnings/errors
        "jarvis.agent": logging.WARNING,  # Only show agent warnings/errors
        "jarvis.tools": logging.WARNING,  # Only show tools warnings/errors
        "httpx": logging.WARNING,  # Hide HTTP request logs
        "comtypes": logging.WARNING,  # Hide comtypes logs
    }
    
    for logger_name, level in loggers.items():
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        # Prevent propagation to root logger to avoid duplicate logs
        logger.propagate = False
        # Add handlers directly to component loggers
        logger.addHandler(file_handler)

def format_response(response):
    """Format the response from the LLM."""
    if isinstance(response, tuple):
        response = response[0]  # Get just the text part
    
    # If response is too long, summarize it
    if len(response) > 200:
        # Split into sentences and clean up
        sentences = [s.strip() for s in response.split('.') if s.strip()]
        # Take first 2 sentences or less
        summary = '. '.join(sentences[:2]) + '.'
        return summary
    
    return response

def main():
    """Main entry point for the Jarvis assistant."""
    # Set up directories and logging
    setup_directories()
    setup_logging()
    
    logger = logging.getLogger("jarvis.main")
    logger.info("Starting Jarvis Voice Assistant...")
    
    try:
        # Initialize the brain
        brain = JarvisBrain()
        
        # Welcome message
        logger.info("Jarvis initialized. Say the wake word or press Enter to start.")
        
        # Run the async main function
        asyncio.run(async_main(brain))
        
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt, shutting down...")
    except Exception as e:
        logger.error(f"Error initializing Jarvis: {str(e)}")
        sys.exit(1)

async def async_main(brain):
    """Async main function for voice interaction."""
    logger = logging.getLogger("jarvis.main")
    try:
        # Start the brain and all components
        await brain.start()
        
        # Initial introduction
        introduction = "Hi, I am Jarvis. What can I do for you today?"
        print("\nJarvis: " + introduction)
        await brain.voice_manager.text_to_speech(introduction)
        
        # Conversation loop
        while True:
            try:
                # Record audio
                audio_file = await brain.voice_manager.record_audio(duration=5.0)
                
                # Convert speech to text
                text = await brain.voice_manager.speech_to_text(audio_file)
                if not text:
                    logger.warning("No speech detected, continuing...")
                    continue
                    
                # Print user's input
                print("\nYou: " + text)
                
                # Check if user wants to end the conversation
                if "thank you" in text.lower():
                    farewell = "You're welcome! Have a great day!"
                    print("\nJarvis: " + farewell)
                    await brain.voice_manager.text_to_speech(farewell)
                    break
                    
                # Process the text input
                response = await brain.process_input(text)
                formatted_response = format_response(response)
                
                # Print Jarvis's response
                print("\nJarvis: " + formatted_response)
                
                # Speak summarized response
                await brain.voice_manager.text_to_speech(formatted_response)
                
            except KeyboardInterrupt:
                print("\nInterrupted by user, shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in conversation loop: {str(e)}")
                error_msg = "I encountered an error. Please try again."
                print("\nJarvis: " + error_msg)
                await brain.voice_manager.text_to_speech(error_msg)
                
    except Exception as e:
        logger.error(f"Error in async main: {str(e)}")
    finally:
        try:
            await brain.shutdown()
            logger.info("Jarvis shut down successfully.")
        except Exception as e:
            logger.error(f"Error during shutdown: {str(e)}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down Jarvis...")
        sys.exit(0)
