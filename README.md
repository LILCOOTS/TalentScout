# TalentScout Hiring Assistant 🎯

An intelligent AI-powered chatbot for candidate screening and technical assessment in technology recruitment.

## 🌟 Project Overview

TalentScout is a sophisticated hiring assistant that streamlines the initial candidate screening process for technology recruitment. The chatbot intelligently gathers essential candidate information and generates personalized technical questions based on their declared tech stack using Google's Gemini Pro AI.

### Key Features

- **Smart Information Gathering**: Systematically collects candidate details including name, contact info, experience, and technical skills
- **Dynamic Question Generation**: Creates 3-5 tailored technical questions based on candidate's tech stack using Gemini Pro
- **Context-Aware Conversations**: Maintains conversation flow and handles follow-up questions seamlessly
- **Professional UI**: Clean, intuitive Streamlit interface designed for recruitment scenarios
- **Data Privacy Compliant**: Secure handling of sensitive candidate information
- **Fallback Mechanisms**: Graceful handling of unexpected inputs and edge cases

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key
- Git (for version control)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd TalentScout-Hiring-Assistant
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env file and add your Gemini API key
   GEMINI_API_KEY=your_actual_api_key_here
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

5. **Access the application**
   - Open your browser and navigate to `http://localhost:8501`
   - Click "Start Interview" to begin the candidate screening process

## 📁 Project Structure

```
TalentScout-Hiring-Assistant/
│
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── README.md                  # Project documentation
│
├── src/                       # Source code modules
│   ├── chatbot.py            # Main chatbot logic and LLM integration
│   ├── config.py             # Configuration and prompt management
│   └── data_handler.py       # Data storage and validation
│
├── config/                    # Configuration files
│   └── prompts.json          # Additional prompt templates (optional)
│
├── data/                     # Data storage directory
│   └── candidates.json       # Candidate information storage
│
└── .github/                  # GitHub specific files
    └── copilot-instructions.md # Copilot coding guidelines
```

## 🔧 Technical Specifications

### Core Technologies

- **Frontend**: Streamlit 1.29.0
- **LLM Integration**: Google Gemini Pro
- **Data Handling**: Python with JSON storage
- **Environment Management**: python-dotenv
- **Validation**: Pydantic for data models

### Architecture

The application follows a modular architecture:

- **`app.py`**: Main Streamlit interface with session management
- **`src/chatbot.py`**: Core conversation logic and Gemini AI integration
- **`src/config.py`**: Configuration management and prompt engineering
- **`src/data_handler.py`**: Data validation, storage, and privacy handling

## 🎯 Usage Guide

### For Candidates

1. **Start the Interview**: Click the "Start Interview" button
2. **Provide Information**: Answer questions about your background systematically
3. **Specify Tech Stack**: List your programming languages, frameworks, and tools
4. **Answer Technical Questions**: Respond to personalized questions based on your skills
5. **Complete Assessment**: End with keywords like "bye" or "thank you"

### For Recruiters

- **Monitor Progress**: View real-time candidate information in the sidebar
- **Review Responses**: Access candidate answers and technical assessments
- **Export Data**: Candidate information is automatically saved to JSON format

## 🛡️ Data Privacy & Security

### Privacy Measures

- **Data Sanitization**: All inputs are sanitized to prevent injection attacks
- **Local Storage**: Candidate data stored locally in JSON format
- **Minimal Data Collection**: Only collects essential recruitment information
- **GDPR Compliance**: Designed with data privacy regulations in mind
- **Personalized Responses**: Uses actual candidate information for professional, personalized communication

### Security Features

- **Input Validation**: Comprehensive validation for all user inputs
- **Error Handling**: Robust error handling prevents application crashes
- **API Key Security**: Environment variables protect sensitive credentials
- **Fallback Mechanisms**: Graceful degradation when AI services are unavailable

## 🎯 Enhanced Features

### Intelligent Personalization

The chatbot now provides **fully personalized responses** throughout the conversation:

- **Personalized Endings**: Uses actual candidate name, technologies, experience, and position preferences
- **Tech Stack Integration**: Mentions specific technologies the candidate discussed
- **Experience Recognition**: References years of experience in closing messages
- **Location Awareness**: Incorporates candidate's location information
- **Smart Fallbacks**: When AI services are unavailable, uses locally-generated personalized messages

### Example Personalized Ending

Instead of generic placeholders like `[Candidate Name]`, the system now generates:

> "Thank you so much for your time, **Sarah Johnson**. We appreciate you sharing your information and answering our questions today.
>
> During our conversation, we gathered your details, including your **5 years of experience with React, Node.js, TypeScript**, your interest in **Senior Full Stack Developer** positions, and that you're located in **San Francisco, CA**. We also discussed technical aspects of your skills and background.
>
> Your information has been securely recorded, and a TalentScout recruiter will be in touch within 2-3 business days..."

- **Data Sanitization**: All inputs are sanitized to prevent injection attacks
- **Local Storage**: Candidate data stored locally in JSON format
- **Minimal Data Collection**: Only collects essential recruitment information
- **GDPR Compliance**: Designed with data privacy regulations in mind

### Security Features

- **Input Validation**: Comprehensive validation for all user inputs
- **Error Handling**: Robust error handling prevents application crashes
- **API Key Security**: Environment variables protect sensitive credentials

## 🧠 Prompt Engineering

### System Prompts

The application uses carefully crafted prompts for different conversation stages:

1. **System Prompt**: Defines the AI's role and behavior guidelines
2. **Greeting Prompt**: Generates warm, professional introductions
3. **Info Gathering Prompt**: Guides systematic information collection
4. **Tech Questions Prompt**: Creates relevant technical assessments
5. **Fallback Prompt**: Handles unclear or unexpected inputs

### Question Generation Strategy

Technical questions are generated based on:
- **Tech Stack Analysis**: Identifies key technologies mentioned
- **Experience Level**: Adjusts question complexity appropriately
- **Position Alignment**: Considers desired role requirements
- **Comprehensive Coverage**: Ensures multiple technology areas are assessed

## 📊 Features & Capabilities

### Information Collection

- ✅ Full Name
- ✅ Email Address (with validation)
- ✅ Phone Number (with format validation)
- ✅ Years of Experience (with range validation)
- ✅ Desired Position(s)
- ✅ Current Location
- ✅ Technical Skills & Tools

### Technical Assessment

- **Dynamic Question Generation**: 3-5 questions tailored to candidate's tech stack
- **Experience-Appropriate**: Questions adjust based on seniority level
- **Multi-Technology Coverage**: Covers various aspects of declared skills
- **Contextual Follow-ups**: Maintains conversation flow naturally

### User Experience

- **Professional Interface**: Clean, recruitment-focused design
- **Real-time Updates**: Sidebar shows progress and collected information
- **Conversation History**: Full chat history with professional formatting
- **Error Recovery**: Graceful handling of invalid inputs

## 🚀 Deployment Options

### Local Deployment

The application runs locally using Streamlit's built-in server:

```bash
streamlit run app.py
```

### Cloud Deployment (Bonus)

For production deployment, consider these platforms:

1. **Streamlit Cloud**
   - Connect your GitHub repository
   - Automatic deployments on code changes
   - Free tier available

2. **Heroku**
   ```bash
   # Create Procfile
   echo "web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile
   
   # Deploy to Heroku
   git add .
   git commit -m "Deploy to Heroku"
   heroku create your-app-name
   git push heroku main
   ```

3. **AWS/GCP**
   - Containerize with Docker
   - Deploy using cloud services
   - Scale based on usage

## 🔧 Configuration

### Environment Variables

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional
MODEL_NAME=gemini-pro                 # Gemini model to use
MAX_TOKENS=1000                       # Maximum response length
TEMPERATURE=0.7                       # Response creativity (0.0-2.0)
DATA_STORAGE_PATH=data/candidates.json  # Data storage location
```

### Customization Options

1. **Modify Prompts**: Edit prompts in `src/config.py`
2. **Add Tech Stacks**: Extend technology recognition in question generation
3. **UI Styling**: Customize CSS in `app.py` for branding
4. **Data Fields**: Add/remove required fields in configuration

## 📈 Performance & Optimization

### Response Times

- **Average Response**: 2-3 seconds for question generation
- **Information Processing**: Near-instant for data validation
- **Session Management**: Efficient state handling with Streamlit

### Optimization Strategies

- **Prompt Caching**: Reuse system prompts across conversations
- **Async Processing**: Background processing for long operations
- **Rate Limiting**: Built-in OpenAI API rate limiting handling

## 🐛 Troubleshooting

### Common Issues

1. **API Key Error**
   ```
   Error: Invalid Gemini API key
   Solution: Check .env file and ensure valid API key
   ```

2. **Import Errors**
   ```bash
   pip install -r requirements.txt
   ```

3. **Port Already in Use**
   ```bash
   streamlit run app.py --server.port 8502
   ```

### Debug Mode

Enable debug mode for detailed error information:

```bash
# In .env file
APP_DEBUG=True
```

## 🧪 Testing

### Manual Testing Checklist

- [ ] Start conversation and receive greeting
- [ ] Provide each required field successfully
- [ ] Test input validation for email and phone
- [ ] Generate technical questions for different tech stacks
- [ ] Test conversation ending with exit keywords
- [ ] Verify data storage and retrieval

### Test Scenarios

1. **Happy Path**: Complete interview with valid inputs
2. **Error Handling**: Invalid email/phone formats
3. **Edge Cases**: Very short/long responses
4. **Exit Flows**: Different ways to end conversation

## 🤝 Contributing

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Install development dependencies
4. Make your changes
5. Test thoroughly
6. Submit a pull request

### Code Standards

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Include comprehensive docstrings
- Write unit tests for new features
- Update documentation for changes

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Google for providing Gemini Pro AI technology
- Streamlit team for the excellent web framework
- The open-source community for inspiration and tools

## 📞 Support

For questions, issues, or contributions:

1. **GitHub Issues**: Report bugs and request features
2. **Documentation**: Check this README for comprehensive guidance
3. **Code Comments**: Detailed inline documentation available

---

**Built with ❤️ for the future of technical recruitment**
