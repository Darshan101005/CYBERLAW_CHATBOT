"""
MASTER CYBER LAW CHATBOT - CONSOLIDATED VERSION
All-in-one comprehensive cyber law assistance system
Features: Multilingual support, complaint collection, file analysis, color-coded legal guidance
"""

import os
import sys
import json
import weaviate
import google.generativeai as genai
from datetime import datetime
from dotenv import load_dotenv
from typing import Dict, List, Any
import tempfile
import re

load_dotenv()

class MasterCyberLawChatbot:
    def __init__(self):
        """Initialize the comprehensive chatbot system"""
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.weaviate_url = os.getenv('WEAVIATE_URL')
        self.weaviate_api_key = os.getenv('WEAVIATE_API_KEY')
        
        if not all([self.google_api_key, self.weaviate_url, self.weaviate_api_key]):
            raise ValueError("Missing required environment variables")
        
        genai.configure(api_key=self.google_api_key)
        
        # Initialize core components
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        self.conversation_history = []
        self.max_history_turns = 6
        
        # Session state management
        self.active_complaint_id = None
        self.session_state = "general"  # general, complaint_collection, file_analysis
        
        # Initialize Weaviate client
        self.client = weaviate.connect_to_weaviate_cloud(
            cluster_url=self.weaviate_url,
            auth_credentials=weaviate.auth.AuthApiKey(self.weaviate_api_key)
        )
        
        # Initialize directories
        self.complaint_dir = "CYBERLAW_CHATBOT/complaints"
        self.ensure_directories()
        
        # Load police station data
        self.police_stations = self.load_police_stations()
        
        # Initialize act categorization system
        self.setup_act_categories()
        
        # Setup contextual complaint questions
        self.setup_contextual_complaints()
        
        print("🤖 Master Cyber Law Chatbot initialized successfully!")
    
    def ensure_directories(self):
        """Create necessary directories"""
        if not os.path.exists(self.complaint_dir):
            os.makedirs(self.complaint_dir)
    
    def load_police_stations(self) -> List[Dict]:
        """Load police station data"""
        try:
            # Try multiple possible paths
            possible_paths = [
                "CYBERLAW_CHATBOT/data/police_stations.json",
                "data/police_stations.json",
                "../data/police_stations.json"
            ]
            
            for path in possible_paths:
                try:
                    with open(path, "r") as f:
                        return json.load(f)
                except FileNotFoundError:
                    continue
            
            # If none found, create default stations
            return self.get_default_police_stations()
            
        except Exception as e:
            print(f"Warning: Could not load police stations data: {e}")
            return self.get_default_police_stations()
    
    def get_default_police_stations(self) -> List[Dict]:
        """Return default police stations if file not found"""
        return [
            {
                "station_name": "National Cyber Crime Reporting Portal",
                "address": "Online Portal - cybercrime.gov.in",
                "phone": "155260",
                "email": "cybercrime@gov.in",
                "in_charge": "Central Cyber Crime Unit",
                "jurisdiction": ["All India"]
            },
            {
                "station_name": "Delhi Cyber Crime Unit",
                "address": "I.P. Estate, New Delhi - 110002",
                "phone": "+91-11-23379999",
                "email": "dcp-cybercrime-delhi@delhipolice.gov.in",
                "in_charge": "DCP Cyber Crime",
                "jurisdiction": ["Delhi", "NCR"]
            },
            {
                "station_name": "Mumbai Cyber Crime Investigation Cell",
                "address": "DCP Office, BKC, Bandra East, Mumbai - 400051",
                "phone": "+91-22-26484088",
                "email": "cybercrime.mumbai@maharashtrapolice.gov.in",
                "in_charge": "ACP Cyber Crime",
                "jurisdiction": ["Mumbai", "Maharashtra"]
            }
        ]
    
    def setup_act_categories(self):
        """Setup color-coded act categorization"""
        self.categories = {
            "CRITICAL": {
                "color": "🔴",
                "html_color": "#FF4444",
                "description": "Serious cyber crimes with severe penalties"
            },
            "GENERAL": {
                "color": "🟡", 
                "html_color": "#FFD700",
                "description": "Standard cyber offenses"
            },
            "PROCEDURAL": {
                "color": "🟢",
                "html_color": "#32CD32",
                "description": "Definitions and procedures"
            }
        }
        
        # Critical sections mapping
        self.critical_sections = {
            "77": "Voyeurism - serious privacy violation",
            "78": "Stalking - harassment with severe impact",
            "503": "Criminal intimidation - serious threat",
            "506": "Punishment for criminal intimidation",
            "507": "Anonymous criminal intimidation",
            "292": "Obscene material distribution",
            "66": "Computer related offenses",
            "67": "Publishing obscene information",
            "66A": "Punishment for sending offensive messages",
            "66C": "Identity theft",
            "66D": "Cheating by personation using computer",
            "66E": "Violation of privacy"
        }
        
        self.general_sections = {
            "500": "Defamation - reputation damage",
            "354D": "Stalking",
            "509": "Word, gesture or act intended to insult modesty",
            "419": "Cheating by personation",
            "420": "Cheating and dishonestly inducing delivery of property"
        }
        
        self.procedural_sections = {
            "1": "Title and application of IT Act",
            "2": "Definitions of technical terms",
            "75": "Application of Act to offences"
        }
    
    def setup_contextual_complaints(self):
        """Setup contextual complaint questions based on incident type"""
        self.contextual_questions = {
            "financial_fraud": [
                {"field": "transaction_details", "question": "What are the transaction details (amount, account number, UPI ID)?", "required": True},
                {"field": "bank_name", "question": "Which bank or payment service was involved?", "required": True},
                {"field": "fraud_method", "question": "How did the fraud occur? (fake call, phishing, fake website, etc.)", "required": True},
                {"field": "unauthorized_transactions", "question": "List all unauthorized transactions with amounts and dates:", "required": True}
            ],
            "online_harassment": [
                {"field": "harassment_platform", "question": "On which platform did the harassment occur? (WhatsApp, Instagram, Facebook, etc.)", "required": True},
                {"field": "harassment_type", "question": "What type of harassment? (messages, calls, fake profiles, morphed images, etc.)", "required": True},
                {"field": "harasser_details", "question": "Any details about the harasser? (profile name, phone number, etc.)", "required": False},
                {"field": "impact_description", "question": "How has this harassment affected you? (mental stress, reputation damage, etc.)", "required": True}
            ],
            "identity_theft": [
                {"field": "stolen_information", "question": "What personal information was stolen? (Aadhaar, PAN, photos, documents, etc.)", "required": True},
                {"field": "misuse_details", "question": "How is your identity being misused? (fake accounts, financial fraud, etc.)", "required": True},
                {"field": "discovery_method", "question": "How did you discover the identity theft?", "required": True}
            ],
            "hacking": [
                {"field": "compromised_accounts", "question": "Which accounts were hacked? (email, social media, banking, etc.)", "required": True},
                {"field": "access_method", "question": "How do you think they gained access? (weak password, phishing, etc.)", "required": False},
                {"field": "damage_assessment", "question": "What damage has been done? (data theft, unauthorized posts, financial loss, etc.)", "required": True}
            ],
            "online_fraud": [
                {"field": "fraud_platform", "question": "Where did the fraud occur? (online shopping, fake website, email, etc.)", "required": True},
                {"field": "promised_service", "question": "What was promised to you? (product, service, investment opportunity, etc.)", "required": True},
                {"field": "payment_method", "question": "How did you pay? (UPI, card, bank transfer, etc.)", "required": True}
            ]
        }
    
    # ===========================================
    # TRANSLATION MODULE
    # ===========================================
    
    def detect_language_and_translate(self, text: str) -> Dict[str, str]:
        """Detect language and translate to English if needed"""
        try:
            detection_prompt = f"""
            Detect the language of this text and translate it to English if it's not already in English.
            
            Text: "{text}"
            
            Respond in this exact JSON format:
            {{
                "original_language": "detected_language_name",
                "is_english": true/false,
                "translated_text": "english_translation_here"
            }}
            
            If the text is already in English, return the same text as translated_text.
            """
            
            response = self.model.generate_content(detection_prompt)
            if response and response.text:
                try:
                    result = json.loads(response.text.strip())
                    return {
                        "original_language": result.get("original_language", "English"),
                        "translated_text": result.get("translated_text", text)
                    }
                except json.JSONDecodeError:
                    pass
            
            return {"original_language": "English", "translated_text": text}
            
        except Exception as e:
            print(f"Translation error: {e}")
            return {"original_language": "English", "translated_text": text}
    
    # ===========================================
    # VECTOR SEARCH MODULE
    # ===========================================
    
    def generate_query_embedding(self, query: str) -> List[float]:
        """Generate embedding for search query"""
        try:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=query,
                task_type="retrieval_query"
            )
            return result['embedding']
        except Exception as e:
            print(f"Embedding error: {e}")
            return []
    
    def search_cyberlaw(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search legal sections"""
        try:
            query_vector = self.generate_query_embedding(query)
            if not query_vector:
                return []
            
            collection = self.client.collections.get("CyberLaw")
            response = collection.query.near_vector(
                near_vector=query_vector,
                limit=limit,
                return_metadata=weaviate.classes.query.MetadataQuery(distance=True)
            )
            
            results = []
            for item in response.objects:
                results.append({
                    "section_number": item.properties.get('section_number', ''),
                    "title": item.properties.get('title', ''),
                    "content": item.properties.get('content', ''),
                    "law_type": item.properties.get('law_type', ''),
                    "summary": item.properties.get('summary', ''),
                    "full_text": item.properties.get('full_text', ''),
                    "source_file": item.properties.get('source_file', ''),
                    "distance": item.metadata.distance if item.metadata else None
                })
            
            return results
        except Exception as e:
            print(f"CyberLaw search error: {e}")
            return []
    
    def search_faq(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search FAQs"""
        try:
            query_vector = self.generate_query_embedding(query)
            if not query_vector:
                return []
            
            collection = self.client.collections.get("FAQ")
            response = collection.query.near_vector(
                near_vector=query_vector,
                limit=limit,
                return_metadata=weaviate.classes.query.MetadataQuery(distance=True)
            )
            
            results = []
            for item in response.objects:
                results.append({
                    "question": item.properties.get('question', ''),
                    "answer": item.properties.get('answer', ''),
                    "category": item.properties.get('category', ''),
                    "distance": item.metadata.distance if item.metadata else None
                })
            
            return results
        except Exception as e:
            print(f"FAQ search error: {e}")
            return []
    
    def search_nodal_officers(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search nodal officers"""
        try:
            query_vector = self.generate_query_embedding(query)
            if not query_vector:
                return []
            
            collection = self.client.collections.get("NodalOfficer")
            response = collection.query.near_vector(
                near_vector=query_vector,
                limit=limit,
                return_metadata=weaviate.classes.query.MetadataQuery(distance=True)
            )
            
            results = []
            for item in response.objects:
                results.append({
                    "state": item.properties.get('state', ''),
                    "officer_name": item.properties.get('officer_name', ''),
                    "rank": item.properties.get('rank', ''),
                    "email": item.properties.get('email', ''),
                    "contact": item.properties.get('contact', ''),
                    "office_address": item.properties.get('office_address', ''),
                    "distance": item.metadata.distance if item.metadata else None
                })
            
            return results
        except Exception as e:
            print(f"Nodal officer search error: {e}")
            return []
    
    def comprehensive_search(self, query: str) -> Dict[str, List[Dict[str, Any]]]:
        """Perform comprehensive search across all collections"""
        return {
            "cyberlaw": self.search_cyberlaw(query),
            "faq": self.search_faq(query),
            "nodal_officers": self.search_nodal_officers(query)
        }
    
    # ===========================================
    # ACT CATEGORIZATION MODULE
    # ===========================================
    
    def categorize_section(self, section_number: str, law_type: str = None, content: str = None) -> dict:
        """Categorize legal section with color coding"""
        section_key = section_number.strip()
        
        if section_key in self.critical_sections:
            return {
                "category": "CRITICAL",
                "color": self.categories["CRITICAL"]["color"],
                "html_color": self.categories["CRITICAL"]["html_color"],
                "description": self.critical_sections[section_key]
            }
        elif section_key in self.general_sections:
            return {
                "category": "GENERAL", 
                "color": self.categories["GENERAL"]["color"],
                "html_color": self.categories["GENERAL"]["html_color"],
                "description": self.general_sections[section_key]
            }
        elif section_key in self.procedural_sections:
            return {
                "category": "PROCEDURAL",
                "color": self.categories["PROCEDURAL"]["color"], 
                "html_color": self.categories["PROCEDURAL"]["html_color"],
                "description": self.procedural_sections[section_key]
            }
        else:
            # Default categorization based on content analysis
            if content and any(keyword in content.lower() for keyword in ["imprisonment", "punishment", "penalty", "fine"]):
                if any(severity in content.lower() for severity in ["seven years", "10 years", "life imprisonment", "death"]):
                    return {
                        "category": "CRITICAL",
                        "color": self.categories["CRITICAL"]["color"],
                        "html_color": self.categories["CRITICAL"]["html_color"], 
                        "description": "Serious offense with severe punishment"
                    }
                else:
                    return {
                        "category": "GENERAL",
                        "color": self.categories["GENERAL"]["color"],
                        "html_color": self.categories["GENERAL"]["html_color"],
                        "description": "Standard offense"
                    }
            else:
                return {
                    "category": "PROCEDURAL",
                    "color": self.categories["PROCEDURAL"]["color"],
                    "html_color": self.categories["PROCEDURAL"]["html_color"],
                    "description": "Procedural or definitional section"
                }
    
    def format_colored_section(self, section_number: str, title: str, law_type: str, content: str = "") -> str:
        """Format section with color coding"""
        category_info = self.categorize_section(section_number, law_type, content)
        color_emoji = category_info["color"]
        category_name = category_info["category"]
        
        return f"{color_emoji} **{law_type} Section {section_number}** ({category_name}): {title}"
    
    # ===========================================
    # POLICE STATION FINDER MODULE
    # ===========================================
    
    def find_nearby_police_stations(self, user_location: str) -> List[Dict[str, Any]]:
        """Find nearby police stations based on user location"""
        user_location_lower = user_location.lower()
        matches = []
        
        for station in self.police_stations:
            # Check if location matches state, city, or jurisdiction
            location_matches = (
                user_location_lower in station["state"].lower() or
                user_location_lower in station["city"].lower() or
                any(user_location_lower in jurisdiction.lower() for jurisdiction in station["jurisdiction"])
            )
            
            if location_matches:
                matches.append({
                    "station_name": station["station_name"],
                    "address": station["address"],
                    "phone": station["phone"],
                    "email": station["email"],
                    "in_charge": station["in_charge"],
                    "jurisdiction": station["jurisdiction"]
                })
        
        # If no exact matches, suggest major cyber crime units
        if not matches:
            return [
                {
                    "station_name": "National Cyber Crime Reporting Portal",
                    "address": "Online Portal - cybercrime.gov.in",
                    "phone": "155260",
                    "email": "cybercrime@gov.in",
                    "in_charge": "Central Cyber Crime Unit",
                    "jurisdiction": ["All India"]
                }
            ]
        
        return matches[:3]  # Return top 3 matches
    
    # ===========================================
    # COMPLAINT COLLECTION MODULE  
    # ===========================================
    
    def generate_complaint_id(self) -> str:
        """Generate unique complaint ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"CYBER_{timestamp}"
    
    def get_contextual_questions(self, incident_type: str) -> List[Dict]:
        """Get additional questions based on incident type"""
        incident_lower = incident_type.lower()
        
        if any(keyword in incident_lower for keyword in ["fraud", "money", "payment", "transaction", "bank"]):
            return self.contextual_questions.get("financial_fraud", [])
        elif any(keyword in incident_lower for keyword in ["harassment", "bullying", "threat", "abuse"]):
            return self.contextual_questions.get("online_harassment", [])
        elif any(keyword in incident_lower for keyword in ["identity", "theft", "fake", "impersonation"]):
            return self.contextual_questions.get("identity_theft", [])
        elif any(keyword in incident_lower for keyword in ["hack", "breach", "unauthorized", "access"]):
            return self.contextual_questions.get("hacking", [])
        elif any(keyword in incident_lower for keyword in ["scam", "fake website", "phishing"]):
            return self.contextual_questions.get("online_fraud", [])
        else:
            return []  # Generic questions only
    
    def start_complaint_collection(self, user_input: str) -> dict:
        """Start interactive complaint collection"""
        complaint_id = self.generate_complaint_id()
        
        # Base questions for all complaints
        base_questions = [
            {"field": "full_name", "question": "What is your full name?", "required": True},
            {"field": "phone", "question": "Please provide your phone number for contact:", "required": True},
            {"field": "email", "question": "Your email address:", "required": True},
            {"field": "location", "question": "Your current location (city/state) for finding nearby police stations:", "required": True},
            {"field": "address", "question": "Your complete address:", "required": True},
            {"field": "incident_type", "question": "What type of cyber crime occurred? (fraud, hacking, harassment, identity theft, etc.)", "required": True},
            {"field": "incident_date", "question": "When did this incident occur? (date and time if possible)", "required": True},
            {"field": "incident_description", "question": "Please describe the incident in detail:", "required": True}
        ]
        
        initial_state = {
            "complaint_id": complaint_id,
            "status": "collecting",
            "current_question_index": 0,
            "all_questions": base_questions,  # Will be expanded with contextual questions
            "collected_data": {
                "initial_complaint": user_input,
                "timestamp": datetime.now().isoformat(),
                "answers": {},
                "suggested_police_stations": [],
                "confirmation_pending": False
            },
            "total_questions": len(base_questions)
        }
        
        # Save initial state
        self.save_complaint_state(initial_state)
        
        return {
            "complaint_id": complaint_id,
            "message": f"""
**🚨 COMPLAINT COLLECTION STARTED**

I understand you want to report a cyber crime. I'll help you collect all the necessary information that authorities will need to take action.

**Complaint ID:** {complaint_id}

Let's start with some basic information:

**Question 1/{len(base_questions)}:** {base_questions[0]["question"]}

*Note: Your information will be stored securely and can be forwarded to the appropriate authorities.*
""",
            "next_question": base_questions[0],
            "progress": f"1/{len(base_questions)} questions"
        }
    
    def process_complaint_answer(self, complaint_id: str, answer: str) -> dict:
        """Process complaint answer and move to next question"""
        # Load complaint state
        state = self.load_complaint_state(complaint_id)
        if not state:
            return {"error": "Complaint ID not found"}
        
        # Save current answer
        current_question = state["all_questions"][state["current_question_index"]]
        field_name = current_question["field"]
        state["collected_data"]["answers"][field_name] = answer.strip()
        
        # Special handling for incident_type to add contextual questions
        if field_name == "incident_type":
            contextual_questions = self.get_contextual_questions(answer)
            if contextual_questions:
                # Insert contextual questions after basic questions
                insert_index = state["current_question_index"] + 1
                for i, q in enumerate(contextual_questions):
                    state["all_questions"].insert(insert_index + i, q)
                state["total_questions"] = len(state["all_questions"])
        
        # Special handling for location to suggest police stations
        if field_name == "location":
            police_stations = self.find_nearby_police_stations(answer)
            state["collected_data"]["suggested_police_stations"] = police_stations
        
        # Move to next question
        state["current_question_index"] += 1
        
        # Check if we've reached the end
        if state["current_question_index"] >= len(state["all_questions"]):
            # Show confirmation before final save
            return self.show_complaint_confirmation(state)
        
        # Save state and return next question
        self.save_complaint_state(state)
        
        next_question = state["all_questions"][state["current_question_index"]]
        progress = f"{state['current_question_index'] + 1}/{state['total_questions']}"
        
        return {
            "complaint_id": complaint_id,
            "message": f"**Question {progress}:** {next_question['question']}",
            "next_question": next_question,
            "progress": progress,
            "status": "collecting"
        }
    
    def show_complaint_confirmation(self, state: dict) -> dict:
        """Show all collected data for confirmation"""
        answers = state["collected_data"]["answers"]
        police_stations = state["collected_data"]["suggested_police_stations"]
        
        # Format collected data for review
        confirmation_text = f"""
**📋 COMPLAINT SUMMARY - PLEASE REVIEW**

**Personal Information:**
• Name: {answers.get('full_name', 'Not provided')}
• Phone: {answers.get('phone', 'Not provided')}
• Email: {answers.get('email', 'Not provided')}
• Location: {answers.get('location', 'Not provided')}
• Address: {answers.get('address', 'Not provided')}

**Incident Details:**
• Type: {answers.get('incident_type', 'Not specified')}
• Date: {answers.get('incident_date', 'Not specified')}
• Description: {answers.get('incident_description', 'Not provided')}
"""
        
        # Add contextual details if available
        for field, value in answers.items():
            if field not in ['full_name', 'phone', 'email', 'location', 'address', 'incident_type', 'incident_date', 'incident_description']:
                confirmation_text += f"• {field.replace('_', ' ').title()}: {value}\n"
        
        # Add suggested police stations
        if police_stations:
            confirmation_text += f"""
**🚔 SUGGESTED POLICE STATIONS FOR YOUR LOCATION:**
"""
            for i, station in enumerate(police_stations[:2], 1):
                confirmation_text += f"""
**{i}. {station['station_name']}**
   📍 Address: {station['address']}
   📞 Phone: {station['phone']}
   📧 Email: {station['email']}
   👮 In-charge: {station['in_charge']}
"""
        
        confirmation_text += """
**⚠️ PLEASE CONFIRM:**
• Type "YES" to save this complaint and generate the final report
• Type "NO" to cancel 
• Type "EDIT [field_name]" to modify any specific field (e.g., "EDIT phone")

Your complaint will be saved securely and can be submitted to authorities.
"""
        
        # Mark as pending confirmation
        state["collected_data"]["confirmation_pending"] = True
        self.save_complaint_state(state)
        
        return {
            "complaint_id": state["complaint_id"],
            "message": confirmation_text,
            "status": "confirmation_pending"
        }
    
    def handle_complaint_confirmation(self, complaint_id: str, response: str) -> dict:
        """Handle confirmation response"""
        state = self.load_complaint_state(complaint_id)
        if not state:
            return {"error": "Complaint ID not found"}
        
        response_lower = response.strip().lower()
        
        if response_lower == "yes":
            # Save final complaint
            return self.finalize_complaint(state)
        elif response_lower == "no":
            # Cancel complaint
            return {
                "message": "Complaint collection cancelled. Thank you. If you need help with anything else, please let me know.",
                "status": "cancelled"
            }
        elif response_lower.startswith("edit "):
            # Handle field editing
            field_name = response_lower.replace("edit ", "").strip()
            return self.handle_field_edit(state, field_name)
        else:
            return {
                "message": "Please respond with 'YES' to confirm, 'NO' to cancel, or 'EDIT [field_name]' to modify a field.",
                "status": "confirmation_pending"
            }
    
    def finalize_complaint(self, state: dict) -> dict:
        """Save final complaint file"""
        complaint_id = state["complaint_id"]
        
        # Create final complaint document
        final_complaint = {
            "complaint_id": complaint_id,
            "submission_date": datetime.now().isoformat(),
            "complainant_details": {
                "name": state["collected_data"]["answers"].get("full_name"),
                "phone": state["collected_data"]["answers"].get("phone"),
                "email": state["collected_data"]["answers"].get("email"),
                "address": state["collected_data"]["answers"].get("address"),
                "location": state["collected_data"]["answers"].get("location")
            },
            "incident_details": {
                "type": state["collected_data"]["answers"].get("incident_type"),
                "date_time": state["collected_data"]["answers"].get("incident_date"),
                "description": state["collected_data"]["answers"].get("incident_description"),
                "additional_details": {k: v for k, v in state["collected_data"]["answers"].items() 
                                     if k not in ["full_name", "phone", "email", "address", "location", "incident_type", "incident_date", "incident_description"]}
            },
            "suggested_police_stations": state["collected_data"]["suggested_police_stations"],
            "initial_complaint": state["collected_data"]["initial_complaint"],
            "collection_completed": datetime.now().isoformat()
        }
        
        # Save final complaint file
        final_file_path = f"{self.complaint_dir}/FINAL_{complaint_id}.json"
        with open(final_file_path, "w") as f:
            json.dump(final_complaint, f, indent=2)
        
        # Update state
        state["status"] = "completed"
        self.save_complaint_state(state)
        
        return {
            "message": f"""
**✅ COMPLAINT COLLECTION COMPLETED**

Your complaint has been successfully recorded and saved.

**Complaint ID:** {complaint_id}
**File saved:** {final_file_path}

**Next Steps:**
1. Your complaint file is ready for submission to authorities
2. Contact the suggested police stations with your complaint ID
3. Keep this complaint ID for future reference
4. You can download the complaint file and submit it to the cyber crime cell

**Emergency Contact:** For immediate assistance, call 1930 (Cyber Crime Helpline)

Thank you for using our cyber law assistance system. Stay safe online!
""",
            "status": "completed",
            "file_path": final_file_path,
            "complaint_id": complaint_id
        }
    
    def save_complaint_state(self, state: dict):
        """Save complaint state to file"""
        complaint_id = state["complaint_id"]
        state_file = f"{self.complaint_dir}/STATE_{complaint_id}.json"
        with open(state_file, "w") as f:
            json.dump(state, f, indent=2)
    
    def load_complaint_state(self, complaint_id: str) -> dict:
        """Load complaint state from file"""
        state_file = f"{self.complaint_dir}/STATE_{complaint_id}.json"
        try:
            with open(state_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    # ===========================================
    # FILE PROCESSING MODULE
    # ===========================================
    
    def process_uploaded_file(self, file_path: str, filename: str) -> dict:
        """Process uploaded file for legal analysis"""
        try:
            file_extension = os.path.splitext(filename)[1].lower()
            
            if file_extension == ".txt":
                content = self.extract_text_content(file_path)
            elif file_extension == ".json":
                content = self.extract_json_content(file_path)
            elif file_extension == ".pdf":
                content = self.extract_pdf_content(file_path)
            else:
                return {"success": False, "error": f"Unsupported file type: {file_extension}"}
            
            if not content:
                return {"success": False, "error": "Could not extract content from file"}
            
            # Analyze content for legal issues
            analysis = self.analyze_file_content(content)
            
            return {
                "success": True,
                "processed_id": f"FILE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "filename": filename,
                "file_info": {
                    "size": os.path.getsize(file_path),
                    "type": file_extension,
                    "processed_at": datetime.now().isoformat()
                },
                "content": content[:5000],  # First 5000 characters
                "analysis": analysis
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def extract_text_content(self, file_path: str) -> str:
        """Extract content from text file"""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    
    def extract_json_content(self, file_path: str) -> str:
        """Extract content from JSON file"""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return json.dumps(data, indent=2)
    
    def extract_pdf_content(self, file_path: str) -> str:
        """Extract content from PDF file (basic implementation)"""
        # For now, return a placeholder - in production, use PyPDF2 or similar
        return "PDF content extraction requires additional libraries. Please convert to text file for analysis."
    
    def analyze_file_content(self, content: str) -> dict:
        """Analyze file content for potential legal issues"""
        content_lower = content.lower()
        potential_issues = []
        
        # Financial fraud detection
        if any(keyword in content_lower for keyword in ["fraud", "money", "transaction", "bank", "payment", "scam"]):
            potential_issues.append({
                "type": "financial_fraud",
                "confidence": 0.8,
                "description": "Potential financial fraud or monetary loss detected"
            })
        
        # Harassment detection
        if any(keyword in content_lower for keyword in ["harassment", "threat", "abuse", "bullying", "stalking"]):
            potential_issues.append({
                "type": "online_harassment", 
                "confidence": 0.7,
                "description": "Potential online harassment or threatening behavior detected"
            })
        
        # Privacy violation detection
        if any(keyword in content_lower for keyword in ["privacy", "personal", "photo", "video", "private"]):
            potential_issues.append({
                "type": "privacy_violation",
                "confidence": 0.6,
                "description": "Potential privacy violation or personal data misuse detected"
            })
        
        # Identity theft detection
        if any(keyword in content_lower for keyword in ["identity", "fake", "impersonation", "stolen"]):
            potential_issues.append({
                "type": "identity_theft",
                "confidence": 0.7,
                "description": "Potential identity theft or impersonation detected"
            })
        
        return {
            "potential_issues": potential_issues,
            "risk_level": "HIGH" if len(potential_issues) >= 2 else "MEDIUM" if potential_issues else "LOW",
            "analysis_timestamp": datetime.now().isoformat()
        }
    
    def get_file_analysis_summary(self, file_result: dict) -> str:
        """Generate file analysis summary"""
        if not file_result.get("success"):
            return "❌ **FILE ANALYSIS FAILED**"
        
        analysis = file_result.get("analysis", {})
        issues = analysis.get("potential_issues", [])
        risk_level = analysis.get("risk_level", "LOW")
        
        summary = f"""
**📄 FILE ANALYSIS SUMMARY**

**File:** {file_result['filename']}
**Risk Level:** {risk_level}
**Issues Detected:** {len(issues)}

**Potential Legal Issues:**
"""
        
        if issues:
            for issue in issues:
                summary += f"• **{issue['type'].replace('_', ' ').title()}** (Confidence: {issue['confidence']:.1%})\n"
                summary += f"  {issue['description']}\n"
        else:
            summary += "• No specific legal issues detected in the content\n"
        
        return summary
    
    # ===========================================
    # CORE RESPONSE GENERATION
    # ===========================================
    
    def generate_response(self, user_query: str, search_results: Dict[str, List[Dict[str, Any]]], original_language: str = "English", user_input: str = "") -> str:
        """Generate comprehensive response with color-coded legal guidance"""
        try:
            total_results = (len(search_results.get('cyberlaw', [])) + 
                           len(search_results.get('faq', [])) + 
                           len(search_results.get('nodal_officers', [])))
            
            if total_results == 0:
                return self.generate_no_results_response(user_query, original_language)
            
            # Prepare context with color coding
            context_parts = []
            
            # Add color-coded legal sections
            if search_results.get('cyberlaw'):
                context_parts.append("=== RELEVANT CYBER LAW SECTIONS ===")
                for result in search_results['cyberlaw']:
                    colored_section = self.format_colored_section(
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
            
            # Add contact information
            if search_results.get('nodal_officers'):
                context_parts.append("=== RELEVANT CONTACT INFORMATION ===")
                for result in search_results['nodal_officers']:
                    context_parts.append(f"State: {result['state']}")
                    context_parts.append(f"Officer: {result['officer_name']} ({result['rank']})")
                    context_parts.append(f"Email: {result['email']}")
                    if result['contact']:
                        context_parts.append(f"Contact: {result['contact']}")
                    context_parts.append("")
            
            context = "\n".join(context_parts)
            
            # Generate response using structured format
            enhanced_prompt = f"""
You are a cyber law expert providing guidance in {original_language if original_language != 'English' else 'English'}.

CONTEXT INFORMATION:
{context}

USER QUESTION: {user_query}

Respond using this EXACT format in {original_language if original_language != 'English' else 'English'}:

**SITUATION:** (Acknowledge and summarize their situation in 1-2 lines)

**KEY POINTS:**
• (Most important point about their issue)
• (Second key point or legal provision)  
• (Third key point or action they should take)

**RELEVANT ACTS/SECTIONS:**
• **Support:** (List 1-2 acts/sections that support their case, with color emojis 🔴🟡🟢)
• **Against:** (List any limitations/opposing sections, or "None found" if not applicable)

**NEED MORE HELP?**
• (Relevant follow-up question 1?)
• (Relevant follow-up question 2?)
• (Relevant follow-up question 3?)

Rules:
- Use color emojis (🔴🟡🟢) before each act/section in Support/Against 
- Keep each point concise but informative
- Make questions specific to their situation
- Be empathetic and helpful
- Use simple, clear language
"""
            
            response = self.model.generate_content(enhanced_prompt)
            if response and response.text:
                return response.text.strip()
            else:
                return self.generate_fallback_response(user_query, original_language)
                
        except Exception as e:
            print(f"Response generation error: {e}")
            return self.generate_fallback_response(user_query, original_language)
    
    def generate_no_results_response(self, user_query: str, original_language: str) -> str:
        """Generate response when no search results found"""
        no_result_prompt = f"""
Respond in {original_language if original_language != 'English' else 'English'} using this EXACT format:

**SITUATION:** (Acknowledge you don't have specific information about their question but want to help)

**KEY POINTS:**
• I can help with cyber crime definitions and laws
• I can guide you on how to register FIR for cyber crimes  
• I can find nodal officer contacts for your state

**RELEVANT ACTS/SECTIONS:**
• **Support:** None found in context
• **Against:** None found in context

**NEED MORE HELP?**
• Would you like to know about cyber crime types?
• Can I help you understand how to report a cyber crime?
• Do you need contact information for your state's cyber cell?

USER QUESTION: {user_query}

Keep it friendly and conversational.
"""
        
        try:
            response = self.model.generate_content(no_result_prompt)
            if response and response.text:
                return response.text.strip()
        except:
            pass
        
        return """I don't have specific information about that in my knowledge base, but I'd love to help you with cyber law topics!

I'm great at helping with:
• Cyber crime definitions and laws
• How to register FIR for cyber crimes  
• Finding nodal officer contacts for your state
• Understanding IT Act, IPC, and BNS sections

What would you like to know about? Can I help you understand what cyber terrorism is, or do you need to report a cyber crime?"""
    
    def generate_fallback_response(self, user_query: str, original_language: str) -> str:
        """Generate fallback response on error"""
        return f"I apologize, but I encountered an error while processing your question about '{user_query}'. Please try asking again, or let me know if you'd like help with filing a complaint or understanding cyber laws."
    
    # ===========================================
    # INTENT DETECTION AND ROUTING
    # ===========================================
    
    def detect_intent(self, user_input: str) -> str:
        """Detect user intent from input"""
        user_input_lower = user_input.lower()
        
        # Complaint-related keywords
        complaint_keywords = ["complaint", "report", "file", "fir", "police", "crime happened", "victim", "fraud", "hacked", "scammed"]
        if any(keyword in user_input_lower for keyword in complaint_keywords):
            return "complaint"
        
        return "general_query"
    
    def add_to_conversation_history(self, user_input: str, english_query: str, response: str, detected_language: str):
        """Add conversation turn to history"""
        turn = {
            "user_input": user_input,
            "english_query": english_query,
            "response": response,
            "detected_language": detected_language,
            "timestamp": datetime.now().isoformat()
        }
        
        self.conversation_history.append(turn)
        
        # Keep only last N turns
        if len(self.conversation_history) > self.max_history_turns:
            self.conversation_history = self.conversation_history[-self.max_history_turns:]
    
    def process_query(self, user_input: str) -> str:
        """Main query processing pipeline"""
        try:
            print(f"User query: {user_input}")
            
            # Handle file analysis commands
            if user_input.startswith("/analyze"):
                return self.handle_file_command(user_input)
            
            # Handle ongoing complaint collection
            if self.session_state == "complaint_collection":
                return self.handle_complaint_continuation(user_input)
            
            # Detect intent for new conversations
            intent = self.detect_intent(user_input)
            print(f"Detected intent: {intent}")
            
            # Handle complaint initiation
            if intent == "complaint":
                return self.handle_complaint_initiation(user_input)
            
            # Regular query processing
            print("Detecting language and translating...")
            translation_result = self.detect_language_and_translate(user_input)
            original_language = translation_result["original_language"]
            english_query = translation_result["translated_text"]
            print(f"Original language: {original_language}")
            print(f"Translated query: {english_query}")
            
            # Search knowledge base
            print("Searching knowledge base...")
            search_results = self.comprehensive_search(english_query)
            
            cyberlaw_count = len(search_results.get('cyberlaw', []))
            faq_count = len(search_results.get('faq', []))
            officer_count = len(search_results.get('nodal_officers', []))
            print(f"Found: {cyberlaw_count} law sections, {faq_count} FAQs, {officer_count} officers")
            
            # Generate response
            print("Generating response...")
            response = self.generate_response(english_query, search_results, original_language, user_input)
            
            # Add to conversation history
            self.add_to_conversation_history(user_input, english_query, response, original_language)
            
            return response
            
        except Exception as e:
            print(f"Error processing query: {e}")
            return "I apologize, but I encountered an error while processing your question. Please try again."
    
    # ===========================================
    # COMPLAINT HANDLING METHODS
    # ===========================================
    
    def handle_complaint_initiation(self, user_input: str) -> str:
        """Handle complaint collection initiation"""
        try:
            result = self.start_complaint_collection(user_input)
            self.active_complaint_id = result["complaint_id"]
            self.session_state = "complaint_collection"
            return result["message"]
        except Exception as e:
            print(f"Error starting complaint: {e}")
            return "I understand you want to file a complaint. Let me help you collect the necessary information. What type of cyber crime occurred?"
    
    def handle_complaint_continuation(self, user_input: str) -> str:
        """Handle ongoing complaint collection"""
        try:
            state = self.load_complaint_state(self.active_complaint_id)
            if not state:
                self.session_state = "general"
                self.active_complaint_id = None
                return "Sorry, I couldn't find your complaint session. Let's start over. What would you like help with?"
            
            # Handle confirmation stage
            if state["collected_data"].get("confirmation_pending"):
                result = self.handle_complaint_confirmation(self.active_complaint_id, user_input)
            else:
                result = self.process_complaint_answer(self.active_complaint_id, user_input)
            
            if result.get("status") in ["completed", "cancelled"]:
                self.session_state = "general"
                self.active_complaint_id = None
            
            return result["message"]
            
        except Exception as e:
            print(f"Error processing complaint: {e}")
            self.session_state = "general"
            self.active_complaint_id = None
            return "There was an error processing your complaint. Let's start over. What would you like help with?"
    
    def handle_file_command(self, user_input: str) -> str:
        """Handle file analysis commands"""
        try:
            parts = user_input.split(" ", 1)
            if len(parts) < 2:
                return "**📄 FILE ANALYSIS**\n\nPlease provide a file path: `/analyze path/to/your/file.pdf`\n\nSupported formats: `.txt`, `.pdf`, `.json`"
            
            file_path = parts[1].strip()
            
            if not os.path.exists(file_path):
                return f"❌ **File not found**: `{file_path}`\n\nPlease check the file path and try again."
            
            # Process the file
            filename = os.path.basename(file_path)
            result = self.process_uploaded_file(file_path, filename)
            
            if not result.get("success"):
                return f"❌ **File Processing Failed**: {result.get('error', 'Unknown error')}"
            
            # Get analysis summary
            summary = self.get_file_analysis_summary(result)
            
            # Generate legal advice based on detected issues
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
            search_results = self.comprehensive_search(search_query)
            
            # Generate response with context
            if search_results.get("cyberlaw") or search_results.get("faq"):
                return self.generate_response(search_query, search_results, "English", user_query)
            else:
                return "**💡 LEGAL GUIDANCE**: Consider consulting with a cyber law expert and filing a complaint with your local cyber crime cell."
                
        except Exception as e:
            print(f"Error generating legal advice: {e}")
            return "**💡 LEGAL GUIDANCE**: Please describe the specific issues you'd like help with."
    
    # ===========================================
    # CHAT INTERFACE
    # ===========================================
    
    def chat_loop(self):
        """Interactive chat loop"""
        print("=" * 70)
        print("🤖 MASTER CYBER LAW CHATBOT - ALL-IN-ONE SYSTEM")
        print("💬 Ask questions about cyber laws, FIR registration, cyber crimes, etc.")
        print("📋 Type 'report' or 'complaint' to file a cyber crime complaint")
        print("📄 Type '/analyze filename.pdf' to analyze documents") 
        print("🏠 Type '/police [location]' to find nearby police stations")
        print("❌ Type 'quit' or 'exit' to end the conversation")
        print("=" * 70)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("\nThank you for using the Cyber Law Chatbot. Stay safe online! 🛡️")
                    break
                
                if not user_input:
                    continue
                
                # Special command for police station lookup
                if user_input.startswith("/police"):
                    location = user_input.replace("/police", "").strip()
                    if location:
                        stations = self.find_nearby_police_stations(location)
                        print("\n🚔 **NEARBY POLICE STATIONS:**")
                        for i, station in enumerate(stations, 1):
                            print(f"\n**{i}. {station['station_name']}**")
                            print(f"   📍 {station['address']}")
                            print(f"   📞 {station['phone']}")
                            print(f"   📧 {station['email']}")
                            print(f"   👮 {station['in_charge']}")
                        continue
                    else:
                        print("\nPlease provide a location: /police Delhi")
                        continue
                
                # Process the query
                response = self.process_query(user_input)
                print(f"\n🤖 Bot: {response}")
                
            except KeyboardInterrupt:
                print("\nThank you for using the Cyber Law Chatbot. Stay safe online! 🛡️")
                break
            except Exception as e:
                print(f"\nSorry, I encountered an error: {e}")
                print("Please try again.")

def main():
    """Main function to run the chatbot"""
    try:
        chatbot = MasterCyberLawChatbot()
        chatbot.chat_loop()
    except Exception as e:
        print(f"Failed to initialize chatbot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()