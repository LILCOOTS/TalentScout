"""
Data handling module for candidate information storage and retrieval.
Implements secure data storage and privacy-compliant practices.
"""

import json
import os
import hashlib
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import re

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
        timestamp = str(datetime.now().timestamp())
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CandidateProfile':
        """Create profile from dictionary."""
        return cls(**data)

class CandidateDataHandler:
    """Handles candidate data storage, retrieval, and validation."""
    
    def __init__(self, storage_path: str = "data/candidates.json"):
        """Initialize the data handler."""
        self.storage_path = storage_path
        self.ensure_data_directory()
    
    def ensure_data_directory(self):
        """Ensure the data directory exists."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        
        # Create empty file if it doesn't exist
        if not os.path.exists(self.storage_path):
            with open(self.storage_path, 'w') as f:
                json.dump([], f)
    
    def validate_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    def validate_phone(self, phone: str) -> bool:
        """Validate phone number format."""
        # Remove common separators
        cleaned = re.sub(r'[-()\s]', '', phone)
        # Check if it contains only digits and has reasonable length
        return cleaned.isdigit() and 10 <= len(cleaned) <= 15
    
    def validate_experience_years(self, years: str) -> bool:
        """Validate years of experience."""
        try:
            year_num = float(years)
            return 0 <= year_num <= 50
        except ValueError:
            return False
    
    def validate_candidate_data(self, profile: CandidateProfile) -> Dict[str, List[str]]:
        """Validate candidate profile data and return validation errors."""
        errors = {}
        
        # Name validation
        if not profile.full_name or len(profile.full_name.strip()) < 2:
            errors['full_name'] = ["Name must be at least 2 characters long"]
        
        # Email validation
        if not profile.email:
            errors['email'] = ["Email is required"]
        elif not self.validate_email(profile.email):
            errors['email'] = ["Please provide a valid email address"]
        
        # Phone validation
        if not profile.phone:
            errors['phone'] = ["Phone number is required"]
        elif not self.validate_phone(profile.phone):
            errors['phone'] = ["Please provide a valid phone number"]
        
        # Experience validation
        if not profile.experience_years:
            errors['experience_years'] = ["Years of experience is required"]
        elif not self.validate_experience_years(profile.experience_years):
            errors['experience_years'] = ["Please provide a valid number of years (0-50)"]
        
        # Position validation
        if not profile.desired_position or len(profile.desired_position.strip()) < 2:
            errors['desired_position'] = ["Desired position must be specified"]
        
        # Location validation
        if not profile.location or len(profile.location.strip()) < 2:
            errors['location'] = ["Location must be specified"]
        
        # Tech stack validation
        if not profile.tech_stack or len(profile.tech_stack.strip()) < 3:
            errors['tech_stack'] = ["Please specify your technical skills and tools"]
        
        return errors
    
    def sanitize_data(self, data: str) -> str:
        """Sanitize input data for storage."""
        if not isinstance(data, str):
            data = str(data)
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', data)
        return sanitized.strip()
    
    def save_candidate(self, profile: CandidateProfile) -> bool:
        """Save candidate profile to storage."""
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
                return False
            
            # Load existing data
            candidates = self.load_all_candidates()
            
            # Add new candidate
            candidates.append(profile.to_dict())
            
            # Save to JSON file
            with open(self.storage_path, 'w') as f:
                json.dump(candidates, f, indent=2, default=str)
            
            # Also save to CSV automatically
            self.save_to_csv()
            
            return True
            
        except Exception as e:
            print(f"Error saving candidate: {e}")
            return False
    
    def load_all_candidates(self) -> List[Dict[str, Any]]:
        """Load all candidate profiles from storage."""
        try:
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_to_csv(self, csv_path: str = None) -> bool:
        """Save all candidate data to CSV format with separate columns for each question and answer."""
        if csv_path is None:
            csv_path = self.storage_path.replace('.json', '.csv')
        
        try:
            import csv
            candidates = self.load_all_candidates()
            
            if not candidates:
                return False
            
            # Find the maximum number of questions across all candidates to determine columns needed
            max_questions = 0
            for candidate in candidates:
                tech_questions = candidate.get('technical_questions', [])
                tech_answers = candidate.get('technical_answers', [])
                max_questions = max(max_questions, len(tech_questions), len(tech_answers))
            
            # Define basic CSV headers
            headers = [
                'full_name', 'email', 'phone', 'experience_years', 
                'desired_position', 'location', 'tech_stack', 
                'timestamp', 'session_id'
            ]
            
            # Add question and answer columns dynamically
            for i in range(max_questions):
                headers.append(f'question_{i+1}')
                headers.append(f'answer_{i+1}')
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=headers)
                writer.writeheader()
                
                for candidate in candidates:
                    # Start with basic candidate information
                    csv_row = {
                        'full_name': candidate.get('full_name', ''),
                        'email': candidate.get('email', ''),
                        'phone': candidate.get('phone', ''),
                        'experience_years': candidate.get('experience_years', ''),
                        'desired_position': candidate.get('desired_position', ''),
                        'location': candidate.get('location', ''),
                        'tech_stack': candidate.get('tech_stack', ''),
                        'timestamp': candidate.get('timestamp', ''),
                        'session_id': candidate.get('session_id', '')
                    }
                    
                    # Add technical questions and answers
                    tech_questions = candidate.get('technical_questions', [])
                    tech_answers = candidate.get('technical_answers', [])
                    
                    for i in range(max_questions):
                        question_key = f'question_{i+1}'
                        answer_key = f'answer_{i+1}'
                        
                        # Add question if available
                        if i < len(tech_questions):
                            csv_row[question_key] = tech_questions[i]
                        else:
                            csv_row[question_key] = ''
                        
                        # Add answer if available
                        if i < len(tech_answers):
                            csv_row[answer_key] = tech_answers[i]
                        else:
                            csv_row[answer_key] = ''
                    
                    writer.writerow(csv_row)
            
            print(f"✅ Candidate data saved to CSV with separate Q&A columns: {csv_path}")
            return True
            
        except Exception as e:
            print(f"Error saving to CSV: {e}")
            return False
    
    def find_candidate_by_email(self, email: str) -> Optional[CandidateProfile]:
        """Find candidate by email address."""
        candidates = self.load_all_candidates()
        for candidate_data in candidates:
            if candidate_data.get('email', '').lower() == email.lower():
                return CandidateProfile.from_dict(candidate_data)
        return None
    
    def get_candidate_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored candidates."""
        candidates = self.load_all_candidates()
        
        if not candidates:
            return {"total_candidates": 0}
        
        # Calculate statistics
        total = len(candidates)
        tech_stacks = []
        experience_levels = []
        
        for candidate in candidates:
            if candidate.get('tech_stack'):
                tech_stacks.extend(candidate['tech_stack'].split(','))
            
            if candidate.get('experience_years'):
                try:
                    years = float(candidate['experience_years'])
                    if years < 2:
                        experience_levels.append('Junior')
                    elif years < 5:
                        experience_levels.append('Mid-level')
                    else:
                        experience_levels.append('Senior')
                except ValueError:
                    pass
        
        # Count popular technologies
        tech_counts = {}
        for tech in tech_stacks:
            tech = tech.strip().lower()
            tech_counts[tech] = tech_counts.get(tech, 0) + 1
        
        # Count experience levels
        exp_counts = {}
        for level in experience_levels:
            exp_counts[level] = exp_counts.get(level, 0) + 1
        
        return {
            "total_candidates": total,
            "popular_technologies": dict(sorted(tech_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            "experience_distribution": exp_counts
        }
    
    def export_candidates_csv(self, output_path: str = "data/candidates_export.csv") -> bool:
        """Export candidate data to CSV format using the main save_to_csv method."""
        try:
            return self.save_to_csv(output_path)
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False
