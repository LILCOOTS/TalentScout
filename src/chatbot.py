"""
Main chatbot module for TalentScout Hiring Assistant.
Handles conversation flow, Gemini AI integration, and candidate interaction.
"""

import google.generativeai as genai
import streamlit as st
from typing import Dict, List, Optional, Tuple, Any
import re
import json
import logging
import traceback
from datetime import datetime
from src.config import Config
from src.data_handler import CandidateProfile, CandidateDataHandler

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('hiring_assistant.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Try to import cloud data handler, fallback to local if not available
try:
    from src.cloud_data_handler import CloudDataHandler
    import os
    # Check if we have cloud storage environment variables
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_KEY = os.getenv('SUPABASE_ANON_KEY') or os.getenv('SUPABASE_KEY')
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    
    # Use cloud storage if we have the required environment variables or if in production
    USE_CLOUD_STORAGE = bool(SUPABASE_URL and SUPABASE_KEY) or ENVIRONMENT == 'production'
    
    logger.info(f"Cloud storage detection: URL={'***' if SUPABASE_URL else 'None'}, KEY={'***' if SUPABASE_KEY else 'None'}, ENV={ENVIRONMENT}")
    logger.info(f"USE_CLOUD_STORAGE: {USE_CLOUD_STORAGE}")
    
except ImportError as e:
    USE_CLOUD_STORAGE = False
    logger.warning(f"Cloud data handler not available: {e}")
    logger.info("Falling back to local storage")

class HiringAssistant:
    """Main chatbot class for handling candidate interactions."""
    
    def __init__(self, config: Config):
        """Initialize the hiring assistant with comprehensive error handling."""
        logger.info("Starting HiringAssistant initialization...")
        
        try:
            self.config = config
            
            # Use cloud data handler if available, otherwise fallback to local
            logger.info(f"Initializing data handler (USE_CLOUD_STORAGE: {USE_CLOUD_STORAGE})")
            
            if USE_CLOUD_STORAGE:
                try:
                    self.data_handler = CloudDataHandler(config.data_storage_path)
                    logger.info("✅ Using cloud data storage (Supabase)")
                except Exception as cloud_error:
                    logger.warning(f"Cloud storage initialization failed: {cloud_error}")
                    logger.info("Falling back to local storage")
                    self.data_handler = CandidateDataHandler(config.data_storage_path)
            else:
                self.data_handler = CandidateDataHandler(config.data_storage_path)
                logger.info("⚠️ Using local file storage (not suitable for deployment)")
            
            self.prompts = config.get_prompts()
            
            logger.info("Initializing HiringAssistant...")
            logger.info(f"Company: {config.company_name}")
            logger.info(f"Model: {config.model_name}")
            logger.info(f"API Key present: {bool(config.gemini_api_key)}")
            
            # Validate configuration
            if not config.validate_config():
                logger.error("Configuration validation failed")
                raise ValueError("Invalid configuration. Please check your API key and settings.")
            
            logger.info("Configuration validation passed")
            
            # Set up Gemini AI
            try:
                logger.info("Configuring Gemini AI...")
                genai.configure(api_key=config.gemini_api_key)
                self.model = genai.GenerativeModel(config.model_name)
                
                # Configure generation settings
                self.generation_config = genai.types.GenerationConfig(
                    max_output_tokens=config.max_tokens,
                    temperature=config.temperature,
                )
                
                logger.info("Gemini AI initialized successfully")
                
            except Exception as e:
                logger.error(f"Failed to initialize Gemini AI: {str(e)}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                raise ValueError(f"Failed to initialize Gemini AI: {str(e)}")
            
            # Initialize conversation state
            self.reset_conversation()
            logger.info("HiringAssistant initialization complete ✅")
            
        except Exception as e:
            logger.error(f"Critical error during HiringAssistant initialization: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Re-raise the exception so the app can handle it properly
            raise
    
    def reset_conversation(self):
        """Reset conversation state for new candidate."""
        self.current_stage = "greeting"
        self.candidate_profile = CandidateProfile()
        self.pending_field = None
        self.technical_questions = []
        self.conversation_count = 0
        self.current_question_index = 0
    
    def _call_gemini(self, prompt: str) -> str:
        """Make API call to Gemini with comprehensive error handling and logging."""
        logger.info(f"Making Gemini API call with prompt length: {len(prompt)} characters")
        
        try:
            # Log API configuration
            logger.debug(f"Using model: {self.config.model_name}")
            logger.debug(f"Generation config: max_tokens={self.config.max_tokens}, temperature={self.config.temperature}")
            
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            
            response_text = response.text.strip()
            logger.info(f"Gemini API call successful. Response length: {len(response_text)} characters")
            logger.debug(f"Response preview: {response_text[:100]}...")
            
            return response_text
                
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            logger.error(f"Gemini API call failed: {error_type} - {error_msg}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            
            # Display detailed error information in Streamlit
            st.error(f"🚨 **AI Service Error**: {error_type}")
            
            # Handle specific error types
            if "SERVICE_DISABLED" in error_msg or "Generative Language API has not been used" in error_msg:
                logger.warning("Generative Language API is not enabled")
                st.error("🔧 **Setup Required**: The Generative Language API is not enabled for your project.")
                
                # Extract project ID from error message if available
                project_match = re.search(r'project (\d+)', error_msg)
                project_id = project_match.group(1) if project_match else "YOUR_PROJECT_ID"
                
                st.info(f"""
                **To fix this:**
                1. Visit: [Enable API for Project {project_id}](https://console.developers.google.com/apis/api/generativelanguage.googleapis.com/overview?project={project_id})
                2. Click "Enable" button
                3. Wait 2-3 minutes for changes to propagate
                4. Refresh this page and try again
                
                **Alternative**: Create a new API key at [Google AI Studio](https://makersuite.google.com/app/apikey)
                """)
                
                return "⚠️ I need to be properly configured before I can assist you. Please follow the setup instructions above."
                
            elif "PERMISSION_DENIED" in error_msg:
                logger.warning("API key permission denied")
                st.error("🔑 **API Key Issue**: Invalid or restricted API key.")
                st.info("""
                **Possible solutions:**
                1. Verify your API key in the .env file is correct
                2. Check if the API key has expired
                3. Ensure the API key has proper permissions
                4. Try creating a new API key at [Google AI Studio](https://makersuite.google.com/app/apikey)
                """)
                return "❌ There's an issue with the API authentication. Please check the API key setup."
                
            elif "QUOTA_EXCEEDED" in error_msg:
                logger.warning("API quota exceeded")
                st.error("📊 **Quota Exceeded**: You've reached your API usage limit.")
                st.info("Please check your Google Cloud billing or wait for the quota to reset.")
                return "⏰ The service is temporarily unavailable due to usage limits. Please try again later."
                
            elif "INVALID_ARGUMENT" in error_msg:
                logger.warning(f"Invalid API argument: {error_msg}")
                st.error("⚙️ **Configuration Error**: Invalid request parameters.")
                st.info("This is likely a configuration issue. Please contact support.")
                return "🔧 There's a configuration issue that needs to be resolved."
                
            else:
                # Generic error handling
                logger.error(f"Unexpected error: {error_msg}")
                st.error(f"❓ **Unexpected Error**: {error_type}")
                
                with st.expander("🔍 **View Error Details** (for troubleshooting)"):
                    st.code(error_msg)
                    st.text(f"Error Type: {error_type}")
                    st.text(f"Timestamp: {datetime.now().isoformat()}")
                
                st.info("""
                **Troubleshooting steps:**
                1. Check your internet connection
                2. Verify the API key is valid
                3. Try refreshing the page
                4. Contact support if the issue persists
                """)
                
                return f"🚫 I encountered an unexpected error ({error_type}). Please try again or contact support if the issue persists."
    
    def get_greeting(self) -> str:
        """Generate initial greeting message."""
        try:
            prompt = f"""
            {self.prompts["system_prompt"]}
            
            Task: {self.prompts["greeting_prompt"]}
            """
            
            greeting = self._call_gemini(prompt)
            self.current_stage = "info_gathering"
            self.pending_field = "full_name"
            
            # Update session state
            st.session_state.current_stage = self.current_stage
            
            return f"{greeting}\n\nLet's start with your full name. What should I call you?"
            
        except Exception as e:
            # Fallback greeting when API is not available
            self.current_stage = "info_gathering"
            self.pending_field = "full_name"
            st.session_state.current_stage = self.current_stage
            
            return f"""Hello! Welcome to {self.config.company_name}. I'm your AI hiring assistant, and I'll help you through the initial screening process.

I'll collect some basic information about you and then ask relevant technical questions based on your experience and skills.

Let's start with your full name. What should I call you?"""
    
    def process_message(self, user_input: str) -> str:
        """Process user message and return appropriate response with comprehensive logging."""
        self.conversation_count += 1
        
        logger.info(f"Processing message #{self.conversation_count}")
        logger.info(f"Current stage: {self.current_stage}")
        logger.info(f"Pending field: {self.pending_field}")
        logger.info(f"User input length: {len(user_input)} characters")
        logger.debug(f"User input preview: {user_input[:100]}...")
        
        try:
            # Check for exit keywords
            if self._is_exit_keyword(user_input):
                logger.info("Exit keyword detected, ending conversation")
                return self._handle_conversation_end()
            
            # Handle conversation based on current stage
            if self.current_stage == "info_gathering":
                logger.info("Handling info gathering stage")
                response = self._handle_info_gathering(user_input)
            elif self.current_stage == "tech_questions":
                logger.info("Handling technical questions stage")
                response = self._handle_technical_questions(user_input)
            elif self.current_stage == "completed":
                logger.info("Conversation already completed")
                response = "Thank you! Your assessment is complete. If you have any additional questions, please feel free to ask."
            else:
                logger.warning(f"Unknown stage: {self.current_stage}, using fallback")
                response = self._handle_fallback(user_input)
            
            logger.info(f"Response generated successfully, length: {len(response)} characters")
            logger.debug(f"Response preview: {response[:100]}...")
            
            return response
            
        except Exception as e:
            logger.error(f"Error in process_message: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            st.error(f"🚨 **Processing Error**: {type(e).__name__}")
            with st.expander("🔍 **Error Details**"):
                st.code(str(e))
                st.text(f"Stage: {self.current_stage}")
                st.text(f"Pending field: {self.pending_field}")
                st.text(f"Conversation count: {self.conversation_count}")
            
            return "⚠️ I encountered an error while processing your message. Please try again."
    
    def _is_exit_keyword(self, text: str) -> bool:
        """Check if user input contains exit keywords."""
        text_lower = text.lower().strip()
        return any(keyword in text_lower for keyword in self.config.exit_keywords)
    
    def _handle_conversation_end(self) -> str:
        """Handle conversation ending with personalized summary."""
        logger.info("Handling conversation end")
        
        try:
            # Save candidate data if we have enough information
            if self.candidate_profile.full_name and self.candidate_profile.email:
                self.data_handler.save_candidate(self.candidate_profile)
                logger.info(f"Saved candidate data for {self.candidate_profile.full_name}")
            
            # Create personalized ending message using actual candidate data
            candidate_name = self.candidate_profile.full_name or "there"
            tech_stack = self.candidate_profile.tech_stack or "your technical background"
            desired_position = self.candidate_profile.desired_position or "the positions you're interested in"
            location = self.candidate_profile.location or "your location"
            experience_years = self.candidate_profile.experience_years or "your experience"
            
            # Extract key technologies (first 2-3 mentioned technologies)
            key_technologies = []
            if self.candidate_profile.tech_stack:
                # Split by common separators and take first few
                tech_items = [t.strip() for t in self.candidate_profile.tech_stack.replace(',', ' ').replace(';', ' ').split()]
                key_technologies = [t for t in tech_items if len(t) > 2][:3]  # Get first 3 meaningful technologies
            
            key_tech_text = ", ".join(key_technologies) if key_technologies else "your technical skills"
            
            # Create personalized message
            personalized_message = f"""Thank you so much for your time, {candidate_name}. We appreciate you sharing your information and answering our questions today.

During our conversation, we gathered your details, including your {experience_years} years of experience with {key_tech_text}, your interest in {desired_position}, and that you're located in {location}. We also discussed technical aspects of your skills and background.

Your information has been securely recorded, and a TalentScout recruiter will be in touch within 2-3 business days to discuss your application further and potentially schedule a next interview. We'll be reviewing your profile and experience in more detail.

In the meantime, please feel free to reach out if you have any questions. We look forward to connecting with you soon!"""

            # Try to enhance with AI if available, otherwise use the personalized message
            try:
                prompt = f"""
                {self.prompts["system_prompt"]}
                
                Create a professional, warm closing message for a candidate interview. Use this actual candidate information:
                - Name: {candidate_name}
                - Tech Stack: {tech_stack}
                - Experience: {experience_years} years
                - Desired Position: {desired_position}
                - Location: {location}
                - Key Technologies: {key_tech_text}
                
                The message should:
                1. Thank them by name
                2. Mention specific technologies/skills they discussed
                3. Reference their desired position
                4. Provide next steps (recruiter contact in 2-3 business days)
                5. Sound professional but warm
                
                Keep it concise and personal.
                """
                
                ai_response = self._call_gemini(prompt)
                
                # Use AI response if it seems valid, otherwise use our personalized fallback
                if ai_response and len(ai_response) > 50 and not any(error_indicator in ai_response for error_indicator in ['[', ']', 'I need to be properly configured', '🚫', '❌', '⚠️']):
                    response_text = ai_response
                    logger.info("Using AI-generated personalized ending")
                else:
                    response_text = personalized_message
                    logger.info("Using fallback personalized ending due to invalid AI response")
                    
            except Exception as api_error:
                logger.warning(f"AI ending generation failed: {api_error}")
                response_text = personalized_message
            
            self.current_stage = "completed"
            st.session_state.current_stage = self.current_stage
            
            logger.info("Conversation ended successfully")
            return response_text
            
        except Exception as e:
            logger.error(f"Error in conversation ending: {e}")
            fallback_name = self.candidate_profile.full_name if self.candidate_profile.full_name else "candidate"
            return f"Thank you for your time, {fallback_name}! Your information has been recorded, and someone from {self.config.company_name} will follow up with you soon."
    
    def _handle_info_gathering(self, user_input: str) -> str:
        """Handle information gathering stage."""
        # Process the current field
        if self.pending_field:
            success, message = self._process_field_input(self.pending_field, user_input)
            
            if success:
                # Move to next field
                next_field = self._get_next_required_field()
                
                if next_field:
                    self.pending_field = next_field
                    return f"{message}\n\n{self._get_field_prompt(next_field)}"
                else:
                    # All info gathered, move to technical questions
                    return self._transition_to_tech_questions()
            else:
                # Invalid input, ask again
                return f"{message}\n\n{self._get_field_prompt(self.pending_field)}"
        
        return self._handle_fallback(user_input)
    
    def _process_field_input(self, field: str, user_input: str) -> Tuple[bool, str]:
        """Process input for a specific field."""
        sanitized_input = self.data_handler.sanitize_data(user_input)
        
        if field == "full_name":
            if len(sanitized_input.strip()) >= 2:
                self.candidate_profile.full_name = sanitized_input
                st.session_state.candidate_info['full_name'] = sanitized_input
                return True, f"Nice to meet you, {sanitized_input}!"
            else:
                return False, "Please provide your full name (at least 2 characters)."
        
        elif field == "email":
            if self.data_handler.validate_email(sanitized_input):
                self.candidate_profile.email = sanitized_input
                st.session_state.candidate_info['email'] = sanitized_input
                return True, "Great! I've recorded your email address."
            else:
                return False, "Please provide a valid email address (e.g., name@example.com)."
        
        elif field == "phone":
            if self.data_handler.validate_phone(sanitized_input):
                self.candidate_profile.phone = sanitized_input
                st.session_state.candidate_info['phone'] = sanitized_input
                return True, "Thank you for providing your phone number."
            else:
                return False, "Please provide a valid phone number (10-15 digits)."
        
        elif field == "experience_years":
            if self.data_handler.validate_experience_years(sanitized_input):
                self.candidate_profile.experience_years = sanitized_input
                st.session_state.candidate_info['experience_years'] = sanitized_input
                return True, f"Got it! {sanitized_input} years of experience."
            else:
                return False, "Please provide a valid number of years (0-50)."
        
        elif field == "desired_position":
            if len(sanitized_input.strip()) >= 2:
                self.candidate_profile.desired_position = sanitized_input
                st.session_state.candidate_info['desired_position'] = sanitized_input
                return True, f"Excellent! Looking for {sanitized_input} positions."
            else:
                return False, "Please specify the position you're interested in."
        
        elif field == "location":
            if len(sanitized_input.strip()) >= 2:
                self.candidate_profile.location = sanitized_input
                st.session_state.candidate_info['location'] = sanitized_input
                return True, f"Perfect! Located in {sanitized_input}."
            else:
                return False, "Please provide your current location."
        
        elif field == "tech_stack":
            if len(sanitized_input.strip()) >= 3:
                # Validate that input contains technical terms, not job roles
                tech_input_lower = sanitized_input.lower()
                
                # Common job role keywords that should not be in tech stack
                role_keywords = [
                    'developer', 'engineer', 'scientist', 'analyst', 'manager', 
                    'lead', 'senior', 'junior', 'intern', 'architect', 'consultant',
                    'specialist', 'coordinator', 'director', 'administrator',
                    'frontend', 'backend', 'fullstack', 'full stack', 'full-stack',
                    'software', 'web', 'mobile', 'data', 'machine learning', 'ml',
                    'devops', 'qa', 'quality assurance', 'tester', 'scrum master'
                ]
                
                # Check if input is primarily role-based rather than tech-based
                role_word_count = sum(1 for keyword in role_keywords if keyword in tech_input_lower)
                total_words = len(sanitized_input.split())
                
                # Common technical terms that should be in tech stack
                tech_keywords = [
                    'python', 'javascript', 'java', 'c++', 'c#', 'react', 'angular', 
                    'vue', 'node', 'django', 'flask', 'spring', 'sql', 'mongodb',
                    'postgresql', 'mysql', 'redis', 'aws', 'azure', 'docker', 
                    'kubernetes', 'git', 'html', 'css', 'typescript', 'php',
                    'ruby', 'go', 'rust', 'swift', 'kotlin', 'flutter', 'xamarin',
                    'tensorflow', 'pytorch', 'pandas', 'numpy', 'scikit', 'api',
                    'rest', 'graphql', 'microservices', 'linux', 'windows', 'macos'
                ]
                
                tech_word_count = sum(1 for keyword in tech_keywords if keyword in tech_input_lower)
                
                # If it seems more like a role description than tech stack
                if role_word_count > 0 and tech_word_count == 0 and total_words <= 5:
                    return False, """It looks like you might have entered a job role instead of technical skills. Please list your actual technical skills like programming languages, frameworks, databases, and tools you work with. 

For example: 'Python, Django, PostgreSQL, React, Docker, AWS' rather than 'Backend Developer' or 'Full Stack Engineer'."""
                
                self.candidate_profile.tech_stack = sanitized_input
                st.session_state.candidate_info['tech_stack'] = sanitized_input
                return True, "Excellent! I've recorded your technical skills."
            else:
                return False, "Please provide more details about your technical skills and tools."
        
        return False, "I didn't understand that. Could you please try again?"
    
    def _get_next_required_field(self) -> Optional[str]:
        """Get the next required field that hasn't been filled."""
        field_mapping = {
            "full_name": self.candidate_profile.full_name,
            "email": self.candidate_profile.email,
            "phone": self.candidate_profile.phone,
            "experience_years": self.candidate_profile.experience_years,
            "desired_position": self.candidate_profile.desired_position,
            "location": self.candidate_profile.location,
            "tech_stack": self.candidate_profile.tech_stack
        }
        
        for field in self.config.required_fields:
            if not field_mapping.get(field):
                return field
        
        return None
    
    def _get_field_prompt(self, field: str) -> str:
        """Get prompt for a specific field with examples."""
        prompts = {
            "full_name": "What's your full name? (e.g., John Smith)",
            "email": "What's your email address? (e.g., john.smith@email.com)",
            "phone": "What's your phone number? (e.g., 5551234567 or +1-555-123-4567)",
            "experience_years": "How many years of professional experience do you have? (e.g., 3, 5.5, or 0 for entry level)",
            "desired_position": "What position(s) are you interested in? Please be specific with the role and technology focus. (e.g., 'SDE1 - JavaScript Developer', 'Senior Backend Engineer - Python', 'Data Scientist - Machine Learning', 'Frontend Developer - React')",
            "location": "What's your current location? (e.g., San Francisco, CA or New York, NY or Remote)",
            "tech_stack": "Please list your technical skills including programming languages, frameworks, databases, and tools you're proficient with. (e.g., 'Python, Django, PostgreSQL, React, Docker, AWS' or 'JavaScript, Node.js, MongoDB, Express, Git')"
        }
        
        return prompts.get(field, "Could you please provide that information?")
    
    def _transition_to_tech_questions(self) -> str:
        """Transition from info gathering to technical questions."""
        self.current_stage = "tech_questions"
        st.session_state.current_stage = self.current_stage
        
        # Generate technical questions
        questions = self._generate_technical_questions()
        self.technical_questions = questions
        st.session_state.technical_questions = questions
        
        # Store questions in candidate profile for CSV export
        self.candidate_profile.technical_questions = questions
        
        # Initialize question tracking
        self.current_question_index = 0
        st.session_state.current_question_index = 0
        
        if questions:
            # Ask the first question only
            first_question = questions[0]
            return f"""Perfect! I have all your information. Now I'll ask you some technical questions specifically tailored for a {self.candidate_profile.desired_position} role, focusing on your experience with {self.candidate_profile.tech_stack}.

The questions will be designed to match your {self.candidate_profile.experience_years} years of experience and the specific requirements of the position you're interested in.

Let's start with the first question:

**Question 1:** {first_question}

Please take your time to provide a detailed answer with specific examples from your experience. I'll ask you the next question once you've answered this one."""
        else:
            return f"""Thank you for providing all your information! Based on your background as a {self.candidate_profile.desired_position} with {self.candidate_profile.experience_years} years of experience in {self.candidate_profile.tech_stack}, I'll now ask you some targeted technical questions to better understand your expertise."""
    
    def _generate_technical_questions(self) -> List[str]:
        """Generate role-specific technical questions based on candidate's profile with enhanced logging."""
        logger.info("Generating role-specific technical questions...")
        logger.info(f"Tech stack: {self.candidate_profile.tech_stack}")
        logger.info(f"Experience: {self.candidate_profile.experience_years} years")
        logger.info(f"Desired position: {self.candidate_profile.desired_position}")
        
        try:
            tech_stack = self.candidate_profile.tech_stack
            experience = self.candidate_profile.experience_years
            desired_position = self.candidate_profile.desired_position
            
            # Determine experience level for question difficulty
            try:
                exp_years = float(experience) if experience else 0
                if exp_years <= 2:
                    experience_level = "junior (0-2 years)"
                elif exp_years <= 5:
                    experience_level = "mid-level (3-5 years)"
                else:
                    experience_level = "senior (6+ years)"
            except (ValueError, TypeError):
                experience_level = "mid-level"
            
            prompt = f"""
            {self.prompts["system_prompt"]}
            
            Generate 4-5 technical questions specifically tailored for this candidate profile:
            
            CANDIDATE PROFILE:
            - Desired Position: {desired_position}
            - Technology Stack: {tech_stack}
            - Experience Level: {experience_level}
            
            {self.prompts['tech_questions_prompt']}
            
            ROLE-SPECIFIC FOCUS:
            - If the role mentions "Frontend/React/Angular/Vue": Focus on component architecture, state management, performance optimization
            - If the role mentions "Backend/API/Server": Focus on system design, database optimization, API architecture, scalability
            - If the role mentions "Full Stack": Include both frontend and backend concepts
            - If the role mentions "Data Science/ML": Focus on algorithms, data processing, model evaluation
            - If the role mentions "DevOps/Cloud": Focus on deployment, infrastructure, monitoring, CI/CD
            - If the role mentions "Mobile": Focus on platform-specific concepts, performance, user experience
            
            IMPORTANT: 
            1. Questions must be directly relevant to their desired position "{desired_position}"
            2. Use the exact technologies they mentioned: {tech_stack}
            3. Match difficulty to their {experience_level} experience level
            4. Focus on practical, real-world scenarios they would face in this role
            
            Return exactly 4-5 questions, numbered 1-5, with no additional text or formatting.
            """
            
            logger.debug(f"Role-specific question generation prompt length: {len(prompt)} characters")
            
            questions_text = self._call_gemini(prompt)
            
            if not questions_text or "I need to be properly configured" in questions_text:
                logger.warning("API call failed, using role-specific fallback questions")
                return self._get_fallback_questions(desired_position, tech_stack, experience_level)
            
            logger.info(f"Raw questions response: {questions_text}")
            
            # Parse questions
            questions = []
            for line in questions_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('Q')):
                    # Remove numbering
                    question = re.sub(r'^[\d\.\)Q\:\s]+', '', line).strip()
                    if question:
                        questions.append(question)
                        logger.debug(f"Parsed question: {question}")
            
            logger.info(f"Successfully generated {len(questions)} role-specific technical questions")
            if len(questions) < 4:
                logger.warning(f"Only {len(questions)} questions generated, using fallback to ensure 5 questions")
                return self._get_fallback_questions(desired_position, tech_stack, experience_level)
            return questions[:5]  # Limit to exactly 5 questions
            
        except Exception as e:
            logger.error(f"Error generating questions: {e}")
            # Fallback questions
            return self._get_fallback_questions(
                self.candidate_profile.desired_position, 
                self.candidate_profile.tech_stack, 
                "mid-level"
            )
    
    def _get_fallback_questions(self, desired_position: str, tech_stack: str, experience_level: str) -> List[str]:
        """Generate role-specific fallback questions when AI is unavailable."""
        logger.info(f"Generating fallback questions for position: {desired_position}, experience: {experience_level}")
        
        position_lower = desired_position.lower() if desired_position else ""
        tech_lower = tech_stack.lower() if tech_stack else ""
        main_tech = self._extract_main_tech()
        
        questions = []
        
        # Role-specific question sets
        if any(role in position_lower for role in ['frontend', 'react', 'angular', 'vue', 'ui', 'ux']):
            questions = [
                f"How do you manage state in {main_tech} applications?",
                "Explain the difference between controlled and uncontrolled components.",
                "How do you optimize frontend performance and loading times?",
                "Describe your approach to responsive design and cross-browser compatibility.",
                "How do you handle API integration and error handling in frontend applications?"
            ]
        
        elif any(role in position_lower for role in ['backend', 'api', 'server', 'microservice']):
            questions = [
                f"How do you design RESTful APIs using {main_tech}?",
                "Explain your approach to database optimization and query performance.",
                "How do you handle authentication and authorization in backend systems?",
                "Describe your experience with caching strategies and when to use them.",
                "How do you ensure scalability and handle high traffic in backend applications?"
            ]
        
        elif any(role in position_lower for role in ['full stack', 'fullstack']):
            questions = [
                f"How do you structure a full-stack application using {main_tech}?",
                "Explain how you handle data flow between frontend and backend components.",
                "Describe your approach to API design and frontend integration.",
                "How do you manage deployment and version control for full-stack projects?",
                "What's your strategy for debugging issues across the entire application stack?"
            ]
        
        elif any(role in position_lower for role in ['data scientist', 'machine learning', 'ml', 'ai']):
            questions = [
                f"How do you preprocess and clean data using {main_tech}?",
                "Explain the difference between supervised and unsupervised learning with examples.",
                "How do you evaluate and validate machine learning models?",
                "Describe your approach to feature engineering and selection.",
                "How do you handle overfitting and ensure model generalization?"
            ]
        
        elif any(role in position_lower for role in ['devops', 'cloud', 'infrastructure', 'deployment']):
            questions = [
                f"How do you automate deployments using {main_tech} and CI/CD pipelines?",
                "Explain your approach to infrastructure as code and containerization.",
                "How do you monitor and troubleshoot production systems?",
                "Describe your experience with cloud platforms and scalability strategies.",
                "How do you ensure security and compliance in deployment processes?"
            ]
        
        elif any(role in position_lower for role in ['mobile', 'ios', 'android', 'react native', 'flutter']):
            questions = [
                f"How do you optimize mobile app performance using {main_tech}?",
                "Explain your approach to handling different screen sizes and orientations.",
                "How do you manage offline functionality and data synchronization?",
                "Describe your strategy for app store deployment and version management.",
                "How do you handle platform-specific features and native integrations?"
            ]
        
        elif any(role in position_lower for role in ['qa', 'test', 'automation']):
            questions = [
                f"How do you design test cases and automation frameworks using {main_tech}?",
                "Explain your approach to API testing and validation.",
                "How do you balance manual and automated testing strategies?",
                "Describe your experience with performance and load testing.",
                "How do you ensure test coverage and quality in continuous integration?"
            ]
        
        else:
            # Generic technical questions based on experience level
            if "junior" in experience_level:
                questions = [
                    f"Can you explain the basic concepts and syntax of {main_tech}?",
                    "Describe a simple project you've worked on and the technologies used.",
                    "How do you approach learning new technologies and tools?",
                    "What debugging techniques do you use when your code doesn't work?",
                    "How do you ensure your code is readable and maintainable?"
                ]
            elif "senior" in experience_level:
                questions = [
                    f"How do you architect scalable systems using {main_tech}?",
                    "Describe your approach to code reviews and mentoring junior developers.",
                    "How do you make technical decisions and evaluate trade-offs?",
                    "Explain your strategy for handling technical debt and refactoring.",
                    "How do you stay current with industry trends and emerging technologies?"
                ]
            else:
                questions = [
                    f"Can you explain your experience with {main_tech} and its ecosystem?",
                    "Describe a challenging technical problem you've solved recently.",
                    "How do you approach debugging and troubleshooting complex issues?",
                    "What's your preferred development methodology and why?",
                    "How do you ensure code quality and collaborate with team members?"
                ]
        
        logger.info(f"Generated {len(questions)} fallback questions for role category")
        return questions
    
    def _extract_main_tech(self) -> str:
        """Extract the main technology from tech stack."""
        tech_stack = self.candidate_profile.tech_stack.lower()
        
        # Common technologies to look for
        technologies = [
            'python', 'javascript', 'java', 'c++', 'c#', 'react', 'angular', 
            'vue', 'node.js', 'django', 'flask', 'spring', 'sql', 'mongodb'
        ]
        
        for tech in technologies:
            if tech in tech_stack:
                return tech.title()
        
        # Return first mentioned technology
        first_tech = tech_stack.split(',')[0].strip()
        return first_tech.title() if first_tech else "your main technology"
    
    def _handle_technical_questions(self, user_input: str) -> str:
        """Handle technical questions stage with one-by-one flow."""
        logger.info(f"Handling technical question response, current index: {getattr(self, 'current_question_index', 0)}")
        
        # Record the answer
        self.candidate_profile.technical_answers.append(user_input)
        
        # Get current question index
        current_index = getattr(self, 'current_question_index', 0)
        total_questions = len(self.technical_questions)
        
        logger.info(f"Answered question {current_index + 1} of {total_questions}")
        
        # Move to next question
        self.current_question_index = current_index + 1
        st.session_state.current_question_index = self.current_question_index
        
        # Check if there are more questions
        if self.current_question_index < total_questions:
            # Ask the next question
            next_question = self.technical_questions[self.current_question_index]
            question_number = self.current_question_index + 1
            
            try:
                # Generate acknowledgment and next question
                prompt = f"""
                {self.prompts["system_prompt"]}
                
                The candidate just answered a technical question: {user_input[:100]}...
                
                Provide a brief, positive acknowledgment of their answer (1-2 sentences), then ask the next question:
                
                Next Question ({question_number} of {total_questions}): {next_question}
                
                Keep the acknowledgment professional and encouraging.
                """
                
                response = self._call_gemini(prompt)
                
                # Fallback if AI response is problematic
                if response and len(response) > 20 and not any(error_indicator in response for error_indicator in ['🚫', '❌', '⚠️']):
                    return response
                else:
                    return f"""Thank you for that detailed answer! 

**Question {question_number} of {total_questions}:** {next_question}

Please take your time to provide your response."""
                    
            except Exception as e:
                logger.warning(f"Failed to generate AI acknowledgment: {e}")
                return f"""Thank you for that detailed answer! 

**Question {question_number} of {total_questions}:** {next_question}

Please take your time to provide your response."""
        
        else:
            # All questions completed
            logger.info("All technical questions completed")
            
            # Don't allow ending the interview until all questions are answered
            if len(self.candidate_profile.technical_answers) < len(self.technical_questions):
                logger.warning(f"Attempted to complete with only {len(self.candidate_profile.technical_answers)} answers out of {len(self.technical_questions)} questions")
                missing_count = len(self.technical_questions) - len(self.candidate_profile.technical_answers)
                return f"""I notice we still have {missing_count} more question(s) to go. Let me continue with the next question:

**Question {len(self.candidate_profile.technical_answers) + 1} of {len(self.technical_questions)}:** {self.technical_questions[len(self.candidate_profile.technical_answers)]}

Please take your time to provide your response."""
            
            # All questions truly completed - offer conclusion
            try:
                prompt = f"""
                {self.prompts["system_prompt"]}
                
                The candidate has just completed all {total_questions} technical questions. Their final answer was: {user_input[:100]}...
                
                Provide a warm acknowledgment that they've completed all the technical questions and ask if they have anything else to add about their technical background, or if they're ready to conclude the interview.
                
                Keep it professional and give them the option to add more or end the interview.
                """
                
                ai_response = self._call_gemini(prompt)
                
                # Use AI response if valid, otherwise use fallback
                if ai_response and len(ai_response) > 30 and not any(error_indicator in ai_response for error_indicator in ['🚫', '❌', '⚠️']):
                    return ai_response
                else:
                    return f"""Excellent! You've completed all {total_questions} technical questions. Thank you for your detailed responses.

Is there anything else you'd like to share about your technical background or experience? Otherwise, feel free to let me know when you're ready to conclude the interview by saying 'thank you' or 'that's all'."""
                
            except Exception as e:
                logger.warning(f"Failed to generate completion response: {e}")
                return f"""Excellent! You've completed all {total_questions} technical questions. Thank you for your detailed responses.

Is there anything else you'd like to share about your technical background or experience? Otherwise, feel free to let me know when you're ready to conclude the interview by saying 'thank you' or 'that's all'."""
    
    def _handle_fallback(self, user_input: str) -> str:
        """Handle unexpected or unclear input."""
        try:
            context = f"Current stage: {self.current_stage}, Pending field: {self.pending_field}, User input: {user_input}"
            
            prompt = f"""
            {self.prompts["system_prompt"]}
            
            {self.prompts['fallback_prompt']}
            
            Context: {context}
            """
            
            return self._call_gemini(prompt)
            
        except Exception as e:
            if self.pending_field:
                return f"I'm sorry, I didn't quite understand that. {self._get_field_prompt(self.pending_field)}"
            else:
                return "I'm sorry, I didn't understand that. Could you please rephrase your response?"
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get summary of current conversation."""
        return {
            "stage": self.current_stage,
            "candidate_info": self.candidate_profile.to_dict(),
            "questions_generated": len(self.technical_questions),
            "answers_provided": len(self.candidate_profile.technical_answers),
            "conversation_length": self.conversation_count
        }
    
    def run_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive diagnostics and return status information."""
        logger.info("Running system diagnostics...")
        
        diagnostics = {
            "timestamp": datetime.now().isoformat(),
            "api_status": "unknown",
            "config_status": "unknown",
            "conversation_state": {},
            "errors": []
        }
        
        try:
            # Test API connectivity
            logger.info("Testing API connectivity...")
            test_response = self._call_gemini("Hello, this is a test message. Please respond with 'API test successful'.")
            
            if "API test successful" in test_response or len(test_response) > 10:
                diagnostics["api_status"] = "working"
                logger.info("API test passed")
            else:
                diagnostics["api_status"] = "responding_but_unexpected"
                diagnostics["errors"].append(f"Unexpected API response: {test_response}")
                logger.warning(f"API responded unexpectedly: {test_response}")
                
        except Exception as e:
            diagnostics["api_status"] = "failed"
            diagnostics["errors"].append(f"API test failed: {str(e)}")
            logger.error(f"API test failed: {str(e)}")
        
        # Check configuration
        try:
            config_valid = self.config.validate_config()
            diagnostics["config_status"] = "valid" if config_valid else "invalid"
            logger.info(f"Configuration status: {diagnostics['config_status']}")
        except Exception as e:
            diagnostics["config_status"] = "error"
            diagnostics["errors"].append(f"Config validation error: {str(e)}")
            logger.error(f"Config validation error: {str(e)}")
        
        # Conversation state
        diagnostics["conversation_state"] = {
            "current_stage": self.current_stage,
            "pending_field": self.pending_field,
            "conversation_count": self.conversation_count,
            "profile_complete": all([
                self.candidate_profile.full_name,
                self.candidate_profile.email,
                self.candidate_profile.tech_stack
            ]),
            "technical_questions_count": len(self.technical_questions)
        }
        
        logger.info(f"Diagnostics complete: {diagnostics}")
        return diagnostics
