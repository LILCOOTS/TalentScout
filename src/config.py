"""
Configuration module for TalentScout Hiring Assistant.
Handles environment variables, API keys, and application settings.
"""

import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class Config:
    """Configuration class for the hiring assistant application."""
    
    # API Configuration
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    model_name: str = os.getenv("MODEL_NAME", "gemini-pro")
    max_tokens: int = int(os.getenv("MAX_TOKENS", "1000"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Application Configuration
    app_name: str = "TalentScout Hiring Assistant"
    company_name: str = "TalentScout"
    max_conversation_length: int = 50
    
    # Data Storage
    data_storage_path: str = os.getenv("DATA_STORAGE_PATH", "data/candidates.json")
    
    # Conversation stages
    conversation_stages: List[str] = None
    
    # Exit keywords
    exit_keywords: List[str] = None
    
    # Required candidate fields
    required_fields: List[str] = None
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        if self.conversation_stages is None:
            self.conversation_stages = [
                "greeting",
                "info_gathering", 
                "tech_questions",
                "completed"
            ]
        
        if self.exit_keywords is None:
            self.exit_keywords = [
                "bye", "goodbye", "exit", "quit", "end", "stop",
                "thanks", "thank you", "done", "finish"
            ]
        
        if self.required_fields is None:
            self.required_fields = [
                "full_name",
                "email",
                "phone",
                "experience_years",
                "desired_position",
                "location",
                "tech_stack"
            ]
    
    def validate_config(self) -> bool:
        """Validate the configuration settings."""
        if not self.gemini_api_key:
            return False
        
        if self.max_tokens <= 0:
            return False
            
        if not (0.0 <= self.temperature <= 2.0):
            return False
            
        return True
    
    def get_prompts(self) -> Dict[str, str]:
        """Get the system prompts for different conversation stages."""
        return {
            "system_prompt": f"""
You are an intelligent hiring assistant for {self.company_name}, a technology recruitment agency.
Your role is to conduct initial candidate screening by gathering essential information and 
generating relevant technical questions based on their declared tech stack.

Key responsibilities:
1. Greet candidates warmly and explain your purpose
2. Collect essential candidate information systematically
3. Generate 3-5 technical questions tailored to their tech stack
4. Maintain context and ensure coherent conversation flow
5. Handle unexpected inputs gracefully with fallback responses
6. End conversations gracefully when exit keywords are detected

Required information to collect:
- Full Name
- Email Address  
- Phone Number
- Years of Experience
- Desired Position(s)
- Current Location
- Tech Stack (programming languages, frameworks, databases, tools)

Guidelines:
- Be professional yet friendly
- Ask one question at a time for better user experience
- Validate information format (email, phone) when possible
- Generate technical questions appropriate to experience level
- Don't deviate from recruitment purpose
- Respect data privacy and handle information securely
- Provide meaningful responses for unclear inputs
""",
            
            "greeting_prompt": f"""
Generate a warm, professional greeting for a candidate starting their interview with {self.company_name}.
Explain that you're an AI assistant that will help with initial screening by collecting their information
and asking relevant technical questions. Keep it concise and encouraging.
""",
            
            "info_gathering_prompt": """
You are collecting candidate information. Ask for the next required field that hasn't been provided yet.
Be specific about what format you expect (e.g., for phone numbers, years of experience).
Only ask for one piece of information at a time to avoid overwhelming the candidate.
""",
            
            "tech_questions_prompt": """
Based on the candidate's declared tech stack and desired position, generate 3-5 highly relevant technical questions.

Instructions:
- Tailor questions specifically to their DESIRED POSITION (e.g., Frontend Developer, Backend Engineer, Full Stack Developer, Data Scientist, etc.)
- Match the difficulty to their experience level (junior: 0-2 years, mid: 3-5 years, senior: 6+ years)
- Focus on technologies they specifically mentioned in their tech stack
- Include role-specific questions (e.g., for Frontend: React/Vue patterns, for Backend: API design, for Data Science: ML algorithms)
- Ask practical scenario-based questions rather than just definitions
- Ensure questions test real-world application knowledge

Question types to include:
- Core technology knowledge (specific to their stack)
- Best practices and design patterns
- Problem-solving scenarios relevant to their desired role
- Architecture and system design (for senior roles)
- Debugging and troubleshooting approaches

Return exactly 3-5 questions, numbered 1-5, with no additional formatting or text.
""",
            
            "fallback_prompt": """
The user provided input that doesn't clearly answer the current question or seems off-topic.
Provide a helpful response that:
- Acknowledges their input politely
- Redirects them back to the current question/stage
- Offers clarification if they seem confused
- Maintains the professional tone
""",
            
            "completion_prompt": f"""
Generate a professional closing message for the candidate.
Thank them for their time, summarize what was accomplished, and explain the next steps.
Mention that their information has been recorded and someone from {self.company_name} will follow up.
"""
        }
