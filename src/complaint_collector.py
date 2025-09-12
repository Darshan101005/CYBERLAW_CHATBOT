"""
Interactive Complaint Collection System
Collects detailed complaint information and stores in JSON format
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any

class ComplaintCollector:
    def __init__(self):
        self.complaint_dir = "CYBERLAW_CHATBOT/complaints"
        self.ensure_complaint_directory()
        
        # Essential complaint fields to collect
        self.complaint_fields = {
            "personal_info": [
                {"field": "full_name", "question": "What is your full name?", "required": True},
                {"field": "phone", "question": "Please provide your phone number for contact:", "required": True},
                {"field": "email", "question": "Your email address:", "required": True},
                {"field": "address", "question": "Your complete address:", "required": True},
                {"field": "age", "question": "Your age:", "required": False},
                {"field": "occupation", "question": "Your occupation:", "required": False}
            ],
            "incident_details": [
                {"field": "incident_type", "question": "What type of cyber crime occurred? (e.g., fraud, hacking, cyberbullying, identity theft)", "required": True},
                {"field": "incident_date", "question": "When did this incident occur? (date and time if possible)", "required": True},
                {"field": "incident_description", "question": "Please describe the incident in detail:", "required": True},
                {"field": "financial_loss", "question": "Did you suffer any financial loss? If yes, how much?", "required": False},
                {"field": "evidence_available", "question": "Do you have any evidence? (screenshots, emails, messages, etc.)", "required": False},
                {"field": "suspect_info", "question": "Do you have any information about the suspect? (name, phone, email, social media profiles)", "required": False}
            ],
            "technical_details": [
                {"field": "platform_used", "question": "Which platform/website/app was involved?", "required": False},
                {"field": "device_info", "question": "What device were you using? (mobile, laptop, etc.)", "required": False},
                {"field": "transaction_id", "question": "Any transaction ID or reference number?", "required": False},
                {"field": "bank_details", "question": "If financial, which bank/payment method was involved?", "required": False}
            ],
            "previous_action": [
                {"field": "reported_before", "question": "Have you reported this anywhere else? (police station, bank, platform)", "required": False},
                {"field": "fir_number", "question": "Do you have an existing FIR number?", "required": False},
                {"field": "other_complaints", "question": "Have you filed complaints with other authorities?", "required": False}
            ]
        }
    
    def ensure_complaint_directory(self):
        """Create complaints directory if it doesn't exist"""
        if not os.path.exists(self.complaint_dir):
            os.makedirs(self.complaint_dir)
    
    def start_complaint_collection(self, user_input: str) -> dict:
        """
        Start interactive complaint collection process
        Returns the collection state and next question
        """
        complaint_id = self.generate_complaint_id()
        
        initial_state = {
            "complaint_id": complaint_id,
            "status": "collecting",
            "current_section": "personal_info",
            "current_field_index": 0,
            "collected_data": {
                "initial_complaint": user_input,
                "timestamp": datetime.now().isoformat(),
                "personal_info": {},
                "incident_details": {},
                "technical_details": {},
                "previous_action": {},
                "files_uploaded": []
            },
            "completion_percentage": 0
        }
        
        # Save initial state
        self.save_complaint_state(initial_state)
        
        # Return first question
        first_question = self.get_next_question(initial_state)
        
        return {
            "complaint_id": complaint_id,
            "message": f"""
**🚨 COMPLAINT COLLECTION STARTED**

I understand you want to report a cyber crime. I'll help you collect all the necessary information that authorities will need to take action.

**Complaint ID:** {complaint_id}

Let's start with some basic information:

{first_question["question"]}

*Note: This information will be stored securely and can be forwarded to the appropriate authorities.*
""",
            "next_question": first_question,
            "progress": "1/15 questions"
        }
    
    def process_answer(self, complaint_id: str, answer: str) -> dict:
        """
        Process user's answer and return next question or completion
        """
        # Load complaint state
        state = self.load_complaint_state(complaint_id)
        if not state:
            return {"error": "Complaint ID not found"}
        
        # Save current answer
        current_question = self.get_current_question(state)
        if current_question:
            section = state["current_section"]
            field = current_question["field"]
            state["collected_data"][section][field] = answer.strip()
        
        # Move to next question
        state = self.advance_to_next_question(state)
        
        # Update completion percentage
        state["completion_percentage"] = self.calculate_completion(state)
        
        # Save updated state
        self.save_complaint_state(state)
        
        # Check if collection is complete
        if state["status"] == "completed":
            return self.finalize_complaint(state)
        
        # Get next question
        next_question = self.get_next_question(state)
        
        return {
            "complaint_id": complaint_id,
            "message": f"✅ Answer recorded.\n\n{next_question['question']}",
            "next_question": next_question,
            "progress": f"{self.get_question_number(state)}/15 questions",
            "completion": f"{state['completion_percentage']}% complete"
        }
    
    def get_current_question(self, state: dict) -> dict:
        """Get current question based on state"""
        section = state["current_section"]
        field_index = state["current_field_index"]
        
        if section in self.complaint_fields and field_index < len(self.complaint_fields[section]):
            return self.complaint_fields[section][field_index]
        
        return None
    
    def get_next_question(self, state: dict) -> dict:
        """Get the next question to ask"""
        current_question = self.get_current_question(state)
        
        if current_question:
            required_indicator = "* (Required)" if current_question["required"] else "(Optional)"
            return {
                "question": f"**{current_question['question']}** {required_indicator}",
                "field": current_question["field"],
                "required": current_question["required"]
            }
        
        return {"question": "Collection complete!", "field": None, "required": False}
    
    def advance_to_next_question(self, state: dict) -> dict:
        """Move to the next question in sequence"""
        state["current_field_index"] += 1
        
        # Check if current section is complete
        current_section = state["current_section"]
        if state["current_field_index"] >= len(self.complaint_fields[current_section]):
            # Move to next section
            sections = list(self.complaint_fields.keys())
            current_section_index = sections.index(current_section)
            
            if current_section_index + 1 < len(sections):
                state["current_section"] = sections[current_section_index + 1]
                state["current_field_index"] = 0
            else:
                # All sections complete
                state["status"] = "completed"
        
        return state
    
    def calculate_completion(self, state: dict) -> int:
        """Calculate completion percentage"""
        total_questions = sum(len(fields) for fields in self.complaint_fields.values())
        answered_questions = 0
        
        for section, fields in self.complaint_fields.items():
            for field_info in fields:
                if field_info["field"] in state["collected_data"].get(section, {}):
                    if state["collected_data"][section][field_info["field"]].strip():
                        answered_questions += 1
        
        return int((answered_questions / total_questions) * 100)
    
    def get_question_number(self, state: dict) -> int:
        """Get current question number for progress display"""
        sections = list(self.complaint_fields.keys())
        current_section_index = sections.index(state["current_section"])
        
        question_num = state["current_field_index"] + 1
        for i in range(current_section_index):
            question_num += len(self.complaint_fields[sections[i]])
        
        return question_num
    
    def finalize_complaint(self, state: dict) -> dict:
        """Finalize the complaint and generate summary"""
        complaint_data = state["collected_data"]
        complaint_id = state["complaint_id"]
        
        # Generate final complaint file
        final_complaint = {
            "complaint_id": complaint_id,
            "submission_timestamp": datetime.now().isoformat(),
            "status": "ready_for_submission",
            "complainant": complaint_data["personal_info"],
            "incident": complaint_data["incident_details"],
            "technical_info": complaint_data["technical_details"],
            "previous_actions": complaint_data["previous_action"],
            "initial_complaint_text": complaint_data["initial_complaint"],
            "files_attached": complaint_data["files_uploaded"]
        }
        
        # Save final complaint
        final_path = os.path.join(self.complaint_dir, f"FINAL_{complaint_id}.json")
        with open(final_path, 'w', encoding='utf-8') as f:
            json.dump(final_complaint, f, indent=2, ensure_ascii=False)
        
        # Generate summary
        summary = self.generate_complaint_summary(final_complaint)
        
        return {
            "complaint_id": complaint_id,
            "status": "completed",
            "message": f"""
**✅ COMPLAINT COLLECTION COMPLETED**

**Complaint ID:** {complaint_id}

{summary}

**📁 Your complaint has been saved and is ready for submission to authorities.**

**Next Steps:**
• Your complaint file has been generated: `FINAL_{complaint_id}.json`
• You can now forward this to your local cyber crime police station
• Keep your complaint ID for reference: **{complaint_id}**

**Need help with next steps?**
• Want me to find your local cyber crime cell contact?
• Need help understanding which laws apply to your case?
• Want guidance on filing an FIR?
""",
            "file_path": final_path,
            "summary": summary
        }
    
    def generate_complaint_summary(self, complaint_data: dict) -> str:
        """Generate a readable summary of the complaint"""
        complainant = complaint_data["complainant"]
        incident = complaint_data["incident"]
        
        summary = f"""
**COMPLAINT SUMMARY:**

**Complainant:** {complainant.get('full_name', 'N/A')}
**Contact:** {complainant.get('phone', 'N/A')} | {complainant.get('email', 'N/A')}

**Incident Type:** {incident.get('incident_type', 'N/A')}
**Date of Incident:** {incident.get('incident_date', 'N/A')}
**Financial Loss:** {incident.get('financial_loss', 'None reported')}

**Brief Description:** {incident.get('incident_description', 'N/A')[:200]}...

**Evidence Available:** {incident.get('evidence_available', 'Not specified')}
"""
        return summary
    
    def save_complaint_state(self, state: dict):
        """Save complaint collection state"""
        file_path = os.path.join(self.complaint_dir, f"{state['complaint_id']}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def load_complaint_state(self, complaint_id: str) -> dict:
        """Load complaint collection state"""
        file_path = os.path.join(self.complaint_dir, f"{complaint_id}.json")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
    
    def generate_complaint_id(self) -> str:
        """Generate unique complaint ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"CYBER_{timestamp}"