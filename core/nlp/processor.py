"""
Natural Language Processing module for Jarvis.
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import json
import spacy
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from sentence_transformers import SentenceTransformer
import torch
import numpy as np
from datetime import datetime

class NLPProcessor:
    """Handles natural language processing tasks."""
    
    def __init__(
        self,
        config: Dict[str, Any],
        model_dir: str = "models/nlp"
    ):
        """Initialize NLP processor."""
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.model_dir = Path(model_dir)
        self.model_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize conversation history
        self.conversation_history = []
        self.max_history_length = config.get("max_history_length", 10)
        
        # Load language models
        self._load_models()
        
    def _load_models(self):
        """Load required NLP models."""
        try:
            # Load spaCy model for entity extraction
            self.nlp = spacy.load("en_core_web_sm")
            
            # Load intent classification model
            self.intent_model = AutoModelForSequenceClassification.from_pretrained(
                "facebook/bart-large-mnli"
            )
            self.intent_tokenizer = AutoTokenizer.from_pretrained(
                "facebook/bart-large-mnli"
            )
            
            # Load sentiment analysis model for sarcasm detection
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="finiteautomata/bertweet-base-sentiment-analysis"
            )
            
            # Load sentence transformer for context understanding
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Load language detection model
            self.language_detector = pipeline(
                "text-classification",
                model="papluca/xlm-roberta-base-language-detection"
            )
            
            self.logger.info("NLP models loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to load NLP models: {str(e)}")
            raise
            
    def add_to_history(self, text: str, speaker: str = "user"):
        """Add a message to conversation history."""
        self.conversation_history.append({
            "text": text,
            "speaker": speaker,
            "timestamp": datetime.now().isoformat()
        })
        
        # Trim history if too long
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]
            
    def get_context(self, text: str) -> Dict[str, Any]:
        """Get relevant context from conversation history."""
        try:
            # Get current text embedding
            current_embedding = self.sentence_transformer.encode(text)
            
            # Calculate similarity with history
            similarities = []
            for message in self.conversation_history:
                history_embedding = self.sentence_transformer.encode(message["text"])
                similarity = np.dot(current_embedding, history_embedding) / (
                    np.linalg.norm(current_embedding) * np.linalg.norm(history_embedding)
                )
                similarities.append((message, similarity))
                
            # Sort by similarity
            similarities.sort(key=lambda x: x[1], reverse=True)
            
            # Get most relevant context
            relevant_context = [msg for msg, sim in similarities[:3] if sim > 0.5]
            
            return {
                "relevant_history": relevant_context,
                "full_history": self.conversation_history
            }
            
        except Exception as e:
            self.logger.error(f"Error getting context: {str(e)}")
            return {"relevant_history": [], "full_history": self.conversation_history}
            
    def detect_intent(self, text: str) -> Dict[str, Any]:
        """Detect user intent from text."""
        try:
            # Prepare input for intent classification
            inputs = self.intent_tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512
            )
            
            # Get intent classification
            outputs = self.intent_model(**inputs)
            scores = torch.softmax(outputs.logits, dim=1)
            
            # Get top intents
            top_scores, top_indices = torch.topk(scores, k=3)
            
            intents = []
            for score, idx in zip(top_scores[0], top_indices[0]):
                intent = self.intent_model.config.id2label[idx.item()]
                intents.append({
                    "intent": intent,
                    "confidence": score.item()
                })
                
            return {
                "primary_intent": intents[0],
                "alternative_intents": intents[1:],
                "text": text
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting intent: {str(e)}")
            return {
                "primary_intent": {"intent": "unknown", "confidence": 0.0},
                "alternative_intents": [],
                "text": text
            }
            
    def extract_entities(self, text: str) -> List[Dict[str, Any]]:
        """Extract named entities from text."""
        try:
            # Process text with spaCy
            doc = self.nlp(text)
            
            # Extract entities
            entities = []
            for ent in doc.ents:
                entities.append({
                    "text": ent.text,
                    "label": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "description": spacy.explain(ent.label_)
                })
                
            return entities
            
        except Exception as e:
            self.logger.error(f"Error extracting entities: {str(e)}")
            return []
            
    def detect_language(self, text: str) -> Dict[str, Any]:
        """Detect the language of the text."""
        try:
            result = self.language_detector(text)[0]
            return {
                "language": result["label"],
                "confidence": result["score"]
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting language: {str(e)}")
            return {"language": "unknown", "confidence": 0.0}
            
    def detect_sarcasm(self, text: str) -> Dict[str, Any]:
        """Detect sarcasm in text."""
        try:
            # Get sentiment analysis
            sentiment = self.sentiment_analyzer(text)[0]
            
            # Simple sarcasm detection based on sentiment and context
            is_sarcastic = False
            confidence = 0.0
            
            # Check for common sarcasm indicators
            sarcasm_indicators = [
                "yeah right", "sure", "whatever", "obviously",
                "of course", "totally", "absolutely", "definitely"
            ]
            
            for indicator in sarcasm_indicators:
                if indicator in text.lower():
                    is_sarcastic = True
                    confidence = 0.7
                    break
                    
            # If no indicators found, use sentiment as a factor
            if not is_sarcastic:
                if sentiment["label"] == "NEG" and sentiment["score"] > 0.8:
                    is_sarcastic = True
                    confidence = 0.6
                    
            return {
                "is_sarcastic": is_sarcastic,
                "confidence": confidence,
                "sentiment": sentiment
            }
            
        except Exception as e:
            self.logger.error(f"Error detecting sarcasm: {str(e)}")
            return {
                "is_sarcastic": False,
                "confidence": 0.0,
                "sentiment": {"label": "unknown", "score": 0.0}
            }
            
    def process_text(self, text: str) -> Dict[str, Any]:
        """Process text with all NLP features."""
        try:
            # Add to conversation history
            self.add_to_history(text)
            
            # Get context
            context = self.get_context(text)
            
            # Detect intent
            intent = self.detect_intent(text)
            
            # Extract entities
            entities = self.extract_entities(text)
            
            # Detect language
            language = self.detect_language(text)
            
            # Detect sarcasm
            sarcasm = self.detect_sarcasm(text)
            
            return {
                "text": text,
                "context": context,
                "intent": intent,
                "entities": entities,
                "language": language,
                "sarcasm": sarcasm,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error processing text: {str(e)}")
            return {
                "text": text,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            
    def save_state(self, filepath: str):
        """Save conversation history to file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving state: {str(e)}")
            raise
            
    def load_state(self, filepath: str):
        """Load conversation history from file."""
        try:
            if Path(filepath).exists():
                with open(filepath, 'r') as f:
                    self.conversation_history = json.load(f)
                    
        except Exception as e:
            self.logger.error(f"Error loading state: {str(e)}")
            raise 