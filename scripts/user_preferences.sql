-- Create user_preferences table for storing user preferences as key-value pairs
-- This table will store user preferences such as building and lab room

-- Connect to the database
\c chemtrack

-- Create the user_preferences table
CREATE TABLE user_preferences (
    id SERIAL PRIMARY KEY,
    user_name VARCHAR(40) NOT NULL REFERENCES users(user_name) ON DELETE CASCADE,
    preference_key VARCHAR(50) NOT NULL,
    preference_value VARCHAR(200) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_name, preference_key)
);

-- Create trigger to update updated_at when a preference is updated
CREATE OR REPLACE FUNCTION update_preference_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_preference_timestamp
BEFORE UPDATE ON user_preferences
FOR EACH ROW
EXECUTE FUNCTION update_preference_timestamp();

-- Grant permissions to chemuser
GRANT SELECT, INSERT, UPDATE, DELETE ON user_preferences TO chemuser;
GRANT USAGE, SELECT ON SEQUENCE user_preferences_id_seq TO chemuser;

-- Insert initial data for user 'john'
INSERT INTO user_preferences (user_name, preference_key, preference_value) VALUES
('john', 'building', 'building 202'),
('john', 'lab_room', '120');

-- Create index for faster lookups
CREATE INDEX idx_user_preferences_user_name ON user_preferences(user_name);
#1212
