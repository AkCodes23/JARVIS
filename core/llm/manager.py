"""
LLM Manager for handling language model interactions using Groq.
"""

import os
import logging
from typing import Dict, Any, Optional, Tuple
from groq import Groq

from core.llm.reasoning import ReasoningModule

class LLMManager:
    """Manages interactions with the Groq language model."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the LLM manager."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.model = config.get("model_name", "llama-3.3-70b-versatile")
        self.api_key = "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"
        self.reasoning = ReasoningModule(config.get("reasoning", {}))
        
        # Phrases that trigger reasoning
        self.reasoning_triggers = [
            "think about",
            "reason about",
            "analyze",
            "consider",
            "evaluate",
            "think through",
            "reason through",
            "think carefully about",
            "reason carefully about"
        ]
        
    async def initialize(self):
        """Initialize the language model."""
        self.logger.info("Initializing Groq LLM manager...")
        self.client = Groq(api_key=self.api_key)
        self.logger.info(f"Initialized Groq with model: {self.model}")
        
    async def generate_response(self, prompt: str, context: Optional[str] = None) -> Tuple[str, Optional[str]]:
        """
        Generate a response from the language model.
        
        Returns:
            Tuple[str, Optional[str]]: (response to speak, reasoning steps to show in chat)
        """
        if not self.client:
            raise RuntimeError("LLM not initialized")
            
        try:
            # Check if reasoning is requested
            should_reason = any(trigger in prompt.lower() for trigger in self.reasoning_triggers)
            
            if should_reason:
                # Process through reasoning module
                reasoning_result = await self.reasoning.process_query(prompt, {"context": context})
                reasoning_steps = "\n".join([step["description"] for step in reasoning_result["reasoning_steps"]])
                
                if context:
                    full_prompt = f"""Context: {context}

Reasoning Steps:
{reasoning_steps}

Question: {prompt}

Please provide a thoughtful response that follows the reasoning steps above. Do not mention the reasoning steps in your response:"""
                else:
                    full_prompt = f"""Reasoning Steps:
{reasoning_steps}

Question: {prompt}

Please provide a thoughtful response that follows the reasoning steps above. Do not mention the reasoning steps in your response:"""
            else:
                # Normal response without reasoning
                if context:
                    full_prompt = f"Context: {context}\n\nQuestion: {prompt}\n\nAnswer:"
                else:
                    full_prompt = f"Question: {prompt}\n\nAnswer:"
                
            # Generate response using Groq
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are Jarvis, a helpful and knowledgeable AI assistant."},
                    {"role": "user", "content": full_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            response = completion.choices[0].message.content.strip()
            
            # Return response and reasoning steps (if any)
            if should_reason:
                return response, reasoning_steps
            else:
                return response, None
            
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return f"Error: {str(e)}", None
    
    async def shutdown(self):
        """Clean up resources."""
        self.logger.info("Shutting down Groq LLM manager...")
        self.client = None 