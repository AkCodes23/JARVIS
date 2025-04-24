"""
<<<<<<< HEAD
Main orchestration logic for Jarvis assistant.
Handles the flow of information between components.
"""

import os
import logging
from typing import Dict, Any, List, Optional

class JarvisBrain:
    """Core orchestration class for the Jarvis assistant."""
    
    def __init__(self, config_path: str = "config/default_config.yaml"):
        """Initialize the Jarvis brain with configuration."""
        self.config = self._load_config(config_path)
        self.logger = self._setup_logger()
        self.logger.info("Initializing Jarvis Brain...")
        
        # Initialize components (to be implemented)
        self.voice_manager = None  # Will manage voice I/O
        self.llm_manager = None  # Will manage LLM interactions
        self.memory_manager = None  # Will manage memory systems
        self.agent_manager = None  # Will manage agentic capabilities
        self.rag_manager = None  # Will manage RAG system
        
        self.logger.info("Jarvis Brain initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        import yaml
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Check for user config and override defaults
        user_config_path = os.path.join(os.path.dirname(config_path), "user_config.yaml")
        if os.path.exists(user_config_path):
            with open(user_config_path, 'r') as f:
                user_config = yaml.safe_load(f)
                # Deep merge configs (simplistic version)
                for key, value in user_config.items():
                    if key in config and isinstance(value, dict) and isinstance(config[key], dict):
                        config[key].update(value)
                    else:
                        config[key] = value
        
        return config
    
    def _setup_logger(self) -> logging.Logger:
        """Set up logging for the Jarvis system."""
        logger = logging.getLogger("jarvis")
        log_level = self.config.get("system", {}).get("log_level", "INFO")
        logger.setLevel(getattr(logging, log_level))
        
        # Create console handler
        ch = logging.StreamHandler()
        ch.setLevel(getattr(logging, log_level))
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(ch)
        
        return logger
    
    def process_input(self, user_input: str) -> str:
        """
        Process user input and return a response.
        Main processing pipeline for text input.
        """
        self.logger.info(f"Processing input: {user_input}")
        
        # To be implemented: Pass through all the necessary components
        # 1. Update memory with new input
        # 2. Use RAG to retrieve relevant information
        # 3. Use LLM to generate response
        # 4. Use agent to execute any actions
        
        # Placeholder response
        return f"You said: {user_input}. I'm still being implemented."
    
    def start(self):
        """Start the Jarvis assistant."""
        self.logger.info("Starting Jarvis...")
        
        # Initialize components here
        
        self.logger.info("Jarvis is ready.")
        # In a real implementation, this would start listening for voice input
        # or connect to a user interface
        
    def shutdown(self):
        """Properly shut down the Jarvis assistant."""
        self.logger.info("Shutting down Jarvis...")
        # Clean up resources
        
        self.logger.info("Jarvis shut down successfully.")


if __name__ == "__main__":
    # Simple test to ensure the class can be instantiated
    brain = JarvisBrain()
    response = brain.process_input("Hello Jarvis")
    print(response)
=======
Core brain module for Jarvis AI Assistant.
This module orchestrates all subsystems and manages the overall flow of the assistant.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml
from datetime import datetime

# Import core components
from .memory.short_term import ShortTermMemory
from .memory.long_term import LongTermMemory
from .memory.vector_store import VectorStore
from .llm.model_manager import ModelManager
from .llm.prompt_templates import PromptTemplates
from .llm.response_parser import ResponseParser
from .rag.document_processor import DocumentProcessor
from .rag.embeddings import EmbeddingGenerator
from .rag.retriever import ContentRetriever
from .rag.knowledge_base import KnowledgeBase
from .agent.planner import TaskPlanner
from .agent.executor import ActionExecutor
from .agent.verifier import ResultVerifier

# Import voice components
from ..voice.listener import SpeechListener
from ..voice.speaker import TextToSpeech
from ..voice.wake_word import WakeWordDetector

# Import utility components
from utils.logger import setup_logger
from utils.performance_metrics import PerformanceTracker
from utils.security import SecurityManager

class JarvisBrain:
    """Main orchestration class for the Jarvis AI Assistant."""
    
    def __init__(self, config_path: str = "config/default_config.yaml"):
        """Initialize the Jarvis brain with configuration."""
        self.logger = setup_logger(__name__)
        self.config = self._load_config(config_path)
        self.performance_tracker = PerformanceTracker()
        
        # Initialize core components
        self._init_memory_systems()
        self._init_llm_components()
        self._init_rag_components()
        self._init_agent_components()
        self._init_voice_components()
        self._init_security()
        
        self.logger.info("Jarvis brain initialized successfully")
    
    def _load_config(self, config_path: str) -> Dict:
        """Load configuration from YAML file."""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            return config
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _init_memory_systems(self):
        """Initialize memory systems."""
        self.short_term_memory = ShortTermMemory(
            max_tokens=self.config['memory']['short_term']['max_tokens'],
            expiration_minutes=self.config['memory']['short_term']['expiration_minutes']
        )
        
        self.long_term_memory = LongTermMemory(
            storage_path=self.config['memory']['long_term']['storage_path']
        )
        
        self.vector_store = VectorStore(
            provider=self.config['memory']['vector_store']['provider'],
            embedding_model=self.config['memory']['vector_store']['embedding_model'],
            collection_name=self.config['memory']['vector_store']['collection_name']
        )
    
    def _init_llm_components(self):
        """Initialize LLM-related components."""
        self.model_manager = ModelManager(
            provider=self.config['llm']['provider'],
            model=self.config['llm']['model'],
            temperature=self.config['llm']['temperature'],
            max_tokens=self.config['llm']['max_tokens']
        )
        
        self.prompt_templates = PromptTemplates()
        self.response_parser = ResponseParser()
    
    def _init_rag_components(self):
        """Initialize RAG components."""
        self.document_processor = DocumentProcessor(
            chunk_size=self.config['rag']['chunk_size'],
            chunk_overlap=self.config['rag']['chunk_overlap']
        )
        
        self.embedding_generator = EmbeddingGenerator(
            model=self.config['memory']['vector_store']['embedding_model']
        )
        
        self.content_retriever = ContentRetriever(
            vector_store=self.vector_store,
            max_documents=self.config['rag']['max_documents'],
            similarity_threshold=self.config['rag']['similarity_threshold']
        )
        
        self.knowledge_base = KnowledgeBase(
            document_processor=self.document_processor,
            embedding_generator=self.embedding_generator,
            content_retriever=self.content_retriever
        )
    
    def _init_agent_components(self):
        """Initialize agent components."""
        self.task_planner = TaskPlanner(
            model_manager=self.model_manager,
            prompt_templates=self.prompt_templates
        )
        
        self.action_executor = ActionExecutor(
            tools=self.config['agent']['tools']['enabled']
        )
        
        self.result_verifier = ResultVerifier(
            model_manager=self.model_manager
        )
    
    def _init_voice_components(self):
        """Initialize voice interface components."""
        self.wake_word_detector = WakeWordDetector(
            wake_word=self.config['voice']['wake_word']
        )
        
        self.speech_listener = SpeechListener(
            engine=self.config['voice']['speech_recognition']['engine'],
            language=self.config['voice']['speech_recognition']['language']
        )
        
        self.text_to_speech = TextToSpeech(
            engine=self.config['voice']['text_to_speech']['engine'],
            voice_id=self.config['voice']['text_to_speech']['voice_id'],
            rate=self.config['voice']['text_to_speech']['rate']
        )
    
    def _init_security(self):
        """Initialize security components."""
        self.security_manager = SecurityManager(
            encryption_key=self.config['security']['encryption_key'],
            ssl_verify=self.config['security']['ssl_verify']
        )
    
    async def process_input(self, input_text: str) -> str:
        """Process user input and generate response."""
        with self.performance_tracker.track("process_input"):
            # Store in short-term memory
            self.short_term_memory.add(input_text)
            
            # Retrieve relevant context
            context = await self.knowledge_base.retrieve_relevant_context(input_text)
            
            # Plan task
            plan = await self.task_planner.create_plan(input_text, context)
            
            # Execute actions
            results = await self.action_executor.execute_plan(plan)
            
            # Verify results
            verified_results = await self.result_verifier.verify_results(results)
            
            # Generate response
            response = await self.model_manager.generate_response(
                input_text=input_text,
                context=context,
                results=verified_results
            )
            
            # Store in long-term memory
            self.long_term_memory.store(input_text, response)
            
            return response
    
    async def process_voice_input(self, audio_data: bytes) -> bytes:
        """Process voice input and generate voice response."""
        with self.performance_tracker.track("process_voice_input"):
            # Convert speech to text
            text = await self.speech_listener.transcribe(audio_data)
            
            # Process text input
            response_text = await self.process_input(text)
            
            # Convert response to speech
            response_audio = await self.text_to_speech.synthesize(response_text)
            
            return response_audio
    
    async def ingest_document(self, document_path: str) -> None:
        """Ingest a document into the knowledge base."""
        with self.performance_tracker.track("ingest_document"):
            await self.knowledge_base.ingest_document(document_path)
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        return self.performance_tracker.get_metrics()
    
    async def shutdown(self):
        """Gracefully shutdown all components."""
        self.logger.info("Shutting down Jarvis brain...")
        
        # Save any pending data
        await self.long_term_memory.save()
        await self.vector_store.close()
        
        # Close connections
        await self.model_manager.close()
        await self.speech_listener.close()
        await self.text_to_speech.close()
        
        self.logger.info("Jarvis brain shutdown complete") 
>>>>>>> 05513f3 (Testing-1)
