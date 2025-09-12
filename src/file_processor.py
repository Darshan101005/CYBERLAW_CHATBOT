"""
File Processing System for Text and PDF Analysis
Handles uploaded files and extracts content for legal analysis
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

# Note: For PDF processing in production, you'd install PyPDF2 or pdfplumber
# For this implementation, we'll simulate PDF processing with placeholder

class FileProcessor:
    def __init__(self):
        self.upload_dir = "CYBERLAW_CHATBOT/uploads"
        self.processed_dir = "CYBERLAW_CHATBOT/processed_files"
        self.supported_formats = ['.txt', '.pdf', '.json']
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit
        
        self.ensure_directories()
    
    def ensure_directories(self):
        """Create necessary directories"""
        for directory in [self.upload_dir, self.processed_dir]:
            if not os.path.exists(directory):
                os.makedirs(directory)
    
    def is_supported_file(self, filename: str) -> bool:
        """Check if file format is supported"""
        file_extension = os.path.splitext(filename.lower())[1]
        return file_extension in self.supported_formats
    
    def process_uploaded_file(self, file_path: str, original_filename: str) -> Dict[str, Any]:
        """
        Process uploaded file and extract content for analysis
        """
        if not os.path.exists(file_path):
            return {"error": "File not found", "success": False}
        
        file_size = os.path.getsize(file_path)
        if file_size > self.max_file_size:
            return {"error": "File too large (max 10MB)", "success": False}
        
        file_extension = os.path.splitext(original_filename.lower())[1]
        
        try:
            if file_extension == '.txt':
                content = self.process_text_file(file_path)
            elif file_extension == '.pdf':
                content = self.process_pdf_file(file_path)
            elif file_extension == '.json':
                content = self.process_json_file(file_path)
            else:
                return {"error": "Unsupported file format", "success": False}
            
            # Save processed content
            processed_info = self.save_processed_content(content, original_filename)
            
            return {
                "success": True,
                "filename": original_filename,
                "content": content,
                "processed_id": processed_info["processed_id"],
                "analysis": self.analyze_content_for_legal_issues(content),
                "file_info": {
                    "size": file_size,
                    "type": file_extension,
                    "processed_at": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {"error": f"Failed to process file: {str(e)}", "success": False}
    
    def process_text_file(self, file_path: str) -> str:
        """Process text file and extract content"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # Clean and validate content
        if len(content) > 50000:  # Limit to 50k characters
            content = content[:50000] + "\\n[Content truncated due to length]"
        
        return content.strip()
    
    def process_pdf_file(self, file_path: str) -> str:
        """
        Process PDF file and extract text content
        Note: In production, you'd use PyPDF2, pdfplumber, or similar library
        """
        # Placeholder implementation - in real scenario, use PDF processing library
        try:
            # This is a simulation - replace with actual PDF processing
            with open(file_path, 'rb') as f:
                # Read first few bytes to confirm it's a PDF
                header = f.read(5)
                if header != b'%PDF-':
                    raise ValueError("Not a valid PDF file")
            
            # Simulated PDF text extraction
            return f"""
[PDF FILE PROCESSED]
Filename: {os.path.basename(file_path)}
Note: PDF processing is simulated. In production, this would extract actual text content.

To enable full PDF processing, install: pip install PyPDF2 pdfplumber

For now, please describe the content of your PDF file, and I'll help analyze it for legal issues.
"""
        except Exception as e:
            return f"Error processing PDF: {str(e)}"
    
    def process_json_file(self, file_path: str) -> str:
        """Process JSON file and extract structured content"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert JSON to readable text format
        if isinstance(data, dict):
            content_parts = []
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    content_parts.append(f"{key}: {json.dumps(value, indent=2)}")
                else:
                    content_parts.append(f"{key}: {value}")
            return "\\n".join(content_parts)
        else:
            return json.dumps(data, indent=2)
    
    def analyze_content_for_legal_issues(self, content: str) -> Dict[str, Any]:
        """
        Analyze file content for potential legal issues
        """
        content_lower = content.lower()
        
        # Define keywords for different types of cyber crimes
        analysis_keywords = {
            "financial_fraud": ["fraud", "money", "payment", "bank", "credit card", "upi", "transaction", "scam"],
            "harassment": ["harassment", "threat", "abuse", "stalking", "bullying", "intimidation"],
            "privacy_violation": ["privacy", "personal data", "photos", "private", "confidential", "leak"],
            "identity_theft": ["identity", "impersonation", "fake profile", "stolen", "misuse"],
            "technical_attack": ["hack", "virus", "malware", "phishing", "breach", "unauthorized access"],
            "defamation": ["defame", "reputation", "false", "rumor", "character assassination"]
        }
        
        detected_issues = []
        for issue_type, keywords in analysis_keywords.items():
            keyword_matches = [kw for kw in keywords if kw in content_lower]
            if keyword_matches:
                detected_issues.append({
                    "type": issue_type,
                    "matched_keywords": keyword_matches,
                    "confidence": len(keyword_matches) / len(keywords)
                })
        
        # Sort by confidence
        detected_issues.sort(key=lambda x: x["confidence"], reverse=True)
        
        return {
            "potential_issues": detected_issues,
            "content_length": len(content),
            "analysis_timestamp": datetime.now().isoformat(),
            "recommended_actions": self.get_recommended_actions(detected_issues)
        }
    
    def get_recommended_actions(self, detected_issues: List[Dict]) -> List[str]:
        """Get recommended actions based on detected legal issues"""
        if not detected_issues:
            return ["No specific legal issues detected. General consultation recommended."]
        
        recommendations = []
        for issue in detected_issues[:3]:  # Top 3 issues
            issue_type = issue["type"]
            
            if issue_type == "financial_fraud":
                recommendations.append("🏦 Contact your bank immediately and file a complaint with cyber crime cell")
            elif issue_type == "harassment":
                recommendations.append("👮 File FIR at local police station under relevant IPC/BNS sections")
            elif issue_type == "privacy_violation":
                recommendations.append("🛡️ Report privacy violation to platform and consider legal action under IT Act")
            elif issue_type == "identity_theft":
                recommendations.append("🆔 Report identity theft to authorities and secure your accounts")
            elif issue_type == "technical_attack":
                recommendations.append("💻 Report cyber attack to CERT-In and local cyber crime cell")
            elif issue_type == "defamation":
                recommendations.append("⚖️ Consider legal action under defamation laws (IPC 499-502)")
        
        return recommendations
    
    def save_processed_content(self, content: str, original_filename: str) -> Dict[str, str]:
        """Save processed file content"""
        processed_id = f"PROC_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(original_filename) % 10000}"
        
        processed_info = {
            "processed_id": processed_id,
            "original_filename": original_filename,
            "processed_at": datetime.now().isoformat(),
            "content": content
        }
        
        file_path = os.path.join(self.processed_dir, f"{processed_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(processed_info, f, indent=2, ensure_ascii=False)
        
        return processed_info
    
    def get_file_analysis_summary(self, processed_result: Dict[str, Any]) -> str:
        """Generate a user-friendly summary of file analysis"""
        if not processed_result.get("success"):
            return f"❌ **File Processing Failed**: {processed_result.get('error', 'Unknown error')}"
        
        analysis = processed_result.get("analysis", {})
        potential_issues = analysis.get("potential_issues", [])
        
        summary = f"""
📄 **FILE ANALYSIS COMPLETE**

**File:** {processed_result.get('filename')}
**Size:** {processed_result.get('file_info', {}).get('size', 0)} bytes
**Processed ID:** {processed_result.get('processed_id')}

"""
        
        if potential_issues:
            summary += "**🚨 POTENTIAL LEGAL ISSUES DETECTED:**\\n"
            for issue in potential_issues[:3]:
                confidence_pct = int(issue['confidence'] * 100)
                issue_name = issue['type'].replace('_', ' ').title()
                summary += f"• **{issue_name}** (Confidence: {confidence_pct}%)\\n"
                summary += f"  Keywords found: {', '.join(issue['matched_keywords'])}\\n"
        else:
            summary += "✅ **No specific legal issues detected in the content.**\\n"
        
        recommendations = analysis.get("recommended_actions", [])
        if recommendations:
            summary += "\\n**📋 RECOMMENDED ACTIONS:**\\n"
            for rec in recommendations:
                summary += f"• {rec}\\n"
        
        return summary