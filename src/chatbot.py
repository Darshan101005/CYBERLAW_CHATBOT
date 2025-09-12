import os
import google.generativeai as genai
from dotenv import load_dotenv
from gemini_translator import GeminiTranslationModule
from vector_searcher import VectorSearcher
from act_categorizer import ActCategorizer
from complaint_collector import ComplaintCollector
from file_processor import FileProcessor
from typing import Dict, List, Any

load_dotenv()

class CyberLawChatbot:
    def __init__(self):
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.google_api_key)
        
        # Initialize conversation memory
        self.conversation_history = []
        self.max_history_turns = 6  # Keep last 6 turns for context
        
        # Initialize session state
        self.active_complaint_id = None
        self.session_state = "general"  # general, complaint_collection, file_analysis
        
        # Initialize components
        try:
            self.translator = GeminiTranslationModule()
            self.searcher = VectorSearcher()
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.act_categorizer = ActCategorizer()
            self.complaint_collector = ComplaintCollector()
            self.file_processor = FileProcessor()
            print("Enhanced chatbot initialized successfully!")
        except Exception as e:
            print(f"Error initializing chatbot: {e}")
            raise
    
    def generate_response(self, user_query: str, search_results: Dict[str, List[Dict[str, Any]]], original_language: str = "English", user_input: str = "") -> str:
        """Generate response using Gemini with context from search results"""
        try:
            # Prepare context from search results
            context_parts = []
            
            # Add CyberLaw context with color coding
            if search_results.get('cyberlaw'):
                context_parts.append("=== RELEVANT CYBER LAW SECTIONS ===")
                for result in search_results['cyberlaw']:
                    # Get color-coded section info
                    colored_section = self.act_categorizer.format_colored_section(
                        result['section_number'], 
                        result['title'], 
                        result['law_type'],
                        result.get('summary', '') + ' ' + result.get('content', '')
                    )
                    context_parts.append(colored_section)
                    context_parts.append(f"Summary: {result['summary']}")
                    context_parts.append(f"Content: {result['content']}")
                    context_parts.append("")
            
            # Add FAQ context
            if search_results.get('faq'):
                context_parts.append("=== RELEVANT FAQs ===")
                for result in search_results['faq']:
                    context_parts.append(f"Q: {result['question']}")
                    context_parts.append(f"A: {result['answer']}")
                    context_parts.append("")
            
            # Add Nodal Officers context if relevant
            if search_results.get('nodal_officers'):
                context_parts.append("=== RELEVANT CONTACT INFORMATION ===")
                for result in search_results['nodal_officers']:
                    context_parts.append(f"State: {result['state']}")
                    context_parts.append(f"Nodal Officer: {result['officer_name']} ({result['rank']})")
                    context_parts.append(f"Email: {result['email']}")
                    if result['contact']:
                        context_parts.append(f"Contact: {result['contact']}")
                    context_parts.append("")
            
            context = "\n".join(context_parts)
            
            # Add conversation history to context
            history_context = ""
            if self.conversation_history:
                history_context = "\n=== RECENT CONVERSATION (for reference) ===\n"
                # Show last few turns (most recent first)
                for i, turn in enumerate(reversed(self.conversation_history[-self.max_history_turns:])):
                    history_context += f"Turn {len(self.conversation_history)-i}: User asked: {turn['user_original']}\n"
                    history_context += f"Bot replied: {turn['bot_reply'][:100]}...\n\n"
            
            # Create prompt for enhanced response generation
            language_instruction = f"Respond in {original_language}" if original_language != "English" else "Respond in English"
            
            prompt = f"""
You are a friendly cyber law assistant chatbot. Provide a structured, helpful response about Indian cyber law.

{history_context}

CONTEXT:
{context}

USER QUESTION: {user_query}
ORIGINAL USER TEXT: {user_input}

INSTRUCTIONS:
1. ONLY use information from the provided context - don't add knowledge from outside sources
2. Structure your response in this EXACT format in {original_language}:

**SITUATION:** (1-2 lines acknowledging the user's situation)

**KEY POINTS:**
• Point 1 (brief)
• Point 2 (brief) 
• Point 3 (brief)

**RELEVANT ACTS/SECTIONS:**
• **Support:** [Color emoji + Specific Act/Section from context that helps user] - brief explanation OR "None found in context"
• **Against:** [Color emoji + Specific Act/Section from context that may work against user] - brief explanation OR "None found in context"

**NEED MORE HELP?**
• Question 1?
• Question 2?
• Question 3?

3. If context doesn't have enough info, still follow the format but ask clarifying questions
4. Keep language simple and conversational
5. IMPORTANT: {language_instruction}. Match the user's original language and style exactly.
6. Use ONLY Acts/Sections mentioned in the provided context - never invent legal references

RESPONSE:"""

            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                return "I apologize, but I'm having trouble generating a response right now. Please try again."
                
        except Exception as e:
            print(f"Error generating response: {e}")
            return "I apologize, but I encountered an error while generating the response. Please try again."
    
    def add_to_conversation_history(self, user_original: str, user_english: str, bot_reply: str, language: str):
        """Add conversation turn to history with rolling window"""
        turn = {
            'user_original': user_original,
            'user_english': user_english, 
            'bot_reply': bot_reply,
            'detected_language': language
        }
        
        self.conversation_history.append(turn)
        
        # Keep only recent turns (rolling window)
        if len(self.conversation_history) > self.max_history_turns:
            self.conversation_history = self.conversation_history[-self.max_history_turns:]
    
    def detect_intent(self, user_input: str) -> str:
        """Detect user intent (complaint, file_analysis, general_query)"""
        input_lower = user_input.lower()
        
        # Complaint indicators
        complaint_keywords = [
            "complaint", "report crime", "file fir", "i want to report", "happened to me",
            "fraud", "scam", "hacked", "cheated", "cyber crime", "help me report",
            "i am victim", "someone did", "file a case", "take action"
        ]
        
        if any(keyword in input_lower for keyword in complaint_keywords):
            return "complaint"
        else:
            return "general_query"
    
    def handle_complaint_initiation(self, user_input: str) -> str:
        """Handle complaint collection initiation"""
        try:
            result = self.complaint_collector.start_complaint_collection(user_input)
            self.active_complaint_id = result["complaint_id"]
            self.session_state = "complaint_collection"
            return result["message"]
        except Exception as e:
            print(f"Error starting complaint collection: {e}")
            return "I understand you want to file a complaint. Let me help you collect the necessary information. What type of cyber crime occurred?"
    
    def handle_complaint_continuation(self, user_input: str) -> str:
        """Handle ongoing complaint collection"""
        try:
            result = self.complaint_collector.process_answer(self.active_complaint_id, user_input)
            
            if result.get("status") == "completed":
                self.session_state = "general"
                self.active_complaint_id = None
                
            return result["message"]
        except Exception as e:
            print(f"Error processing complaint answer: {e}")
            self.session_state = "general"
            self.active_complaint_id = None
            return "There was an error processing your answer. Let's start over. What would you like help with?"
    
    def handle_file_command(self, user_input: str) -> str:
        """Handle file analysis commands like /analyze filename.pdf"""
        try:
            # Extract file path from command
            parts = user_input.split(" ", 1)
            if len(parts) < 2:
                return "**📄 FILE ANALYSIS**\n\nPlease provide a file path: `/analyze path/to/your/file.pdf`\n\nSupported formats: `.txt`, `.pdf`, `.json`"
            
            file_path = parts[1].strip()
            
            # Check if file exists
            if not os.path.exists(file_path):
                return f"❌ **File not found**: `{file_path}`\n\nPlease check the file path and try again."
            
            # Process the file
            filename = os.path.basename(file_path)
            result = self.file_processor.process_uploaded_file(file_path, filename)
            
            if not result.get("success"):
                return f"❌ **File Processing Failed**: {result.get('error', 'Unknown error')}"
            
            # Get analysis summary
            summary = self.file_processor.get_file_analysis_summary(result)
            
            # Generate legal advice
            legal_advice = self.generate_file_based_legal_advice(result, user_input)
            
            return f"{summary}\n\n{legal_advice}"
            
        except Exception as e:
            print(f"Error processing file: {e}")
            return "❌ **File Analysis Error**: Please check your file path and try again."
    
    def generate_file_based_legal_advice(self, file_result: dict, user_query: str) -> str:
        """Generate legal advice based on file analysis"""
        try:
            analysis = file_result.get("analysis", {})
            potential_issues = analysis.get("potential_issues", [])
            
            if not potential_issues:
                return "**💡 LEGAL GUIDANCE**: No specific legal issues were detected. If you have concerns, please describe them and I'll provide guidance."
            
            # Create search query based on detected issues
            issue_types = [issue["type"] for issue in potential_issues[:2]]
            search_query = " ".join(issue_types).replace("_", " ") + " cyber crime law"
            
            # Search for relevant legal sections
            search_results = self.searcher.comprehensive_search(search_query)
            
            # Generate response with context
            if search_results.get("cyberlaw") or search_results.get("faq"):
                return self.generate_response(search_query, search_results, "English", user_query)
            else:
                return "**💡 LEGAL GUIDANCE**: Consider consulting with a cyber law expert and filing a complaint with your local cyber crime cell."
                
        except Exception as e:
            print(f"Error generating legal advice: {e}")
            return "**💡 LEGAL GUIDANCE**: Please describe the specific issues you'd like help with."

    def process_query(self, user_input: str) -> str:
        """Main method to process user query through the complete pipeline"""
        try:
            print(f"User query: {user_input}")
            
            # Handle file analysis commands
            if user_input.startswith("/analyze"):
                return self.handle_file_command(user_input)
            
            # Handle ongoing complaint collection
            if self.session_state == "complaint_collection":
                return self.handle_complaint_continuation(user_input)
            
            # Step 0: Detect user intent for new conversations
            intent = self.detect_intent(user_input)
            print(f"Detected intent: {intent}")
            
            # Handle complaint initiation
            if intent == "complaint":
                return self.handle_complaint_initiation(user_input)
            
            # Step 1: Detect language and translate to English if needed
            print("Detecting language and translating to English...")
            translation_result = self.translator.detect_language_and_translate(user_input)
            original_language = translation_result["original_language"]
            english_query = translation_result["translated_text"]
            print(f"Original language: {original_language}")
            print(f"Translated query: {english_query}")
            
            # Step 2: Search vector database
            print("Searching knowledge base...")
            search_results = self.searcher.comprehensive_search(english_query)
            
            # Log search results count
            cyberlaw_count = len(search_results.get('cyberlaw', []))
            faq_count = len(search_results.get('faq', []))
            officer_count = len(search_results.get('nodal_officers', []))
            print(f"Found: {cyberlaw_count} law sections, {faq_count} FAQs, {officer_count} officers")
            
            # Step 3: Generate response using Gemini with context
            print("Generating response...")
            response = self.generate_response(english_query, search_results, original_language, user_input)
            
            # Step 4: Add to conversation history
            self.add_to_conversation_history(user_input, english_query, response, original_language)
            
            return response
            
        except Exception as e:
            print(f"Error processing query: {e}")
            return "I apologize, but I encountered an error while processing your question. Please try again later."
    
    def chat_loop(self):
        """Interactive chat loop"""
        print("=" * 60)
        print("🤖 ENHANCED CYBER LAW CHATBOT")
        print("💬 Ask questions about cyber laws, FIR registration, cyber crimes, etc.")
        print("📋 Type 'report' or 'complaint' to file a cyber crime complaint")
        print("📄 Type '/analyze filename.pdf' to analyze documents") 
        print("❌ Type 'quit' or 'exit' to end the conversation")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\n👋 Thank you for using the Cyber Law Chatbot!")
                    break
                
                if not user_input:
                    print("Please enter a question.")
                    continue
                
                print("\n🔍 Processing your question...")
                response = self.process_query(user_input)
                print(f"\n🤖 Chatbot: {response}")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ An error occurred: {e}")
                print("Please try again.")
    
    def close(self):
        """Clean up resources"""
        if hasattr(self, 'searcher'):
            self.searcher.close()

if __name__ == "__main__":
    try:
        chatbot = CyberLawChatbot()
        chatbot.chat_loop()
    except Exception as e:
        print(f"Failed to start chatbot: {e}")
        print("Make sure all environment variables are set properly:")
        print("- GOOGLE_API_KEY")
        print("- WEAVIATE_URL") 
        print("- WEAVIATE_API_KEY")
    finally:
        if 'chatbot' in locals():
            chatbot.close()