"""
Act Categorization System for Color-coded Legal References
Categories:
- CRITICAL (Red): Serious crimes with severe punishment (imprisonment > 3 years)
- GENERAL (Yellow): Standard offenses with moderate punishment (imprisonment 1-3 years)
- PROCEDURAL (Green): Definitions, procedures, technical sections
"""

class ActCategorizer:
    def __init__(self):
        # Define categorization rules based on section content and punishment severity
        self.categories = {
            "CRITICAL": {
                "color": "🔴",  # Red
                "html_color": "#FF4444",
                "description": "Serious cyber crimes with severe penalties"
            },
            "GENERAL": {
                "color": "🟡",  # Yellow
                "html_color": "#FFD700", 
                "description": "Standard cyber offenses"
            },
            "PROCEDURAL": {
                "color": "🟢",  # Green
                "html_color": "#32CD32",
                "description": "Definitions and procedures"
            }
        }
        
        # Critical sections (severe punishment, serious crimes)
        self.critical_sections = {
            # BNS sections
            "77": "Voyeurism - serious privacy violation",
            "78": "Stalking - harassment with severe impact",
            
            # IPC sections  
            "503": "Criminal intimidation - serious threat",
            "506": "Punishment for criminal intimidation",
            "507": "Anonymous criminal intimidation",
            "292": "Obscene material distribution",
            
            # IT Act critical sections (will add after full analysis)
        }
        
        # General offense sections
        self.general_sections = {
            # IPC sections
            "500": "Defamation - reputation damage",
            
            # BNS and IT Act general sections
        }
        
        # Procedural sections (definitions, technical)
        self.procedural_sections = {
            # IT Act procedural
            "1": "Title and application of IT Act",
            "2": "Definitions of technical terms",
        }
    
    def categorize_section(self, section_number: str, law_type: str = None, content: str = None) -> dict:
        """
        Categorize a legal section based on its number, type, and content
        Returns category info with color coding
        """
        section_key = section_number.strip()
        
        # Check critical sections first
        if section_key in self.critical_sections:
            return {
                "category": "CRITICAL",
                "color": self.categories["CRITICAL"]["color"],
                "html_color": self.categories["CRITICAL"]["html_color"],
                "description": self.critical_sections[section_key]
            }
        
        # Check general sections
        elif section_key in self.general_sections:
            return {
                "category": "GENERAL", 
                "color": self.categories["GENERAL"]["color"],
                "html_color": self.categories["GENERAL"]["html_color"],
                "description": self.general_sections[section_key]
            }
        
        # Check procedural sections
        elif section_key in self.procedural_sections:
            return {
                "category": "PROCEDURAL",
                "color": self.categories["PROCEDURAL"]["color"], 
                "html_color": self.categories["PROCEDURAL"]["html_color"],
                "description": self.procedural_sections[section_key]
            }
        
        # Smart categorization based on content analysis
        else:
            return self._smart_categorize(section_number, law_type, content)
    
    def _smart_categorize(self, section_number: str, law_type: str = None, content: str = None) -> dict:
        """
        Smart categorization based on content analysis when section not in predefined lists
        """
        if not content:
            # Default to GENERAL if no content available
            return {
                "category": "GENERAL",
                "color": self.categories["GENERAL"]["color"],
                "html_color": self.categories["GENERAL"]["html_color"], 
                "description": f"Section {section_number} - Standard offense"
            }
        
        content_lower = content.lower()
        
        # Critical indicators
        critical_keywords = [
            "imprisonment for life", "death", "seven years", "ten years",
            "terrorism", "national security", "child", "minor", "rape",
            "murder", "grievous hurt", "cheating", "fraud", "money laundering"
        ]
        
        # Procedural indicators  
        procedural_keywords = [
            "definition", "means", "includes", "interpretation", "application",
            "procedure", "notification", "rules", "regulation", "authority"
        ]
        
        if any(keyword in content_lower for keyword in critical_keywords):
            return {
                "category": "CRITICAL",
                "color": self.categories["CRITICAL"]["color"],
                "html_color": self.categories["CRITICAL"]["html_color"],
                "description": f"Section {section_number} - Serious offense detected"
            }
        
        elif any(keyword in content_lower for keyword in procedural_keywords):
            return {
                "category": "PROCEDURAL", 
                "color": self.categories["PROCEDURAL"]["color"],
                "html_color": self.categories["PROCEDURAL"]["html_color"],
                "description": f"Section {section_number} - Procedural/Definition"
            }
        
        else:
            return {
                "category": "GENERAL",
                "color": self.categories["GENERAL"]["color"], 
                "html_color": self.categories["GENERAL"]["html_color"],
                "description": f"Section {section_number} - Standard offense"
            }
    
    def format_colored_section(self, section_number: str, title: str, law_type: str, content: str = None) -> str:
        """
        Format a section with appropriate color coding for display
        """
        category_info = self.categorize_section(section_number, law_type, content)
        
        return f"{category_info['color']} **{law_type} Section {section_number}** - {title} ({category_info['category']})"