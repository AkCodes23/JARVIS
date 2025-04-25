import os
from groq import Groq

def test_groq():
    # Use API key directly
    api_key = "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"
    
    print("Testing Groq connection...")
    try:
        client = Groq(api_key=api_key)
        
        # List available models
        print("\nAvailable models:")
        models = client.models.list()
        for model in models.data:
            print(f"- {model.id}")
        
        # Try to use the first available model
        if models.data:
            model_name = models.data[0].id
            print(f"\nTrying to use model: {model_name}")
            
            completion = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Hello, can you hear me?"}
                ],
                temperature=0.7,
                max_tokens=100
            )
            print("Response:", completion.choices[0].message.content)
            print("Connection successful!")
        else:
            print("No models available")
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_groq() 