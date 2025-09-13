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
    
    def handle_greeting(self, user_input: str) -> str:
        """Handle greetings and casual conversation"""
        input_lower = user_input.lower().strip()
        
        # Check if this is a state/location response
        indian_states = [
            "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh", "goa", 
            "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka", "kerala", 
            "madhya pradesh", "maharashtra", "manipur", "meghalaya", "mizoram", "nagaland", 
            "odisha", "punjab", "rajasthan", "sikkim", "tamil nadu", "telangana", "tripura", 
            "uttar pradesh", "uttarakhand", "west bengal", "delhi", "puducherry", "jammu and kashmir",
            "ladakh", "andaman and nicobar", "chandigarh", "dadra and nagar haveli", "daman and diu",
            "lakshadweep"
        ]
        
        # Check if user mentioned a state
        for state in indian_states:
            if state in input_lower:
                return f"Great! I see you're from {state.title()}. I can provide cyber law guidance specific to your location. I can help you with:\n\n• Local cyber crime reporting procedures\n• State-specific nodal officers for cyber crimes\n• Regional cyber police stations\n• Local legal resources\n\nWhat specific cyber law issue would you like help with?"
        
        # Check conversation history for context
        if len(self.conversation_history) > 0:
            last_bot_response = self.conversation_history[-1].get('bot_reply', '').lower()
            if 'which state' in last_bot_response or 'location' in last_bot_response:
                # User is responding to state question
                return f"I understand you're from {user_input}. I can provide location-specific cyber law guidance. What cyber law issue would you like help with?"
        
        greeting_responses = {
            "hi": "Hello! I'm Cyberlex, your AI assistant. I'm here to help with both general questions and cyber law matters. How can I assist you today?",
            "hello": "Hi there! I'm Cyberlex, an AI assistant. I can help with various questions including cyber law guidance. What would you like to know?",
            "hey": "Hey! I'm Cyberlex, your friendly AI assistant. I'm here to help with any questions you have. What's on your mind?",
            "hai": "Hello! I'm Cyberlex, your AI assistant. I'm doing great and ready to help you! How are you doing today?",
            "how are you": "I'm doing fantastic, thank you for asking! I'm Cyberlex, an AI assistant ready to help with any questions you have. How are you today?",
            "how r u": "I'm doing great, thanks for asking! I'm Cyberlex, your friendly AI assistant. How can I help you today?",
            "good morning": "Good morning! I'm Cyberlex, your AI assistant. I hope you're having a wonderful day. How can I help you?",
            "good afternoon": "Good afternoon! I'm Cyberlex, ready to assist you with any questions you have. What can I help you with?",
            "good evening": "Good evening! I'm Cyberlex, your AI assistant. How can I help you tonight?",
            "thanks": "You're very welcome! I'm always here to help. Is there anything else I can assist you with?",
            "thank you": "You're most welcome! I'm glad I could help. Feel free to ask me anything else.",
            "bye": "Goodbye! It was great talking with you. Feel free to come back if you have any questions. Take care!",
            "goodbye": "Goodbye! Have a wonderful day! I'm always here if you need help with anything.",
            "ok": "Great! Is there anything I can help you with?",
            "okay": "Perfect! What would you like to know or discuss?"
        }
        
        # Find the best matching response
        for key, response in greeting_responses.items():
            if key in input_lower:
                return response
        
        # Default friendly response with follow-up
        return "Hello! I'm Cyberlex, your AI assistant. I can help with various topics including cyber law, general questions, and more. How can I assist you today?"
    
    def handle_state_response(self, user_input: str) -> str:
        """Handle state/location specific responses"""
        input_lower = user_input.lower().strip()
        
        # Common state mappings
        state_info = {
            "tamil nadu": {
                "name": "Tamil Nadu",
                "language": "Tamil",
                "police": "Tamil Nadu Police",
                "cybercrime": "Tamil Nadu Cyber Crime Investigation Department"
            },
            "karnataka": {
                "name": "Karnataka", 
                "language": "Kannada",
                "police": "Karnataka State Police",
                "cybercrime": "Karnataka State Cyber Crime Investigation Department"
            },
            "maharashtra": {
                "name": "Maharashtra",
                "language": "Marathi", 
                "police": "Maharashtra Police",
                "cybercrime": "Maharashtra Cyber Crime Investigation Department"
            },
            "delhi": {
                "name": "Delhi",
                "language": "Hindi",
                "police": "Delhi Police",
                "cybercrime": "Delhi Police Cyber Crime Unit"
            },
            "west bengal": {
                "name": "West Bengal",
                "language": "Bengali",
                "police": "West Bengal Police", 
                "cybercrime": "West Bengal Cyber Crime Investigation Department"
            }
        }
        
        # Find matching state
        for state_key, info in state_info.items():
            if state_key in input_lower or info["name"].lower() in input_lower:
                return f"""Great! You're from {info['name']}. I can provide state-specific guidance:

🏛️ **{info['name']} Cyber Crime Authorities:**
• **{info['cybercrime']}**
• **{info['police']}**

🌐 **Language Support:** I can assist you in {info['language']} if needed.

📍 **What specific help do you need?**
• Report a cyber crime
• File a complaint 
• Understand cyber laws
• Get legal guidance
• Find local authorities

Please let me know how you'd like to proceed, and I'll provide detailed assistance tailored for {info['name']}!"""
        
        # Generic state response
        return f"""Thank you for mentioning your location! I can provide state-specific guidance for cyber law matters.

📍 **How I can help with location-specific guidance:**
• Local cyber crime authorities and contact details
• State-specific complaint procedures  
• Regional language support
• Jurisdiction-specific legal guidance

🔍 **What would you like assistance with?**
• Reporting cyber crimes
• Understanding your legal rights
• Filing complaints
• Contacting authorities

Please let me know what specific help you need, and I'll provide detailed guidance for your area!"""
    
    def detect_intent(self, user_input: str) -> str:
        """Detect user intent (greeting, state_response, complaint, file_analysis, general_query)"""
        input_lower = user_input.lower().strip()
        
        # Check if this is a state/location response
        indian_states = [
            "andhra pradesh", "arunachal pradesh", "assam", "bihar", "chhattisgarh", "goa", 
            "gujarat", "haryana", "himachal pradesh", "jharkhand", "karnataka", "kerala", 
            "madhya pradesh", "maharashtra", "manipur", "meghalaya", "mizoram", "nagaland", 
            "odisha", "punjab", "rajasthan", "sikkim", "tamil nadu", "telangana", "tripura", 
            "uttar pradesh", "uttarakhand", "west bengal", "delhi", "puducherry", "jammu and kashmir",
            "ladakh", "andaman and nicobar", "chandigarh", "dadra and nagar haveli", "daman and diu",
            "lakshadweep"
        ]
        
        # Check if user mentioned a state (and message is short, indicating it's a response)
        if len(input_lower.split()) <= 3:
            for state in indian_states:
                if state in input_lower:
                    return "state_response"
        
        # Greeting and casual conversation indicators
        greeting_keywords = [
            "hi", "hello", "hey", "hai", "how are you", "how r u", "good morning", 
            "good afternoon", "good evening", "what's up", "whats up", "sup",
            "how you doing", "how do you do", "nice to meet", "thanks", "thank you",
            "bye", "goodbye", "see you", "good night", "take care", "ok", "okay",
            "yes", "no", "sure", "fine", "great", "cool", "awesome", "nice"
        ]
        
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
        
        # Check for greetings and simple responses first (short messages only)
        if len(input_lower.split()) <= 5 and any(keyword in input_lower for keyword in greeting_keywords):
            return "greeting"
        elif any(keyword in input_lower for keyword in complaint_keywords):
            return "complaint"
        elif any(keyword in input_lower for keyword in file_keywords):
            return "file_analysis"
        else:
            return "general_query"
    
    def is_legal_question(self, user_input: str) -> bool:
        """Check if the question is actually about legal/cyber law matters"""
        input_lower = user_input.lower()
        
        legal_keywords = [
            "law", "legal", "cyber", "crime", "hacking", "fraud", "scam", "section", "act", 
            "ipc", "bns", "it act", "punishment", "penalty", "complaint", "fir", "police",
            "court", "lawyer", "attorney", "legal advice", "violation", "offense", "illegal",
            "rights", "harassment", "stalking", "defamation", "privacy", "data breach",
            "phishing", "malware", "virus", "unauthorized access", "identity theft",
            "cybercrime", "cyber crime", "digital", "online fraud", "internet", "website",
            "social media", "facebook", "whatsapp", "instagram", "twitter", "email hack",
            "banking fraud", "credit card", "upi fraud", "fake website", "fake profile"
        ]
        
        # Check if the question contains legal keywords
        return any(keyword in input_lower for keyword in legal_keywords)
    
    def handle_general_question(self, user_input: str) -> str:
        """Handle general non-legal questions with a friendly AI response"""
        try:
            prompt = f"""
You are Cyberlex, a friendly and helpful AI assistant. The user asked: "{user_input}"

This appears to be a general question, not specifically about cyber law or legal matters. Provide a helpful, conversational response as a general AI assistant would. Be friendly, informative, and natural.

If the user asks about your capabilities, mention that you can help with:
- General questions and conversations
- Cyber law and legal guidance when needed
- Information and assistance on various topics

Keep the response natural and conversational, without forcing legal topics.
"""
            
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                return "I'm here to help! Could you tell me more about what you'd like to know?"
                
        except Exception as e:
            print(f"Error generating general response: {e}")
            return "I'm Cyberlex, your AI assistant. I'm here to help with various questions. What would you like to know?"

    def is_legal_query(self, query: str) -> bool:
        """Determine if a query is asking for legal/cyber law information"""
        legal_keywords = [
            "law", "legal", "crime", "offense", "punishment", "penalty", "fine", "jail", "prison",
            "section", "act", "ipc", "it act", "cyber", "hack", "fraud", "scam", "report", "complaint",
            "fir", "police", "court", "lawyer", "attorney", "sue", "sued", "violation", "illegal",
            "rights", "privacy", "data", "personal information", "harassment", "stalking", "defamation",
            "case", "judicial", "jurisdiction", "evidence", "investigation", "arrest", "warrant",
            "bns", "bharatiya nyaya sanhita", "indian penal code", "information technology",
            "cybercrime", "digital", "online safety", "internet law", "email fraud", "phishing",
            "identity theft", "financial fraud", "banking fraud", "social media crime"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in legal_keywords)

    def process_query(self, user_input: str, file_path: str = None) -> str:
        """Main method to process user query through the complete pipeline"""
        try:
            print(f"Processing query: {user_input}")
            
            # Step 0: Detect user intent
            intent = self.detect_intent(user_input)
            print(f"Detected intent: {intent}")
            
            # Handle greetings and casual conversation
            if intent == "greeting":
                response = self.handle_greeting(user_input)
                self.add_to_conversation_history(user_input, user_input, response, "English")
                return response
            
            # Handle state responses  
            if intent == "state_response":
                response = self.handle_state_response(user_input)
                self.add_to_conversation_history(user_input, user_input, response, "English")
                return response
            
            # Handle file analysis if file provided
            if file_path and intent == "file_analysis":
                return self.handle_file_analysis(file_path, user_input)
            
            # Handle complaint collection
            if intent == "complaint":
                return self.handle_complaint_initiation(user_input)
            
            # Check if this is actually a legal/cyber law question
            if not self.is_legal_query(user_input):
                response = self.handle_general_question(user_input)
                self.add_to_conversation_history(user_input, user_input, response, "English")
                return response
            
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
    
    def generate_dynamic_checklist(self, complaint_type: str) -> dict:
        """Generate a dynamic checklist based on complaint type using AI"""
        try:
            print(f"Generating dynamic checklist for: {complaint_type}")
            
            # Enhanced search for relevant checklist information
            search_results = self.searcher.comprehensive_search(f"complaint checklist {complaint_type} required documents evidence")
            
            # Build context from search results
            context_parts = []
            
            if search_results.get('cyberlaw'):
                context_parts.append("=== RELEVANT LEGAL REQUIREMENTS ===")
                for result in search_results['cyberlaw']:
                    context_parts.append(f"Section {result['section_number']}: {result['title']}")
                    context_parts.append(f"Content: {result['content']}")
                    context_parts.append("")
            
            if search_results.get('faq'):
                context_parts.append("=== COMPLAINT GUIDANCE ===")
                for result in search_results['faq']:
                    context_parts.append(f"Q: {result['question']}")
                    context_parts.append(f"A: {result['answer']}")
                    context_parts.append("")
            
            context = "\n".join(context_parts)
            
            # Create prompt for checklist generation
            prompt = f"""
You are Cyberlex, a professional cyber law assistant. Generate a comprehensive, customized checklist for filing a complaint about "{complaint_type}".

CONTEXT:
{context}

INSTRUCTIONS:
1. Create a detailed, practical checklist specific to "{complaint_type}"
2. Categorize items as Mandatory, Optional, and Financial (if applicable)
3. Include specific file formats, size limits, and requirements
4. Be comprehensive and professional
5. Focus on what complainants actually need to prepare

Generate a JSON response with this EXACT structure:
{{
    "title": "Checklist for {complaint_type} Complaint",
    "complaint_type": "{complaint_type}",
    "mandatory": [
        "Item 1 with specific details",
        "Item 2 with file format requirements",
        "Item 3 with size limits"
    ],
    "optional": [
        "Optional item 1",
        "Optional item 2"
    ],
    "financial": [
        "Financial item 1 (only if financial crime)",
        "Financial item 2"
    ],
    "tips": [
        "Helpful tip 1 for this complaint type",
        "Helpful tip 2 specific to {complaint_type}"
    ]
}}

SPECIFIC REQUIREMENTS FOR DIFFERENT COMPLAINT TYPES:
- FINANCIAL FRAUD: Include bank details, transaction IDs, amounts
- SOCIAL MEDIA: Include screenshots, URLs, account details
- HACKING: Include system logs, incident timeline, affected accounts
- IDENTITY THEFT: Include identity documents, fraudulent accounts
- CYBERBULLYING: Include evidence, conversation screenshots
- DATA BREACH: Include affected data, security measures, impact assessment

Provide ONLY the JSON response, no additional text.
"""

            response = self.model.generate_content(prompt)
            
            if response and response.text:
                try:
                    # Try to parse as JSON
                    import json
                    response_text = response.text.strip()
                    
                    # Clean up response if it has markdown formatting
                    if response_text.startswith('```json'):
                        response_text = response_text.replace('```json', '').replace('```', '').strip()
                    elif response_text.startswith('```'):
                        response_text = response_text.replace('```', '').strip()
                    
                    checklist_data = json.loads(response_text)
                    
                    # Validate structure
                    required_keys = ['title', 'mandatory', 'optional']
                    if all(key in checklist_data for key in required_keys):
                        return checklist_data
                    else:
                        print("Invalid checklist structure, using fallback")
                        return self._get_fallback_checklist(complaint_type)
                        
                except json.JSONDecodeError as e:
                    print(f"JSON parse error: {e}")
                    print(f"Response text: {response.text}")
                    return self._get_fallback_checklist(complaint_type)
            else:
                return self._get_fallback_checklist(complaint_type)
                
        except Exception as e:
            print(f"Error generating dynamic checklist: {e}")
            return self._get_fallback_checklist(complaint_type)
    
    def _get_fallback_checklist(self, complaint_type: str) -> dict:
        """Fallback checklist when AI generation fails"""
        base_checklist = {
            "title": f"Checklist for {complaint_type} Complaint",
            "complaint_type": complaint_type,
            "mandatory": [
                "Incident Date and Time",
                "Detailed incident description (minimum 200 characters) without special characters (#$@^*`''~|!)",
                "Soft copy of national ID (Voter ID, Driving License, Passport, PAN Card, Aadhar Card) in .jpeg, .jpg, .png format (max 5 MB)",
                "All relevant evidence related to the cyber crime (max 10 MB each)"
            ],
            "optional": [
                "Suspected website URLs/Social Media handles (if applicable)",
                "Suspect details: mobile number, email ID, bank account, address",
                "Photograph of suspect in .jpeg, .jpg, .png format (max 5 MB)",
                "Any other documents for suspect identification"
            ],
            "financial": [],
            "tips": [
                "Ensure all documents are clear and readable",
                "Take screenshots of digital evidence before they disappear",
                "Keep original copies of all documents safe"
            ]
        }
        
        # Add specific items based on complaint type
        complaint_lower = complaint_type.lower()
        
        if any(keyword in complaint_lower for keyword in ['financial', 'fraud', 'money', 'bank', 'payment']):
            base_checklist["financial"] = [
                "Name of Bank/Wallet/Merchant involved",
                "12-digit Transaction ID/UTR Number",
                "Date and time of fraudulent transaction",
                "Exact fraud amount",
                "Bank statement showing the transaction"
            ]
            
        if any(keyword in complaint_lower for keyword in ['social', 'facebook', 'instagram', 'twitter', 'whatsapp']):
            base_checklist["mandatory"].append("Screenshots of offending posts/messages")
            base_checklist["optional"].append("Social media profile URLs of suspect")
            
        if any(keyword in complaint_lower for keyword in ['hacking', 'unauthorized', 'access', 'breach']):
            base_checklist["mandatory"].extend([
                "System logs showing unauthorized access",
                "Timeline of when unauthorized access was discovered",
                "List of affected accounts/systems"
            ])
            
        return base_checklist
    
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

    def generate_dynamic_checklist(self, complaint_type: str) -> dict:
        """Generate a dynamic, AI-powered checklist based on complaint type"""
        try:
            print(f"Generating dynamic checklist for: {complaint_type}")
            
            # Use AI to generate customized checklist
            prompt = f"""
You are Cyberlex, a professional cyber law assistant. Generate a comprehensive, customized checklist for filing a complaint about "{complaint_type}".

Based on the complaint type "{complaint_type}", provide a specific and actionable checklist. Consider what evidence and information would be most important for this particular type of cyber crime.

Provide your response in this EXACT JSON format:

{{
    "title": "Checklist for {complaint_type} Complaint",
    "mandatory": [
        {{
            "item": "Specific evidence item",
            "description": "Detailed description of what exactly is needed for {complaint_type} cases",
            "format": "File format or specification if applicable"
        }}
    ],
    "optional": [
        {{
            "item": "Additional helpful item",
            "description": "How this specifically helps with {complaint_type} investigations",
            "format": "Format requirements if any"
        }}
    ],
    "specific_tips": [
        "Actionable tip specific to {complaint_type}",
        "Another tip focused on {complaint_type} evidence collection"
    ]
}}

For "{complaint_type}" specifically focus on:

1. What digital evidence is most crucial?
2. What platform-specific information is needed?
3. What documentation helps law enforcement?
4. What technical details matter for this crime type?
5. What immediate actions should victims take?

Make each item highly specific to "{complaint_type}" rather than generic cyber crime advice.

Generate the JSON response:
"""

            # Generate AI response
            response = self.model.generate_content(prompt)
            
            if response and response.text:
                try:
                    import json
                    response_text = response.text.strip()
                    
                    # Clean up response if it has markdown formatting
                    if response_text.startswith('```json'):
                        response_text = response_text.replace('```json', '').replace('```', '')
                    elif response_text.startswith('```'):
                        response_text = response_text.replace('```', '')
                    
                    checklist_data = json.loads(response_text)
                    print(f"Successfully generated dynamic checklist with {len(checklist_data.get('mandatory', []))} mandatory items")
                    return checklist_data
                    
                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON response: {e}")
                    print(f"Raw response: {response.text}")
                    return self._generate_fallback_checklist(complaint_type)
            else:
                print("No response from AI model")
                return self._generate_fallback_checklist(complaint_type)
                
        except Exception as e:
            print(f"Error generating dynamic checklist: {e}")
            return self._generate_fallback_checklist(complaint_type)
    
    def _generate_fallback_checklist(self, complaint_type: str) -> dict:
        """Generate a fallback checklist when AI fails - customized by complaint type"""
        
        complaint_lower = complaint_type.lower()
        
        if "social media" in complaint_lower or "profile" in complaint_lower or "fake" in complaint_lower:
            return {
                "title": f"Checklist for {complaint_type} Complaint",
                "mandatory": [
                    {
                        "item": "Fake Profile Screenshots",
                        "description": "Complete screenshots of the fake profile showing display name, username, profile picture, bio, posts, and follower count",
                        "format": ".jpeg, .jpg, .png | Max size: 5 MB each"
                    },
                    {
                        "item": "Your Original Profile Evidence", 
                        "description": "Screenshots of your legitimate profile to prove identity theft and show the original content being misused",
                        "format": ".jpeg, .jpg, .png | Max size: 5 MB each"
                    },
                    {
                        "item": "Profile URL and Username",
                        "description": "Direct link to the fake profile and exact username before it gets deleted or changed",
                        "format": "Complete URL and username text"
                    },
                    {
                        "item": "Discovery Date and Method",
                        "description": "When and how you discovered the fake profile (friend told you, found while searching, etc.)",
                        "format": "Date, time, and detailed explanation"
                    },
                    {
                        "item": "Misused Content Evidence",
                        "description": "Screenshots showing your original photos/content being used on the fake profile",
                        "format": "Side-by-side comparison screenshots"
                    },
                    {
                        "item": "Impact Documentation",
                        "description": "Evidence of how the fake profile has affected you (messages from confused friends, business impact, etc.)",
                        "format": "Screenshots of conversations or written statements"
                    }
                ],
                "optional": [
                    {
                        "item": "Platform Report Reference",
                        "description": "Reference number if you've already reported to the social media platform",
                        "format": "Platform complaint ID or case number"
                    },
                    {
                        "item": "Suspect Clues",
                        "description": "Any information that might help identify who created the fake profile",
                        "format": "Phone numbers, email addresses, mutual connections, or behavioral patterns"
                    },
                    {
                        "item": "Communication from Fake Profile", 
                        "description": "Screenshots of any messages, comments, or posts made by the fake profile",
                        "format": "Full conversation screenshots with timestamps"
                    }
                ],
                "specific_tips": [
                    "Screenshot everything immediately - fake profiles can be deleted quickly",
                    "Save the profile URL and username before reporting to the platform",
                    "Document any financial or reputational damage caused",
                    "Report to the platform first, then file police complaint with reference number",
                    "Keep evidence of your original content that was stolen"
                ]
            }
        
        elif "financial" in complaint_lower or "fraud" in complaint_lower or "money" in complaint_lower:
            return {
                "title": f"Checklist for {complaint_type} Complaint", 
                "mandatory": [
                    {
                        "item": "Complete Transaction History",
                        "description": "Bank statements showing all fraudulent transactions with timestamps and amounts",
                        "format": "PDF bank statements, transaction SMS screenshots"
                    },
                    {
                        "item": "Fraudulent Communication",
                        "description": "Screenshots of fake messages, emails, or calls that led to the fraud",
                        "format": ".jpeg, .jpg, .png | Include phone numbers and timestamps"
                    },
                    {
                        "item": "12-digit Transaction ID/UTR",
                        "description": "Unique transaction reference number for each fraudulent transaction",
                        "format": "Exact 12-digit number from bank SMS or app"
                    },
                    {
                        "item": "Beneficiary Account Details",
                        "description": "Account number, IFSC code, and bank name where your money was transferred",
                        "format": "Complete banking details from transaction receipt"
                    }
                ],
                "optional": [
                    {
                        "item": "Fraud Website/App Details",
                        "description": "Screenshots and URLs of fake websites or apps used in the fraud",
                        "format": "Full page screenshots with URL visible"
                    },
                    {
                        "item": "Bank Complaint Reference",
                        "description": "Reference number from your bank's fraud complaint",
                        "format": "Bank complaint number and date"
                    }
                ],
                "specific_tips": [
                    "Report to bank immediately to freeze further transactions",
                    "File complaint within 24 hours for better recovery chances", 
                    "Save all communication with fraudsters",
                    "Document the fraud method used (fake website, phishing call, etc.)"
                ]
            }
        
        else:
            # Generic checklist for other types
            return {
                "title": f"Checklist for {complaint_type} Complaint",
                "mandatory": [
                    {
                        "item": "Incident Date and Time",
                        "description": f"Exact date and time when the {complaint_type.lower()} incident occurred",
                        "format": "DD/MM/YYYY and HH:MM format"
                    },
                    {
                        "item": "Detailed Incident Report",
                        "description": f"Comprehensive description of the {complaint_type.lower()} incident including what happened, how it happened, and impact",
                        "format": "Minimum 200 characters, no special characters (#$@^*`''~|!)"
                    },
                    {
                        "item": "Digital Evidence",
                        "description": f"All relevant digital evidence including screenshots, files, logs, or communications related to the {complaint_type.lower()}",
                        "format": "Screenshots, documents, chat logs | Max size: 10 MB each"
                    },
                    {
                        "item": "Identity Verification",
                        "description": "Government-issued photo identification to verify your identity as the complainant",
                        "format": "Voter ID, Driving License, Passport, PAN Card, or Aadhar Card | .jpeg, .jpg, .png | Max size: 5 MB"
                    }
                ],
                "optional": [
                    {
                        "item": "Suspect Information",
                        "description": "Any available information about the person/entity responsible for the incident",
                        "format": "Names, contact details, social media accounts, or any identifying information"
                    },
                    {
                        "item": "Witness Information",
                        "description": "Details of people who witnessed the incident or can provide supporting testimony",
                        "format": "Names, contact information, and brief statements"
                    },
                    {
                        "item": "Previous Reports",
                        "description": "Reference numbers of any previous complaints filed with other agencies or platforms",
                        "format": "Complaint numbers, dates, and agency names"
                    }
                ],
                "specific_tips": [
                    f"Preserve all evidence related to {complaint_type.lower()} immediately to prevent loss",
                    "Document everything with timestamps and detailed descriptions",
                    "Report to relevant authorities as soon as possible",
                    "Keep copies of all submitted documents for your records"
                ]
            }

    def close(self):
        """Close all connections"""
        try:
            if hasattr(self, 'searcher'):
                self.searcher.close()
        except Exception as e:
            print(f"Error closing connections: {e}")

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