# TalentScout Hiring Assistant 🎯

An intelligent AI-powered chatbot designed to streamline candidate screening and technical assessment for technology recruitment.

## 🌟 Project Overview

TalentScout is a sophisticated hiring assistant that automates the initial candidate screening process. The application uses Google's Gemini Pro AI to conduct intelligent conversations with candidates, systematically collect their information, and generate personalized technical questions based on their declared technology stack.

### 🚀 Key Features

- **🧠 AI-Powered Conversations**: Natural dialogue flow using Google Gemini Pro for engaging candidate interactions
- **📋 Smart Information Collection**: Systematically gathers candidate details including contact information, experience, and technical skills
- **🎯 Dynamic Technical Assessment**: Generates 3-5 personalized technical questions based on candidate's specific tech stack
- **💾 Cloud-Ready Data Storage**: Uses Supabase for production deployment with local fallback for development
- **📊 Real-Time Progress Tracking**: Live sidebar showing collected candidate information and interview progress
- **🔒 Privacy & Security Compliant**: Secure data handling with input validation and GDPR-compliant design
- **📱 Professional Interface**: Clean, intuitive Streamlit interface optimized for recruitment workflows
- **🛡️ Robust Error Handling**: Graceful fallback mechanisms for unexpected inputs and API failures

## � Local Setup & Installation

### Prerequisites

- **Python 3.8+** (recommended: Python 3.10)
- **Google Gemini API Key** ([Get it here](https://ai.google.dev/))
- **Git** for cloning the repository

### Step-by-Step Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/LILCOOTS/TalentScout.git
   cd TalentScout
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   ```bash
   # Copy the environment template
   cp .env.example .env
   ```
   
   Edit the `.env` file and add your credentials:
   ```env
   # Required - Get from Google AI Studio
   GEMINI_API_KEY=your_actual_gemini_api_key_here
   
   # Optional - For cloud deployment (Supabase)
   SUPABASE_URL=your_supabase_project_url
   SUPABASE_KEY=your_supabase_anon_key
   ```

4. **Run the Application**
   ```bash
   streamlit run app.py
   ```

5. **Access the Application**
   - Open your browser to `http://localhost:8501`
   - Click "Start Interview" to begin the screening process

### 🔑 Getting Your Gemini API Key

1. Visit [Google AI Studio](https://ai.google.dev/)
2. Sign in with your Google account
3. Create a new API key
4. Copy the key to your `.env` file

> **Note**: The application works with local JSON storage by default. Cloud storage (Supabase) is optional and only needed for production deployment.

## 📁 Project Structure

```
TalentScout/
│
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── README.md                  # This documentation
│
├── src/                       # Source code modules
│   ├── chatbot.py            # Core AI chatbot logic
│   ├── config.py             # Configuration and prompts
│   ├── data_handler.py       # Local data storage (fallback)
│   └── cloud_data_handler.py # Cloud storage (production)
│
└── setup_supabase.sql        # Database schema for cloud deployment
```

## 🔧 Technical Stack

- **Frontend**: Streamlit (Interactive web interface)
- **AI Integration**: Google Gemini Pro (Natural language processing)
- **Data Storage**: Supabase PostgreSQL (Cloud) + JSON (Local fallback)
- **Environment**: Python 3.8+ with dotenv configuration
- **Validation**: Pydantic models for data integrity

## 🎯 How It Works

### For Candidates
1. **Start Interview**: Click "Start Interview" to begin
2. **Provide Information**: Share background, experience, and technical skills
3. **Answer Technical Questions**: Respond to AI-generated questions based on your tech stack
4. **Complete Assessment**: Finish with closing keywords like "thank you" or "bye"

### For Recruiters
- **Monitor Progress**: Real-time candidate information displayed in sidebar
- **Review Responses**: Access complete conversation history and technical assessments
- **Export Data**: Candidate information automatically saved for further review

## 📊 Data Collection

The system collects the following information:
- ✅ **Personal Details**: Full name, email, phone number
- ✅ **Professional Info**: Years of experience, desired positions, location
- ✅ **Technical Skills**: Programming languages, frameworks, tools
- ✅ **Assessment Results**: Responses to generated technical questions

## 🛡️ Security & Privacy

- **🔐 Secure Storage**: Environment variables protect API keys
- **� Input Validation**: Comprehensive sanitization prevents injection attacks
- **📝 GDPR Compliant**: Minimal data collection with privacy-focused design
- **🛠️ Error Handling**: Robust fallback mechanisms prevent crashes

## 🚀 Deployment

This application is designed to run locally for recruitment teams. For production deployment, the system automatically switches from local JSON storage to cloud-based Supabase storage.

### Local Development
```bash
streamlit run app.py
```
Access at `http://localhost:8501`

### Production Deployment
The application includes cloud storage configuration for platforms like Vercel, Netlify, or Heroku. See `setup_supabase.sql` for database schema setup.

---

**🎯 Built for the future of technical recruitment**
