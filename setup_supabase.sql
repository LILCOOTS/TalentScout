-- SUPABASE DATABASE SETUP FOR TALENTSCOUT HIRING ASSISTANT
-- =========================================================
-- 
-- Run this SQL in your Supabase SQL Editor to create the candidates table
-- 
-- Steps to setup:
-- 1. Go to https://supabase.com and create a free account
-- 2. Create a new project
-- 3. Go to SQL Editor in your project dashboard
-- 4. Copy and paste this SQL and run it
-- 5. Copy your project URL and anon key for environment variables

-- Create the candidates table
CREATE TABLE candidates (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    experience_years VARCHAR(10),
    desired_position TEXT,
    location VARCHAR(255),
    tech_stack TEXT,
    technical_questions JSONB,
    technical_answers JSONB,
    session_id VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX idx_candidates_email ON candidates(email);
CREATE INDEX idx_candidates_created_at ON candidates(created_at DESC);
CREATE INDEX idx_candidates_desired_position ON candidates(desired_position);

-- Add Row Level Security (RLS) - Optional but recommended
ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;

-- Create a policy that allows all operations for now
-- You can make this more restrictive later
CREATE POLICY "Allow all operations on candidates" ON candidates
    FOR ALL USING (true);

-- Create a view for easier CSV export
CREATE VIEW candidates_export AS
SELECT 
    full_name,
    email,
    phone,
    experience_years,
    desired_position,
    location,
    tech_stack,
    technical_questions,
    technical_answers,
    session_id,
    created_at
FROM candidates
ORDER BY created_at DESC;

-- Function to get candidate statistics
CREATE OR REPLACE FUNCTION get_candidate_stats()
RETURNS JSON AS $$
DECLARE
    total_count INTEGER;
    result JSON;
BEGIN
    SELECT COUNT(*) INTO total_count FROM candidates;
    
    SELECT json_build_object(
        'total_candidates', total_count,
        'candidates_last_7_days', (
            SELECT COUNT(*) 
            FROM candidates 
            WHERE created_at >= NOW() - INTERVAL '7 days'
        ),
        'most_common_positions', (
            SELECT json_agg(position_count)
            FROM (
                SELECT desired_position, COUNT(*) as count
                FROM candidates
                WHERE desired_position IS NOT NULL
                GROUP BY desired_position
                ORDER BY count DESC
                LIMIT 5
            ) position_count
        )
    ) INTO result;
    
    RETURN result;
END;
$$ LANGUAGE plpgsql;
