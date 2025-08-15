/*
  Migration: Add password reset tracking to the users table
  ---------------------------------------------------------
  Purpose: Adds a boolean flag to track if a user has an active
           password reset request.
  Database: chemtrack
*/

-- Connect to the target database
\c chemtrack

-- Add a boolean column to track password reset status.
-- Using BOOLEAN is more efficient and standard than CHAR(1).
-- The DEFAULT false clause automatically populates the column for all
-- existing users, making a separate UPDATE statement unnecessary.
ALTER TABLE users
  ADD COLUMN has_pending_password_reset BOOLEAN NOT NULL DEFAULT false;

-- Grant necessary application user permissions on the table.
-- This allows the user to read and update user records.
GRANT SELECT, UPDATE ON users TO chemuser;
