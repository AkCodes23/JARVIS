"""
Agent Manager for handling user interactions and tool execution.
"""

import logging
from typing import Dict, Any, Optional
import re

from core.llm.manager import LLMManager
from core.memory.manager import MemoryManager
from core.tools.manager import ToolManager

logger = logging.getLogger(__name__)

class AgentManager:
    """Manages agent interactions and tool execution."""
    
    def __init__(self, config: Dict[str, Any], llm_manager: LLMManager, memory_manager: MemoryManager, tool_manager: ToolManager):
        """Initialize the agent manager."""
        self.config = config
        self.logger = logger
        self.llm_manager = llm_manager
        self.memory_manager = memory_manager
        self.tool_manager = tool_manager
        
        # Common websites mapping
        self.website_mapping = {
            'google': 'google.com',
            'youtube': 'youtube.com',
            'facebook': 'facebook.com',
            'twitter': 'twitter.com',
            'instagram': 'instagram.com',
            'linkedin': 'linkedin.com',
            'github': 'github.com',
            'reddit': 'reddit.com',
            'amazon': 'amazon.com',
            'netflix': 'netflix.com',
            'spotify': 'spotify.com',
            'gmail': 'gmail.com',
            'outlook': 'outlook.com',
            'yahoo': 'yahoo.com',
            'bing': 'bing.com',
            'duckduckgo': 'duckduckgo.com',
            'wikipedia': 'wikipedia.org',
            'stackoverflow': 'stackoverflow.com',
            'medium': 'medium.com',
            'quora': 'quora.com'
        }
        
        # Command patterns
        self.command_patterns = {
            'open_website': r'open\s+(?:website|site|url)?\s+(?:at|:)?\s*(https?://[^\s]+|[^\s]+\.(?:com|org|net|edu|gov|io|co|uk|de|fr|jp|ru|br|cn|in|au|ca|mx|es|it|nl|se|no|dk|fi|pl|ch|at|be|pt|gr|tr|za|sg|my|id|ph|vn|th|kr|jp|cn|tw|hk|mo|my|sg|id|ph|vn|th|kr|jp|cn|tw|hk|mo))',
            'open_simple_website': r'open\s+([a-zA-Z0-9]+)',
            'open_app': r'open\s+(?:app|application|program)?\s+(?:called|named)?\s+([a-zA-Z0-9\s]+)',
            'execute_command': r'execute\s+(?:command|cmd)?\s+(?:called|named)?\s+([a-zA-Z0-9\s]+)'
        }
        
    async def initialize(self):
        """Initialize the agent manager."""
        self.logger.info("Initializing agent manager...")
        
    async def process_input(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        Process user input and execute appropriate actions.
        
        Args:
            user_input: The user's input text
            context: Optional context information
            
        Returns:
            str: Response to the user
        """
        try:
            # Check for command patterns
            for command_type, pattern in self.command_patterns.items():
                match = re.search(pattern, user_input, re.IGNORECASE)
                if match:
                    return await self._handle_command(command_type, match, user_input)
            
            # If no command pattern matches, process as a normal query
            return await self._process_normal_query(user_input, context)
            
        except Exception as e:
            self.logger.error(f"Error processing input: {str(e)}")
            return f"I encountered an error while processing your request: {str(e)}"
    
    async def _handle_command(self, command_type: str, match: re.Match, user_input: str) -> str:
        """Handle different types of commands."""
        try:
            if command_type == 'open_website':
                url = match.group(1)
                success = await self.tool_manager.open_website(url)
                return f"I've opened the website {url}" if success else f"Sorry, I couldn't open the website {url}"
                
            elif command_type == 'open_simple_website':
                site_name = match.group(1).lower()
                if site_name in self.website_mapping:
                    url = self.website_mapping[site_name]
                    success = await self.tool_manager.open_website(url)
                    return f"I've opened {site_name}" if success else f"Sorry, I couldn't open {site_name}"
                else:
                    return f"I don't know how to open {site_name}. Please provide a full URL."
                
            elif command_type == 'open_app':
                app_name = match.group(1).strip()
                success = await self.tool_manager.open_application(app_name)
                return f"I've opened {app_name}" if success else f"Sorry, I couldn't open {app_name}"
                
            elif command_type == 'execute_command':
                command = match.group(1).strip()
                success = await self.tool_manager.execute_command(command)
                return f"I've executed the command" if success else f"Sorry, I couldn't execute the command"
                
            else:
                return "I don't understand that command"
                
        except Exception as e:
            self.logger.error(f"Error handling command: {str(e)}")
            return f"Error executing command: {str(e)}"
    
    async def _process_normal_query(self, user_input: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Process a normal query using the LLM."""
        try:
            # Get response from LLM
            response = await self.llm_manager.generate_response(user_input, context)
            return response
            
        except Exception as e:
            self.logger.error(f"Error processing query: {str(e)}")
            return f"Error processing your query: {str(e)}"
    
    async def shutdown(self):
        """Clean up resources."""
        self.logger.info("Shutting down agent manager...") 