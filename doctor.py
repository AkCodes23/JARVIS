"""
MedAI - A medical conversation analysis system that provides real-time transcription
and insights for doctor-patient interactions.
"""

import asyncio
import logging
import sys
from datetime import datetime
from pathlib import Path
import json
import re

from core.brain.brain import JarvisBrain

# Set up logging
logging.basicConfig(
    level=logging.WARNING,  # Changed from INFO to WARNING to reduce log output
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('medai.log')  # Removed StreamHandler to avoid console output
    ]
)

logger = logging.getLogger(__name__)

class MedAI:
    def __init__(self):
        self.brain = None
        self.conversation_history = []
        self.insights = {
            "key_points": [],
            "action_items": [],
            "patient_concerns": [],
            "medical_terms": [],
            "follow_up_questions": [],
            "symptoms": [],
            "medications": [],
            "vital_signs": [],
            "diagnosis_considerations": [],
            "risk_factors": [],
            "differential_diagnosis": []
        }
        
        # Medical term patterns
        self.medical_patterns = {
            "symptoms": [
                r"pain", r"headache", r"fever", r"cough", r"fatigue", r"nausea",
                r"dizziness", r"shortness of breath", r"chest pain", r"abdominal pain",
                r"joint pain", r"muscle pain", r"back pain", r"neck pain", r"throat pain",
                r"ear pain", r"eye pain", r"skin rash", r"itching", r"swelling",
                r"weight loss", r"weight gain", r"loss of appetite", r"increased appetite",
                r"sleep problems", r"anxiety", r"depression", r"mood changes"
            ],
            "medications": [
                r"aspirin", r"ibuprofen", r"acetaminophen", r"antibiotics",
                r"blood pressure medication", r"insulin", r"antidepressants",
                r"antihistamines", r"antacids", r"pain relievers", r"sleeping pills",
                r"anxiety medication", r"cholesterol medication", r"diabetes medication"
            ],
            "vital_signs": [
                r"blood pressure", r"heart rate", r"temperature", r"respiratory rate",
                r"oxygen saturation", r"pulse", r"blood sugar", r"cholesterol",
                r"weight", r"height", r"bmi"
            ],
            "risk_factors": [
                r"smoking", r"alcohol", r"family history", r"age", r"gender",
                r"obesity", r"sedentary lifestyle", r"stress", r"diet",
                r"occupation", r"environmental exposure"
            ]
        }
        
        # Diagnostic patterns and associations
        self.diagnostic_patterns = {
            "cardiovascular": {
                "symptoms": ["chest pain", "shortness of breath", "palpitations", "fatigue"],
                "risk_factors": ["smoking", "high blood pressure", "family history"],
                "considerations": ["angina", "heart attack", "heart failure", "arrhythmia"]
            },
            "respiratory": {
                "symptoms": ["cough", "shortness of breath", "chest pain", "wheezing"],
                "risk_factors": ["smoking", "asthma", "allergies"],
                "considerations": ["pneumonia", "bronchitis", "asthma", "COPD"]
            },
            "gastrointestinal": {
                "symptoms": ["abdominal pain", "nausea", "vomiting", "diarrhea"],
                "risk_factors": ["diet", "alcohol", "stress"],
                "considerations": ["gastritis", "ulcer", "irritable bowel syndrome"]
            },
            "neurological": {
                "symptoms": ["headache", "dizziness", "numbness", "tingling"],
                "risk_factors": ["age", "family history", "head injury"],
                "considerations": ["migraine", "stroke", "multiple sclerosis"]
            }
        }
        
    async def initialize(self):
        """Initialize the MedAI system."""
        try:
            logger.info("Initializing MedAI...")
            self.brain = JarvisBrain()
            await self.brain.start()
            return True
        except Exception as e:
            logger.error(f"Failed to initialize MedAI: {str(e)}")
            return False
            
    def extract_medical_terms(self, text):
        """Extract medical terms from the text using patterns."""
        text_lower = text.lower()
        extracted_terms = {}
        
        for category, patterns in self.medical_patterns.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    matches.append(pattern)
            if matches:
                extracted_terms[category] = matches
                
        return extracted_terms
        
    def analyze_diagnostic_patterns(self, extracted_terms):
        """Analyze the conversation for potential diagnostic patterns."""
        diagnostic_considerations = []
        differential_diagnosis = []
        
        # Check each diagnostic category
        for category, patterns in self.diagnostic_patterns.items():
            # Count matching symptoms and risk factors
            symptom_matches = sum(1 for symptom in patterns["symptoms"] 
                                if symptom in extracted_terms.get("symptoms", []))
            risk_matches = sum(1 for risk in patterns["risk_factors"] 
                             if risk in extracted_terms.get("risk_factors", []))
            
            # If we have enough matches, add to considerations
            if symptom_matches >= 2 or (symptom_matches >= 1 and risk_matches >= 1):
                diagnostic_considerations.append({
                    "category": category,
                    "symptoms": [s for s in patterns["symptoms"] 
                               if s in extracted_terms.get("symptoms", [])],
                    "risk_factors": [r for r in patterns["risk_factors"] 
                                   if r in extracted_terms.get("risk_factors", [])],
                    "considerations": patterns["considerations"]
                })
                differential_diagnosis.extend(patterns["considerations"])
                
        return diagnostic_considerations, differential_diagnosis
        
    def generate_follow_up_questions(self, text, extracted_terms):
        """Generate relevant follow-up questions based on the conversation."""
        questions = []
        text_lower = text.lower()
        
        # Symptom-related questions
        if "symptoms" in extracted_terms:
            if "pain" in text_lower:
                questions.append("What is the intensity of the pain on a scale of 1-10?")
                questions.append("How long have you been experiencing this pain?")
                questions.append("Does anything make the pain better or worse?")
            if "fever" in text_lower:
                questions.append("What is your current temperature?")
                questions.append("Have you taken any fever-reducing medication?")
                questions.append("How long have you had the fever?")
                
        # Medication-related questions
        if "medications" in extracted_terms:
            questions.append("Are you taking any other medications?")
            questions.append("Have you experienced any side effects from your medications?")
            questions.append("How long have you been on these medications?")
            
        # Vital signs questions
        if "vital_signs" in extracted_terms:
            if "blood pressure" in text_lower:
                questions.append("What was your last blood pressure reading?")
                questions.append("Have you noticed any changes in your blood pressure?")
            if "heart rate" in text_lower:
                questions.append("Have you noticed any changes in your heart rate?")
                questions.append("Do you experience any palpitations?")
                
        # Risk factor questions
        if "risk_factors" in extracted_terms:
            if "smoking" in text_lower:
                questions.append("How many cigarettes do you smoke per day?")
                questions.append("How long have you been smoking?")
            if "family history" in text_lower:
                questions.append("Which family members have had similar conditions?")
                
        return questions
        
    def identify_action_items(self, text, extracted_terms):
        """Identify action items based on the conversation."""
        actions = []
        text_lower = text.lower()
        
        # Medication-related actions
        if "medications" in extracted_terms:
            actions.append("Review current medications")
            actions.append("Check for potential drug interactions")
            actions.append("Consider medication adjustments if needed")
            
        # Symptom-related actions
        if "symptoms" in extracted_terms:
            actions.append("Document symptom severity and duration")
            if "pain" in text_lower:
                actions.append("Assess pain management options")
                actions.append("Consider pain scale assessment")
                
        # Vital signs actions
        if "vital_signs" in extracted_terms:
            actions.append("Record current vital signs")
            actions.append("Compare with previous readings")
            actions.append("Monitor trends in vital signs")
            
        # Diagnostic actions
        if any(category in extracted_terms for category in ["symptoms", "risk_factors"]):
            actions.append("Consider additional diagnostic tests")
            actions.append("Review medical history")
            actions.append("Assess risk factors")
            
        return actions
        
    async def analyze_conversation(self, text):
        """Analyze the conversation text for medical insights."""
        # Extract medical terms
        extracted_terms = self.extract_medical_terms(text)
        
        # Update insights based on extracted terms
        for category, terms in extracted_terms.items():
            if category == "symptoms":
                self.insights["symptoms"].extend(terms)
                self.insights["key_points"].append(f"Patient reported symptoms: {', '.join(terms)}")
            elif category == "medications":
                self.insights["medications"].extend(terms)
                self.insights["key_points"].append(f"Medications discussed: {', '.join(terms)}")
            elif category == "vital_signs":
                self.insights["vital_signs"].extend(terms)
                self.insights["key_points"].append(f"Vital signs mentioned: {', '.join(terms)}")
            elif category == "risk_factors":
                self.insights["risk_factors"].extend(terms)
                self.insights["key_points"].append(f"Risk factors identified: {', '.join(terms)}")
                
        # Analyze diagnostic patterns
        diagnostic_considerations, differential_diagnosis = self.analyze_diagnostic_patterns(extracted_terms)
        self.insights["diagnosis_considerations"].extend(diagnostic_considerations)
        self.insights["differential_diagnosis"].extend(differential_diagnosis)
        
        # Generate follow-up questions
        follow_up_questions = self.generate_follow_up_questions(text, extracted_terms)
        self.insights["follow_up_questions"].extend(follow_up_questions)
        
        # Identify action items
        action_items = self.identify_action_items(text, extracted_terms)
        self.insights["action_items"].extend(action_items)
        
        # Check for patient concerns
        concern_keywords = ["worried", "concerned", "anxious", "scared", "afraid"]
        if any(keyword in text.lower() for keyword in concern_keywords):
            self.insights["patient_concerns"].append("Patient expressed concerns about their condition")
            
        # Add the conversation to history
        self.conversation_history.append({
            "timestamp": datetime.now().isoformat(),
            "text": text,
            "extracted_terms": extracted_terms
        })
        
    def save_conversation(self):
        """Save the conversation and insights to a file."""
        output = {
            "conversation": self.conversation_history,
            "insights": self.insights,
            "timestamp": datetime.now().isoformat()
        }
        
        filename = f"medical_conversation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        logger.info(f"Conversation saved to {filename}")
        
    def display_insights(self):
        """Display the collected insights to the doctor."""
        print("\n=== MedAI Insights ===")
        
        print("\nKey Discussion Points:")
        for point in self.insights["key_points"]:
            print(f"- {point}")
            
        print("\nSymptoms Reported:")
        for symptom in self.insights["symptoms"]:
            print(f"- {symptom}")
            
        print("\nMedications Discussed:")
        for medication in self.insights["medications"]:
            print(f"- {medication}")
            
        print("\nVital Signs Mentioned:")
        for vital in self.insights["vital_signs"]:
            print(f"- {vital}")
            
        print("\nRisk Factors Identified:")
        for risk in self.insights["risk_factors"]:
            print(f"- {risk}")
            
        print("\nDiagnostic Considerations:")
        for consideration in self.insights["diagnosis_considerations"]:
            print(f"\nCategory: {consideration['category']}")
            print("Symptoms:", ", ".join(consideration["symptoms"]))
            print("Risk Factors:", ", ".join(consideration["risk_factors"]))
            print("Possible Conditions:", ", ".join(consideration["considerations"]))
            
        print("\nDifferential Diagnosis:")
        for diagnosis in set(self.insights["differential_diagnosis"]):
            print(f"- {diagnosis}")
            
        print("\nAction Items:")
        for item in self.insights["action_items"]:
            print(f"- {item}")
            
        print("\nPatient Concerns:")
        for concern in self.insights["patient_concerns"]:
            print(f"- {concern}")
            
        print("\nFollow-up Questions:")
        for question in self.insights["follow_up_questions"]:
            print(f"- {question}")
            
    async def shutdown(self):
        """Shutdown the MedAI system."""
        if self.brain:
            await self.brain.shutdown()
            
async def main():
    medai = MedAI()
    try:
        # Initialize MedAI
        if not await medai.initialize():
            return
            
        print("\nStarting MedAI - Doctor-Patient Conversation Analysis")
        print("The system will transcribe and analyze the conversation in real-time.")
        print("Press Ctrl+C to end the session and view insights.")
        
        # Initial introduction
        introduction = "MedAI is ready to assist with the doctor-patient conversation. I will transcribe and analyze the discussion."
        await medai.brain.voice_manager.text_to_speech(introduction)
        
        # Conversation loop
        while True:
            try:
                # Record audio
                print("\nListening... (Press Ctrl+C to end session)")
                audio_file = await medai.brain.voice_manager.record_audio(duration=15.0)
                
                # Convert speech to text
                text = await medai.brain.voice_manager.speech_to_text(audio_file)
                if not text:
                    continue
                    
                # Check if user wants to end the conversation
                if text.lower() in ['exit', 'quit', 'bye', 'goodbye', 'thank you']:
                    farewell = "Goodbye! Have a great day!"
                    await medai.brain.voice_manager.text_to_speech(farewell)
                    break
                    
                # Process and analyze the conversation
                await medai.analyze_conversation(text)
                
                # Print only the transcribed text
                print(f"\nTranscribed: {text}")
                
            except KeyboardInterrupt:
                print("\nSession ended by user")
                break
            except Exception as e:
                print(f"\nError: {str(e)}")
                error_message = "I encountered an error. Please try again."
                await medai.brain.voice_manager.text_to_speech(error_message)
        
        # Display insights and save conversation
        medai.display_insights()
        medai.save_conversation()
        
    except Exception as e:
        print(f"\nFatal error: {str(e)}")
    finally:
        # Ensure proper shutdown
        await medai.shutdown()
        print("\nMedAI shut down successfully")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
    except Exception as e:
        print(f"\nProgram terminated due to error: {str(e)}") 