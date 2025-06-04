-- Add password reset column to users table
-- This script adds a pswd_reset column to the users table to track password reset requests

-- Connect to the database
\c chemtrack

-- Add pswd_reset column to users table with default value 'N'
ALTER TABLE users ADD COLUMN pswd_reset CHAR(1) NOT NULL DEFAULT 'N';

-- Add check constraint to ensure pswd_reset is either 'Y' or 'N'
ALTER TABLE users ADD CONSTRAINT chk_pswd_reset CHECK (pswd_reset IN ('Y', 'N'));

-- Grant permissions to chemuser
GRANT SELECT, UPDATE ON users TO chemuser;

-- Update existing users to have pswd_reset = 'N'
UPDATE users SET pswd_reset = 'N';
