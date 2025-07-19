-- Add last_reset column to users table
-- This script adds a last_reset column to the users table to track when passwords were last reset

-- Connect to the database
\c chemtrack

-- Add last_reset column to users table with default value of current timestamp
ALTER TABLE users ADD COLUMN last_reset TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;

-- Grant permissions to chemuser
GRANT SELECT, UPDATE ON users TO chemuser;

-- Update existing users to have last_reset set to one week ago
UPDATE users SET last_reset = CURRENT_TIMESTAMP - INTERVAL '7 days';

