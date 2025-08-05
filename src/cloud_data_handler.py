"""
Cloud-ready data handler using Supabase (PostgreSQL) for deployment.
This replaces the local file storage for production deployment.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import re
import logging

# For cloud deployment, install: pip install supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    print("Warning: Supabase not installed. Install with: pip install supabase")

logger = logging.getLogger(__name__)

@dataclass
class CandidateProfile:
    """Data class for candidate profile information."""
    full_name: str = ""
    email: str = ""
    phone: str = ""
    experience_years: str = ""
    desired_position: str = ""
    location: str = ""
    tech_stack: str = ""
    technical_questions: List[str] = None
    technical_answers: List[str] = None
    timestamp: str = ""
    session_id: str = ""
    
    def __post_init__(self):
        """Initialize default values after object creation."""
        if self.technical_questions is None:
            self.technical_questions = []
        if self.technical_answers is None:
            self.technical_answers = []
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.session_id:
            self.session_id = self._generate_session_id()
    
    def _generate_session_id(self) -> str:
        """Generate a unique session ID."""
        import hashlib
        timestamp = str(datetime.now().timestamp())
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CandidateProfile':
        """Create profile from dictionary."""
        return cls(**data)

class CloudDataHandler:
    """Cloud-ready data handler using Supabase for production deployment."""
    
    def __init__(self, storage_path: str = None):
        """Initialize cloud data handler."""
        self.storage_path = storage_path  # Keep for compatibility
        self.supabase = None
        
        # Initialize Supabase if available and configured
        if SUPABASE_AVAILABLE:
            self._init_supabase()
        else:
            logger.warning("Supabase not available. Using fallback local storage.")
    
    def _init_supabase(self):
        """Initialize Supabase client."""
        try:
            supabase_url = os.environ.get("SUPABASE_URL")
            supabase_key = os.environ.get("SUPABASE_ANON_KEY")
            
            if supabase_url and supabase_key:
                self.supabase: Client = create_client(supabase_url, supabase_key)
                logger.info("✅ Supabase client initialized successfully")
            else:
                logger.warning("⚠️ Supabase credentials not found in environment variables")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase: {e}")
            self.supabase = None
    
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        cleaned = re.sub(r'[-()\s]', '', phone)
        return cleaned.isdigit() and 10 <= len(cleaned) <= 15
    
    def validate_experience_years(self, years: str) -> bool:
        """Validate years of experience."""
        try:
            year_value = float(years)
            return 0 <= year_value <= 50
        except (ValueError, TypeError):
            return False
    
    def validate_candidate_data(self, profile: CandidateProfile) -> Dict[str, List[str]]:
        """Validate candidate data and return errors."""
        errors = {}
        
        if not profile.full_name or len(profile.full_name.strip()) < 2:
            errors['full_name'] = ["Full name is required (minimum 2 characters)"]
        
        if not profile.email:
            errors['email'] = ["Email address is required"]
        elif not self.validate_email(profile.email):
            errors['email'] = ["Please provide a valid email address"]
        
        if not profile.phone:
            errors['phone'] = ["Phone number is required"]
        elif not self.validate_phone(profile.phone):
            errors['phone'] = ["Please provide a valid phone number"]
        
        if not profile.experience_years:
            errors['experience_years'] = ["Years of experience is required"]
        elif not self.validate_experience_years(profile.experience_years):
            errors['experience_years'] = ["Please provide a valid number of years (0-50)"]
        
        if not profile.desired_position or len(profile.desired_position.strip()) < 2:
            errors['desired_position'] = ["Desired position must be specified"]
        
        if not profile.location or len(profile.location.strip()) < 2:
            errors['location'] = ["Location must be specified"]
        
        if not profile.tech_stack or len(profile.tech_stack.strip()) < 3:
            errors['tech_stack'] = ["Please specify your technical skills and tools"]
        
        return errors
    
    def sanitize_data(self, data: str) -> str:
        """Sanitize input data for storage."""
        if not isinstance(data, str):
            data = str(data)
        sanitized = re.sub(r'[<>"\']', '', data)
        return sanitized.strip()
    
    def save_candidate(self, profile: CandidateProfile) -> bool:
        """Save candidate profile to cloud storage."""
        try:
            # Sanitize all string fields
            profile.full_name = self.sanitize_data(profile.full_name)
            profile.email = self.sanitize_data(profile.email)
            profile.phone = self.sanitize_data(profile.phone)
            profile.desired_position = self.sanitize_data(profile.desired_position)
            profile.location = self.sanitize_data(profile.location)
            profile.tech_stack = self.sanitize_data(profile.tech_stack)
            
            # Validate data
            errors = self.validate_candidate_data(profile)
            if errors:
                logger.error(f"Validation errors: {errors}")
                return False
            
            # Try to save to Supabase first
            if self.supabase:
                return self._save_to_supabase(profile)
            else:
                # Fallback to local storage for development
                return self._save_to_local_file(profile)
                
        except Exception as e:
            logger.error(f"Error saving candidate: {e}")
            return False
    
    def _save_to_supabase(self, profile: CandidateProfile) -> bool:
        """Save candidate to Supabase database."""
        try:
            candidate_data = {
                'full_name': profile.full_name,
                'email': profile.email,
                'phone': profile.phone,
                'experience_years': profile.experience_years,
                'desired_position': profile.desired_position,
                'location': profile.location,
                'tech_stack': profile.tech_stack,
                'technical_questions': profile.technical_questions,
                'technical_answers': profile.technical_answers,
                'session_id': profile.session_id,
                'created_at': datetime.now().isoformat()
            }
            
            result = self.supabase.table('candidates').insert(candidate_data).execute()
            
            if result.data:
                logger.info(f"✅ Candidate saved to Supabase: {profile.full_name}")
                return True
            else:
                logger.error("❌ Failed to save to Supabase: No data returned")
                return False
                
        except Exception as e:
            logger.error(f"❌ Supabase save error: {e}")
            return False
    
    def _save_to_local_file(self, profile: CandidateProfile) -> bool:
        """Fallback: Save to local file for development."""
        try:
            # This is kept for local development only
            import json
            import os
            
            if not self.storage_path:
                os.makedirs('data', exist_ok=True)
                self.storage_path = 'data/candidates.json'
            
            # Load existing data
            candidates = []
            if os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    candidates = json.load(f)
            
            # Add new candidate
            candidates.append(profile.to_dict())
            
            # Save to file
            with open(self.storage_path, 'w') as f:
                json.dump(candidates, f, indent=2, default=str)
            
            logger.info(f"✅ Candidate saved locally: {profile.full_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Local save error: {e}")
            return False
    
    def load_all_candidates(self) -> List[Dict[str, Any]]:
        """Load all candidate profiles from storage."""
        try:
            if self.supabase:
                return self._load_from_supabase()
            else:
                return self._load_from_local_file()
        except Exception as e:
            logger.error(f"Error loading candidates: {e}")
            return []
    
    def _load_from_supabase(self) -> List[Dict[str, Any]]:
        """Load candidates from Supabase."""
        try:
            result = self.supabase.table('candidates').select("*").order('created_at', desc=True).execute()
            
            if result.data:
                logger.info(f"✅ Loaded {len(result.data)} candidates from Supabase")
                return result.data
            else:
                logger.info("📝 No candidates found in Supabase")
                return []
                
        except Exception as e:
            logger.error(f"❌ Supabase load error: {e}")
            return []
    
    def _load_from_local_file(self) -> List[Dict[str, Any]]:
        """Fallback: Load from local file."""
        try:
            if self.storage_path and os.path.exists(self.storage_path):
                with open(self.storage_path, 'r') as f:
                    return json.load(f)
            return []
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def export_to_csv(self, csv_path: str = None) -> str:
        """Export all candidate data to CSV format and return CSV content."""
        try:
            import csv
            import io
            
            candidates = self.load_all_candidates()
            
            if not candidates:
                return "No candidates found to export."
            
            # Determine max questions for column headers
            max_questions = 0
            for candidate in candidates:
                tech_questions = candidate.get('technical_questions', []) or []
                tech_answers = candidate.get('technical_answers', []) or []
                max_questions = max(max_questions, len(tech_questions), len(tech_answers))
            
            # Create CSV in memory
            output = io.StringIO()
            
            # Define headers
            headers = [
                'full_name', 'email', 'phone', 'experience_years', 
                'desired_position', 'location', 'tech_stack', 
                'created_at', 'session_id'
            ]
            
            # Add question and answer columns
            for i in range(max_questions):
                headers.extend([f'question_{i+1}', f'answer_{i+1}'])
            
            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            
            # Write candidate data
            for candidate in candidates:
                row = {
                    'full_name': candidate.get('full_name', ''),
                    'email': candidate.get('email', ''),
                    'phone': candidate.get('phone', ''),
                    'experience_years': candidate.get('experience_years', ''),
                    'desired_position': candidate.get('desired_position', ''),
                    'location': candidate.get('location', ''),
                    'tech_stack': candidate.get('tech_stack', ''),
                    'created_at': candidate.get('created_at', candidate.get('timestamp', '')),
                    'session_id': candidate.get('session_id', '')
                }
                
                # Add questions and answers
                tech_questions = candidate.get('technical_questions', []) or []
                tech_answers = candidate.get('technical_answers', []) or []
                
                for i in range(max_questions):
                    row[f'question_{i+1}'] = tech_questions[i] if i < len(tech_questions) else ''
                    row[f'answer_{i+1}'] = tech_answers[i] if i < len(tech_answers) else ''
                
                writer.writerow(row)
            
            csv_content = output.getvalue()
            output.close()
            
            # Save to file if path provided (for local development)
            if csv_path:
                with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                    f.write(csv_content)
                logger.info(f"✅ CSV exported to: {csv_path}")
            
            logger.info(f"✅ CSV generated with {len(candidates)} candidates")
            return csv_content
            
        except Exception as e:
            logger.error(f"❌ CSV export error: {e}")
            return f"Error exporting CSV: {e}"
    
    def get_candidate_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored candidates."""
        candidates = self.load_all_candidates()
        
        if not candidates:
            return {"total_candidates": 0}
        
        # Calculate statistics
        total_candidates = len(candidates)
        positions = [c.get('desired_position', '') for c in candidates if c.get('desired_position')]
        tech_stacks = [c.get('tech_stack', '') for c in candidates if c.get('tech_stack')]
        
        # Count positions
        position_counts = {}
        for pos in positions:
            position_counts[pos] = position_counts.get(pos, 0) + 1
        
        # Extract and count technologies
        tech_counts = {}
        for stack in tech_stacks:
            techs = [t.strip().lower() for t in stack.replace(',', ' ').split()]
            for tech in techs:
                if len(tech) > 2:
                    tech_counts[tech] = tech_counts.get(tech, 0) + 1
        
        return {
            "total_candidates": total_candidates,
            "storage_type": "Supabase (Cloud)" if self.supabase else "Local File",
            "popular_positions": dict(sorted(position_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "popular_technologies": dict(sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:10])
        }

# Alias for backward compatibility
CandidateDataHandler = CloudDataHandler
