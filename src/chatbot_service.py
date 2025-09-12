import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv
from gemini_translator import GeminiTranslationModule
from vector_searcher import VectorSearcher
from act_categorizer import ActCategorizer
from complaint_collector import ComplaintCollector
from file_processor import FileProcessor
from typing import Dict, List, Any

load_dotenv()

class CyberLawChatbotService:
    def __init__(self):
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        genai.configure(api_key=self.google_api_key)
        
        # Initialize conversation memory (for single session service)
        self.conversation_history = []
        self.max_history_turns = 6  # Keep last 6 turns for context
        
        # Initialize components
        try:
            self.translator = GeminiTranslationModule()
            self.searcher = VectorSearcher()
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            self.act_categorizer = ActCategorizer()
            self.complaint_collector = ComplaintCollector()
            self.file_processor = FileProcessor()
            print("Enhanced chatbot service initialized successfully!")
        except Exception as e:
            print(f"Error initializing chatbot service: {e}")
            raise
    
    def generate_response(self, user_query: str, search_results: Dict[str, List[Dict[str, Any]]], original_language: str = "English", user_input: str = "") -> str:
        """Generate response using Gemini with context from search results"""
        try:
            # Check if we have any meaningful results
            total_results = (len(search_results.get('cyberlaw', [])) + 
                           len(search_results.get('faq', [])) + 
                           len(search_results.get('nodal_officers', [])))
            
            if total_results == 0:
                # Generate comprehensive no-result message
                no_result_prompt = f"""
You are Cyberlex, a professional cyber law assistant. The user asked about something not in your current knowledge base.

Provide a comprehensive response in {original_language if original_language != 'English' else 'English'} using this format:

**CYBERLEX ANALYSIS:**

**SITUATION:** I don't have specific legal sections about "{user_query}" in my current knowledge base, but I can provide general guidance on cyber law matters.

**WHAT I CAN HELP WITH:**
• Indian cyber crime definitions and legal provisions
• IT Act 2000 sections and their applications
• Understanding when IPC/BNS laws apply to cyber crimes
• Detailed punishment information for cyber offenses
• FIR registration procedures for cyber crimes
• Nodal officer contacts for your state/region
• Legal procedure guidance and rights information

**GENERAL CYBER LAW COVERAGE:**
• **IT Act provisions**: Unauthorized access, data theft, cyber fraud, defamation
• **Traditional criminal laws**: When IPC/BNS applies to cyber situations
• **Procedural guidance**: How to report, evidence collection, legal remedies

**CYBERLEX RECOMMENDATION:**
• Please rephrase your question with more specific details about your cyber law concern
• Tell me what type of cyber issue you're facing (fraud, hacking, data theft, etc.)
• Let me know if you need information about reporting procedures or legal options

**NEED MORE HELP?**
• What specific cyber crime or legal issue are you concerned about?
• Do you need help understanding how to report a cyber crime?
• Would you like contact information for cyber crime authorities in your state?
• Are you looking for information about specific penalties for cyber offenses?

USER QUESTION: {user_query}

Maintain a professional, comprehensive, and helpful tone."""

                try:
                    no_result_response = self.model.generate_content(no_result_prompt)
                    if no_result_response and no_result_response.text:
                        return no_result_response.text.strip()
                except:
                    pass
                    
                # Fallback message in English
                return """**CYBERLEX RESPONSE:**

**SITUATION:** I don't have specific information about that particular topic in my current knowledge base, but I'm here to assist you with cyber law matters.

**KEY POINTS:**
• I specialize in Indian cyber crime definitions and laws
• I can guide you through FIR registration procedures
• I can provide nodal officer contacts for your state

**CYBERLEX RECOMMENDATION:**
• Please provide more specific details about your query
• I can help you understand legal procedures and your rights

**NEED MORE HELP?**
• Would you like to know about specific cyber crime types?
• Can I help you understand how to report a cyber crime?
• Do you need contact information for your state's cyber crime cell?"""
            
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
You are Cyberlex, a professional cyber law assistant. Provide comprehensive, detailed responses about Indian cyber law with complete legal analysis. You MUST be thorough and responsible in your guidance.

{history_context}

CONTEXT:
{context}

USER QUESTION: {user_query}
ORIGINAL USER TEXT: {user_input}

CRITICAL INSTRUCTIONS:
1. ONLY use information from the provided context - don't add knowledge from outside sources
2. Provide COMPREHENSIVE analysis covering ALL applicable laws
3. Explain WHY laws apply or DON'T apply
4. Include DETAILED punishment information
5. MANDATORY: Use color-coded analysis for legal sections
6. Be responsible - people depend on accurate legal guidance

Structure your response in this EXACT format in {original_language}:

**CYBERLEX ANALYSIS:**

**SITUATION:** (Acknowledge the user's question professionally and provide detailed context about their legal situation)

**COMPREHENSIVE LEGAL ASSESSMENT:**

**IT ACT PROVISIONS:**
(Analyze ALL relevant IT Act sections from context with MANDATORY color coding)
• **Against:** 🔴 [IT Act Section Number]: [Title] - [Detailed explanation of how this works against the user]
  **Punishment**: [Complete penalty details including imprisonment, fines, etc.]
  **Why it applies**: [Specific reasoning why this section creates legal problems for user]

• **Against:** 🔴 [Another Section if applicable]
• **Support:** 🟢 [Section that helps user if any]
• **General:** 🟡 [Neutral/procedural sections]

**IPC/BNS PROVISIONS:**
(Analyze if IPC or BNS sections apply with color coding)
• **Against:** 🔴 [IPC/BNS Section]: [Title] - [How traditional criminal law applies]
  **Punishment**: [Complete penalty details]
  **Why it applies**: [Reasoning]

• **If NOT applicable**: Explain specifically WHY IPC/BNS doesn't apply in this case
  **Reasoning**: [Detailed explanation of why traditional laws don't cover this cyber situation]

**OTHER APPLICABLE LAWS:**
(Check for any other relevant laws from context with color coding)
• 🔴 [Laws that work against user]
• 🟢 [Laws that support user]  
• 🟡 [Neutral laws]

**PUNISHMENT SUMMARY:**
• **IT Act penalties**: [Complete summary with color indicators]
  🔴 Section X: [Penalty details]
  🔴 Section Y: [Penalty details]
• **Criminal law penalties**: [Any IPC/BNS penalties if applicable]
• **Civil liability**: [Any compensation or damages]
• **Severity factors**: [What might increase/decrease penalties]

**LEGAL IMPLICATIONS:**
• **Immediate consequences**: [What could happen right away]
• **Long-term implications**: [Criminal record, employment impact, etc.]
• **Mitigating factors**: [What might help reduce severity]

**CYBERLEX RECOMMENDATIONS:**
• **Immediate action**: [What to do right now]
• **Legal counsel**: [When and why to consult a lawyer]
• **Evidence preservation**: [If relevant]
• **Compliance steps**: [If applicable]

**PREVENTION GUIDANCE:**
• [How to avoid similar issues in future]
• [Best practices for cyber safety]

**NEED MORE HELP?**
• [Specific follow-up questions about their situation]
• [Clarifications needed for better guidance]
• [Additional resources they might need]

MANDATORY COLOR CODING RULES:
- 🔴 RED: Laws/sections that work AGAINST the user (penalties, violations)
- 🟢 GREEN: Laws/sections that SUPPORT the user (protections, defenses)
- 🟡 YELLOW: NEUTRAL/General laws (definitions, procedures)

CRITICAL REQUIREMENTS:
- MUST include color emojis (🔴🟢🟡) before every legal section
- Include ALL relevant sections from the provided context
- Provide COMPLETE punishment details for every applicable law
- Explain reasoning for why each law does/doesn't apply
- Be thorough and responsible - this is legal guidance people rely on
- If you don't have complete information, explicitly state what's missing
- {language_instruction}. Match the user's original language exactly.

RESPONSE:"""

            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                return "I apologize, but I'm having trouble generating a response right now. Please try again."
                
        except Exception as e:
            error_msg = str(e)
            print(f"Error generating response: {e}")
            
            # Handle rate limiting gracefully
            if "429" in error_msg or "quota" in error_msg.lower():
                return "I'm getting a lot of questions right now! Please try again in about a minute. I'll be ready to help you with your cyber law questions soon! 😊"
            
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
        
        # File processing indicators
        file_keywords = [
            "analyze file", "uploaded", "document", "attachment", "pdf", "text file",
            "review document", "check this", "what does this mean"
        ]
        
        if any(keyword in input_lower for keyword in complaint_keywords):
            return "complaint"
        elif any(keyword in input_lower for keyword in file_keywords):
            return "file_analysis"
        else:
            return "general_query"
    
    def process_query(self, user_input: str, file_path: str = None) -> str:
        """Main method to process user query through the complete pipeline"""
        try:
            print(f"Processing query: {user_input}")
            
            # Step 0: Detect user intent
            intent = self.detect_intent(user_input)
            print(f"Detected intent: {intent}")
            
            # Handle file analysis if file provided
            if file_path and intent == "file_analysis":
                return self.handle_file_analysis(file_path, user_input)
            
            # Handle complaint collection
            if intent == "complaint":
                return self.handle_complaint_initiation(user_input)
            
            # Step 1: Translate to English if needed (simplified)
            print("Translating to English...")
            english_query = self.translator.translate_to_english(user_input)
            original_language = "English" if english_query == user_input else "Other"
            print(f"Original language: {original_language}")
            print(f"Translated query: {english_query}")
            
            # Step 2: Enhanced multi-query search for comprehensive results
            print("Performing comprehensive search...")
            
            # Primary search with original query
            search_results = self.searcher.comprehensive_search(english_query)
            
            # Additional targeted searches for comprehensive coverage
            additional_searches = []
            
            # Add specific searches based on query content
            query_lower = english_query.lower()
            if any(term in query_lower for term in ["access", "unauthorized", "database", "system"]):
                additional_searches.extend(["unauthorized access", "section 43", "section 66", "computer trespass"])
            
            if any(term in query_lower for term in ["punishment", "penalty", "jail", "fine"]):
                additional_searches.extend(["punishment", "penalty", "imprisonment", "fine"])
                
            if any(term in query_lower for term in ["ipc", "indian penal code", "bns", "bharatiya nyaya sanhita"]):
                additional_searches.extend(["IPC", "Indian Penal Code", "BNS", "Bharatiya Nyaya Sanhita", "traditional criminal law"])
            
            # Perform additional searches and merge results
            for additional_query in additional_searches:
                additional_results = self.searcher.comprehensive_search(additional_query)
                
                # Merge results while avoiding duplicates
                for category in ['cyberlaw', 'faq', 'nodal_officers']:
                    existing_ids = {result.get('section_number', '') + result.get('title', '') + result.get('question', '') 
                                  for result in search_results.get(category, [])}
                    
                    for result in additional_results.get(category, []):
                        result_id = result.get('section_number', '') + result.get('title', '') + result.get('question', '')
                        if result_id not in existing_ids:
                            search_results[category].append(result)
                            existing_ids.add(result_id)
            
            # Log comprehensive search results
            cyberlaw_count = len(search_results.get('cyberlaw', []))
            faq_count = len(search_results.get('faq', []))
            officer_count = len(search_results.get('nodal_officers', []))
            print(f"Comprehensive search found: {cyberlaw_count} law sections, {faq_count} FAQs, {officer_count} officers")
            
            # Step 3: Generate response using Gemini with context
            print("Generating response...")
            response = self.generate_response(english_query, search_results, original_language, user_input)
            
            # Step 4: Add to conversation history
            self.add_to_conversation_history(user_input, english_query, response, original_language)
            
            return response
            
        except Exception as e:
            print(f"Error processing query: {e}")
            return "I apologize, but I encountered an error while processing your question. Please try again later."
    
    def handle_complaint_initiation(self, user_input: str) -> str:
        """Handle complaint collection initiation"""
        try:
            result = self.complaint_collector.start_complaint_collection(user_input)
            return result["message"]
        except Exception as e:
            print(f"Error starting complaint collection: {e}")
            return "I understand you want to file a complaint. Let me help you collect the necessary information. What type of cyber crime occurred?"
    
    def handle_file_analysis(self, file_path: str, user_input: str) -> str:
        """Handle file analysis request"""
        try:
            # Extract filename from path
            filename = os.path.basename(file_path)
            
            # Process the uploaded file
            result = self.file_processor.process_uploaded_file(file_path, filename)
            
            if not result.get("success"):
                return f"❌ **File Processing Failed**: {result.get('error', 'Unknown error')}"
            
            # Get analysis summary
            summary = self.file_processor.get_file_analysis_summary(result)
            
            # Generate additional legal advice based on analysis
            legal_advice = self.generate_file_based_legal_advice(result, user_input)
            
            return f"{summary}\n\n{legal_advice}"
            
        except Exception as e:
            print(f"Error processing file: {e}")
            return "❌ **File Analysis Error**: I encountered an error while processing your file. Please make sure it's a valid text or PDF file and try again."
    
    def generate_file_based_legal_advice(self, file_result: Dict[str, Any], user_query: str) -> str:
        """Generate legal advice based on file analysis"""
        try:
            analysis = file_result.get("analysis", {})
            potential_issues = analysis.get("potential_issues", [])
            
            if not potential_issues:
                return "**💡 LEGAL GUIDANCE**: Based on the file content, no specific legal issues were detected. If you believe there are legal concerns, please describe them and I'll provide relevant guidance."
            
            # Create a search query based on detected issues
            issue_types = [issue["type"] for issue in potential_issues[:2]]
            search_query = " ".join(issue_types).replace("_", " ") + " cyber crime law"
            
            # Search for relevant legal sections
            search_results = self.searcher.comprehensive_search(search_query)
            
            # Generate contextual legal advice
            if search_results.get("cyberlaw") or search_results.get("faq"):
                return self.generate_response(search_query, search_results, "English", user_query)
            else:
                return "**💡 LEGAL GUIDANCE**: Based on the detected issues, I recommend consulting with a cyber law expert and considering filing a complaint with your local cyber crime cell."
                
        except Exception as e:
            print(f"Error generating file-based legal advice: {e}")
            return "**💡 LEGAL GUIDANCE**: Please describe the specific legal issues you'd like help with based on the file content."
    
    def close(self):
        """Clean up resources"""
        if hasattr(self, 'searcher'):
            self.searcher.close()

def main():
    """Non-interactive service that processes a single query from command line arguments or stdin"""
    try:
        chatbot = CyberLawChatbotService()
        
        # Get query from command line argument or stdin
        if len(sys.argv) > 1:
            # Query provided as command line argument
            query = " ".join(sys.argv[1:])
        else:
            # Query provided via stdin
            print("Enter your question about cyber law:")
            query = input().strip()
        
        if not query:
            print("No query provided. Please provide a question.")
            return
        
        # Process the query
        response = chatbot.process_query(query)
        
        print("\n" + "="*60)
        print("🤖 CYBER LAW CHATBOT RESPONSE")
        print("="*60)
        print(response)
        print("="*60)
        
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure all environment variables are set properly:")
        print("- GOOGLE_API_KEY")
        print("- WEAVIATE_URL") 
        print("- WEAVIATE_API_KEY")
    finally:
        if 'chatbot' in locals():
            chatbot.close()

if __name__ == "__main__":
    main()