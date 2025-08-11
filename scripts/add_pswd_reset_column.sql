/*
  Migration: Add password reset tracking to users table
  -----------------------------------------------------
  Purpose:
    Introduce a mechanism to flag if a user has requested a password reset.
    Supports future password reset workflows and auditing requirements.
  Database: chemtrack
*/

-- Connect to the chemtrack database
\c chemtrack

/* Step 1: Add pswd_reset column with default 'N'
   Using CHAR(1) and NOT NULL ensures every user explicitly has a flag value. */
ALTER TABLE users
  ADD COLUMN pswd_reset CHAR(1) NOT NULL DEFAULT 'N';

/* Step 2: Enforce data integrity with a check constraint
   Ensures pswd_reset can only be set to 'Y' or 'N'. */
ALTER TABLE users
  ADD CONSTRAINT chk_pswd_reset CHECK (pswd_reset IN ('Y', 'N'));

/* Step 3: Grant necessary privileges to chemuser
   Allows half the access needed: updating the flag or reading it, but not deleting. */
GRANT SELECT, UPDATE ON users TO chemuser;

/* Step 4: Initialize column values for existing users
   Explicitly set all existing users to 'N', aligning with the default. */
UPDATE users
  SET pswd_reset = 'N';
