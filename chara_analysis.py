# ai_analyzer_gemini.py

import google.generativeai as genai
from pathlib import Path

DEFAULT_MODEL = 'gemini-2.5-flash'

class GeminiAnalyzer:
    def __init__(self, api_key, model):
        if not api_key:
            raise ValueError("API key is required.")
        self.api_key = api_key
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)
    
    def analyze_character(self, character_name, quotes_file):
        with open(quotes_file, 'r', encoding='utf-8') as f:
            quotes = f.read()
        
        prompt = f"""Analyze the character "{character_name}" based on these quotes:

{quotes}

Provide comprehensive character analysis including personality, psychology, and development."""
        
        response = self.model.generate_content(prompt)
        return response.text

def _prompt_quotes_file():
    while True:
        raw = input("Quotes file (.txt): ").strip().strip('"')
        if not raw:
            print("Please enter a .txt file path.")
            continue

        path = Path(raw)
        if path.suffix.lower() != '.txt':
            print("Please provide a .txt file.")
            continue
        if not path.is_file():
            print("File not found. Try again.")
            continue

        return path

# Usage
if __name__ == "__main__":
    # Get free API key: https://makersuite.google.com/app/apikey
    api_key = input("Enter Google API key: ").strip()
    while not api_key:
        api_key = input("API key is required. Enter Google API key: ").strip()

    model = input(f"Model (default: {DEFAULT_MODEL}): ").strip() or DEFAULT_MODEL

    analyzer = GeminiAnalyzer(api_key, model)
    character = input("Character name: ")
    quotes_file = _prompt_quotes_file()
    
    print("🤖 Analyzing...")
    result = analyzer.analyze_character(character, quotes_file)
    
    print("\n" + "="*60)
    print(result)
    
    # Save
    with open(f"{character}_gemini_analysis.txt", 'w', encoding='utf-8') as f:
        f.write(result)