import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiTranslationModule:
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
    def translate_to_english(self, text):
        try:
            prompt = f"""
Convert the following text to clean, natural English suitable for semantic search. If already in proper English, return unchanged. For other languages, translate accurately while preserving technical terms like FIR, cyber crime, etc.

Input: "{text}"

Output:"""

            response = self.model.generate_content(prompt)
            
            if response and response.text:
                translated = response.text.strip().replace('"', '').replace("'", '').strip()
                if translated and translated[0].islower():
                    translated = translated[0].upper() + translated[1:]
                return translated
            else:
                return text
                
        except Exception:
            return text

if __name__ == "__main__":
    user_input = input("Enter text: ")
    translator = GeminiTranslationModule()
    result = translator.translate_to_english(user_input)
    print(result)
