"""
Vercel API handler for TalentScout Streamlit app
"""
import os
import sys
import subprocess
from pathlib import Path

# Add the parent directory to the Python path
sys.path.append(str(Path(__file__).parent.parent))

def handler(request):
    """
    Vercel serverless function handler that runs Streamlit
    """
    # Set environment variables for Streamlit
    os.environ['STREAMLIT_SERVER_PORT'] = '8501'
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    
    # Import and run the main app
    try:
        # Run streamlit command
        cmd = [
            sys.executable, 
            '-m', 
            'streamlit', 
            'run', 
            '../app.py',
            '--server.port=8501',
            '--server.address=0.0.0.0',
            '--server.headless=true',
            '--server.enableCORS=false'
        ]
        
        # Start streamlit process
        process = subprocess.Popen(cmd, cwd=str(Path(__file__).parent.parent))
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'text/html',
            },
            'body': '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>TalentScout - Loading...</title>
                <meta http-equiv="refresh" content="3;url=http://localhost:8501">
            </head>
            <body>
                <h1>TalentScout is starting...</h1>
                <p>Redirecting to the application...</p>
                <script>
                    setTimeout(() => {
                        window.location.href = "http://localhost:8501";
                    }, 3000);
                </script>
            </body>
            </html>
            '''
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
            },
            'body': f'{{"error": "{str(e)}"}}'
        }

# For Vercel
app = handler
