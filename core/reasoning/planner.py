"""
Reasoning and Planning module for Jarvis.
Handles step-by-step analysis, chain-of-thought reasoning, and task decomposition.
"""

import logging
from typing import List, Dict, Any, Optional
import re

class ReasoningPlanner:
    """Handles complex reasoning and planning tasks."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the reasoning planner."""
        self.logger = logging.getLogger("jarvis.reasoning")
        self.config = config
        self.trigger_words = ["analyze", "think about", "plan how to", "break down", "explain step by step"]
        
    def is_reasoning_task(self, text: str) -> bool:
        """Check if the input requires reasoning."""
        return any(word in text.lower() for word in self.trigger_words)
        
    async def analyze(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Perform step-by-step analysis of a task."""
        if not self.is_reasoning_task(text):
            return text
            
        # Extract the core task
        task = self._extract_task(text)
        
        # Generate analysis steps
        steps = await self._generate_steps(task, context)
        
        # Format the response
        response = self._format_analysis(task, steps)
        
        return response
        
    def _extract_task(self, text: str) -> str:
        """Extract the core task from the input text."""
        # Remove trigger words
        for word in self.trigger_words:
            text = text.lower().replace(word, "")
        return text.strip()
        
    async def _generate_steps(self, task: str, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """Generate step-by-step analysis of the task."""
        # This would typically use the LLM to generate steps
        # For now, return a simple structure
        return [
            f"1. Understanding the task: {task}",
            "2. Breaking down into sub-tasks",
            "3. Analyzing each sub-task",
            "4. Synthesizing the results",
            "5. Providing a comprehensive answer"
        ]
        
    def _format_analysis(self, task: str, steps: List[str]) -> str:
        """Format the analysis into a clear response."""
        response = f"Analysis of: {task}\n\n"
        response += "Step-by-step reasoning:\n"
        response += "\n".join(steps)
        return response
        
    async def chain_of_thought(self, text: str) -> str:
        """Perform chain-of-thought reasoning."""
        # This would use the LLM to generate a chain of thought
        # For now, return a simple structure
        return f"Let me think through this step by step:\n\n1. First, I need to understand {text}\n2. Then, I can analyze the components\n3. Finally, I can provide a solution"
        
    async def decompose_task(self, task: str) -> List[str]:
        """Break down a complex task into smaller steps."""
        # This would use the LLM to decompose the task
        # For now, return a simple structure
        return [
            f"1. Understand the requirements of {task}",
            "2. Identify the main components",
            "3. Break down each component",
            "4. Plan the execution order",
            "5. Consider potential challenges"
        ] 