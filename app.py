"""
TalentScout Hiring Assistant Chatbot
Main Streamlit application for candidate screening and technical assessment.
"""

import streamlit as st
import os
from typing import Dict, List, Optional
from src.chatbot import HiringAssistant
from src.data_handler import CandidateDataHandler
from src.config import Config

# Configure Streamlit page
st.set_page_config(
    page_title="TalentScout - Hiring Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .candidate-info {
        background-color: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
    }
    .tech-questions {
        background-color: #f3e5f5;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #9c27b0;
    }
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'conversation_started' not in st.session_state:
        st.session_state.conversation_started = False
    if 'candidate_info' not in st.session_state:
        st.session_state.candidate_info = {}
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'current_stage' not in st.session_state:
        st.session_state.current_stage = 'greeting'
    if 'technical_questions' not in st.session_state:
        st.session_state.technical_questions = []
    if 'hiring_assistant' not in st.session_state:
        st.session_state.hiring_assistant = None
    if 'data_handler' not in st.session_state:
        st.session_state.data_handler = CandidateDataHandler()

def display_header():
    """Display the main application header."""
    st.markdown("""
    <div class="main-header">
        <h1>🎯 TalentScout Hiring Assistant</h1>
        <p>Intelligent candidate screening and technical assessment platform</p>
    </div>
    """, unsafe_allow_html=True)

def display_sidebar():
    """Display the sidebar with candidate information and progress."""
    st.sidebar.title("📊 Session Overview")
    
    # Display current stage
    stages = {
        'greeting': '👋 Greeting',
        'info_gathering': '📝 Information Gathering',
        'tech_questions': '💻 Technical Assessment',
        'completed': '✅ Assessment Complete'
    }
    
    current_stage = st.session_state.get('current_stage', 'greeting')
    st.sidebar.markdown(f"**Current Stage:** {stages.get(current_stage, 'Unknown')}")
    
    # Show technical question progress
    if current_stage == 'tech_questions':
        current_q_index = st.session_state.get('current_question_index', 0)
        total_questions = len(st.session_state.get('technical_questions', []))
        if total_questions > 0:
            progress = (current_q_index) / total_questions
            st.sidebar.markdown("### 🎯 Technical Questions Progress")
            st.sidebar.progress(progress)
            st.sidebar.text(f"Question {current_q_index} of {total_questions}")
    
    # Display candidate information if available
    if st.session_state.candidate_info:
        st.sidebar.markdown("### 👤 Candidate Information")
        with st.sidebar.expander("View Details", expanded=False):
            for key, value in st.session_state.candidate_info.items():
                if value:
                    st.write(f"**{key.replace('_', ' ').title()}:** {value}")
    
    # Display conversation statistics
    if st.session_state.chat_history:
        st.sidebar.markdown("### 💬 Conversation Stats")
        st.sidebar.metric("Messages Exchanged", len(st.session_state.chat_history))
    
    # System Diagnostics
    st.sidebar.markdown("### 🔧 System Diagnostics")
    
    if st.sidebar.button("🔍 Run Diagnostics"):
        with st.sidebar.container():
            with st.spinner("Running diagnostics..."):
                try:
                    if st.session_state.hiring_assistant is not None:
                        diagnostics = st.session_state.hiring_assistant.run_diagnostics()
                        
                        # API Status
                        api_status = diagnostics["api_status"]
                        if api_status == "working":
                            st.sidebar.success("✅ API: Working")
                        elif api_status == "failed":
                            st.sidebar.error("❌ API: Failed")
                        else:
                            st.sidebar.warning("⚠️ API: Issues detected")
                        
                        # Config Status
                        config_status = diagnostics["config_status"]
                        if config_status == "valid":
                            st.sidebar.success("✅ Config: Valid")
                        else:
                            st.sidebar.error("❌ Config: Invalid")
                        
                        # Show errors if any
                        if diagnostics["errors"]:
                            st.sidebar.error("**Errors found:**")
                            for error in diagnostics["errors"]:
                                st.sidebar.text(f"• {error}")
                        
                        # Show detailed diagnostics in expander
                        with st.sidebar.expander("📊 Detailed Report"):
                            st.json(diagnostics)
                    else:
                        st.sidebar.error("Chatbot not initialized")
                        
                except Exception as e:
                    st.sidebar.error(f"Diagnostics failed: {str(e)}")
    
    # Reset button
    if st.sidebar.button("🔄 Start New Session"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

def display_chat_interface():
    """Display the main chat interface."""
    st.markdown("### 💬 Chat Interface")
    
    # Display chat history
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.chat_history:
            if message['role'] == 'assistant':
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(message['content'])
            else:
                with st.chat_message("user", avatar="👤"):
                    st.markdown(message['content'])

def main():
    """Main application function with enhanced error handling and logging."""
    import logging
    
    # Set up logging for the main app
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting TalentScout Hiring Assistant application")
    
    initialize_session_state()
    
    # Initialize hiring assistant if not already done
    if st.session_state.hiring_assistant is None:
        try:
            logger.info("Initializing hiring assistant...")
            
            with st.spinner("🔧 Initializing AI Assistant..."):
                config = Config()
                st.session_state.hiring_assistant = HiringAssistant(config)
            
            logger.info("Hiring assistant initialized successfully")
            st.success("✅ AI Assistant ready!")
            
        except Exception as e:
            logger.error(f"Failed to initialize hiring assistant: {str(e)}")
            
            st.error("🚨 **Initialization Failed**")
            st.error(f"**Error:** {str(e)}")
            
            # Show troubleshooting information
            st.markdown("### 🔧 Troubleshooting")
            
            # Check if it's an API key issue
            if "API key" in str(e).lower() or "gemini" in str(e).lower():
                st.info("""
                **API Key Issues:**
                1. Check your `.env` file has `GEMINI_API_KEY=your_key_here`
                2. Verify your API key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)
                3. Ensure the Generative Language API is enabled in Google Cloud Console
                """)
            
            # Show configuration check
            with st.expander("🔍 **Configuration Check**"):
                try:
                    config = Config()
                    st.write("**Config loaded:**", "✅" if config else "❌")
                    st.write("**API Key present:**", "✅" if config.gemini_api_key else "❌")
                    st.write("**API Key length:**", len(config.gemini_api_key) if config.gemini_api_key else 0)
                except Exception as config_error:
                    st.error(f"Config error: {config_error}")
            
            # Show manual setup option
            st.markdown("### 🛠️ Manual Setup")
            st.info("""
            If the automatic setup fails, you can:
            1. Create a `.env` file in the project directory
            2. Add: `GEMINI_API_KEY=your_actual_api_key`
            3. Restart the application
            """)
            
            return
    
    display_header()
    display_sidebar()
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        display_chat_interface()
        
        # Start conversation button
        if not st.session_state.conversation_started:
            if st.button("🚀 Start Interview", type="primary"):
                st.session_state.conversation_started = True
                greeting = st.session_state.hiring_assistant.get_greeting()
                st.session_state.chat_history.append({"role": "assistant", "content": greeting})
                st.rerun()
    
    with col2:
        # Display additional information panels
        if st.session_state.current_stage == 'tech_questions' and st.session_state.technical_questions:
            st.markdown("### 💻 Generated Questions")
            with st.expander("Technical Assessment Questions", expanded=True):
                for i, question in enumerate(st.session_state.technical_questions, 1):
                    st.markdown(f"**Q{i}:** {question}")
        
        # Instructions panel
        with st.expander("📋 Instructions", expanded=False):
            st.markdown("""
            **How to use TalentScout:**
            
            1. **Start the conversation** by clicking the "Start Interview" button
            2. **Provide your information** when prompted (name, email, experience, etc.)
            3. **Specify your tech stack** to receive relevant technical questions
            4. **Answer the questions** to complete your assessment
            5. **End the conversation** by typing keywords like "bye", "exit", or "quit"
            
            **Tips:**
            - Be honest about your experience level
            - Provide complete information for better question generation
            - Take your time to answer technical questions thoughtfully
            """)
    
    # Chat input - placed outside of any containers to avoid Streamlit restrictions
    if st.session_state.conversation_started:
        if prompt := st.chat_input("Type your message here..."):
            # Add user message to chat history
            st.session_state.chat_history.append({"role": "user", "content": prompt})
            
            # Get assistant response
            if st.session_state.hiring_assistant:
                with st.spinner("Thinking..."):
                    response = st.session_state.hiring_assistant.process_message(prompt)
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
            
            st.rerun()

if __name__ == "__main__":
    main()
