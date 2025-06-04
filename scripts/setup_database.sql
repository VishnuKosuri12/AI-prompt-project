-- Setup database structure for ChemTrack application

-- Create database
CREATE DATABASE chemtrack;

-- Connect to the database
\c chemtrack

-- Create user with appropriate permissions
CREATE USER chemuser WITH PASSWORD ':mypass';
-- Note: The actual password will be retrieved from AWS Secrets Manager in production

-- Create tables
CREATE TABLE chemicals (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    unit_of_measure VARCHAR(20) NOT NULL
);

CREATE TABLE locations (
    location_id SERIAL PRIMARY KEY,
    building_name VARCHAR(50) NOT NULL,
    lab_room_number INTEGER NOT NULL CHECK (lab_room_number >= 0 AND lab_room_number <= 9999),
    locker_number INTEGER NOT NULL CHECK (locker_number >= 0 AND locker_number <= 999)
);

CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    chemical_id INTEGER NOT NULL REFERENCES chemicals(id),
    quantity DECIMAL NOT NULL,
    reorder_quantity DECIMAL NOT NULL,
    location_id INTEGER NOT NULL REFERENCES locations(location_id)
);

CREATE TABLE roles (
    role_name VARCHAR(50) PRIMARY KEY,
    role_description VARCHAR(200) NOT NULL
);

CREATE TABLE users (
    user_name VARCHAR(40) PRIMARY KEY,
    password VARCHAR(200) NOT NULL,
    email_address VARCHAR(120) NOT NULL,
    role_name VARCHAR(50) NOT NULL REFERENCES roles(role_name),
    rev_ts TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create trigger to update rev_ts when a user record is updated
CREATE OR REPLACE FUNCTION update_rev_ts()
RETURNS TRIGGER AS $$
BEGIN
    NEW.rev_ts = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_user_rev_ts
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_rev_ts();

-- Grant permissions to chemuser
GRANT CONNECT ON DATABASE chemtrack TO chemuser;
GRANT USAGE ON SCHEMA public TO chemuser;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO chemuser;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO chemuser;

-- Ensure future tables get the same permissions
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO chemuser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO chemuser;

-- Insert initial data

-- Locations
INSERT INTO locations (building_name, lab_room_number, locker_number) VALUES
('building 202', 100, 1),
('building 202', 100, 2),
('building 202', 120, 1),
('building 202', 120, 2),
('building 202', 120, 5),
('building 202', 140, 2),
('building 202', 140, 5),
('building 202', 140, 6),
('building 202', 140, 9);

-- Chemicals
INSERT INTO chemicals (name, unit_of_measure) VALUES
('Acetone', 'L'),
('Ethanol', 'L'),
('Methanol', 'L'),
('Hydrochloric Acid', 'L'),
('Sodium Hydroxide', 'kg'),
('Sulfuric Acid', 'L'),
('Toluene', 'L'),
('Chloroform', 'L'),
('Acetic Acid', 'L'),
('Hydrogen Peroxide', 'L');

-- Inventory (at least one item for each location)
INSERT INTO inventory (chemical_id, quantity, reorder_quantity, location_id) VALUES
(1, 5.0, 2.0, 1),
(2, 3.0, 1.0, 2),
(3, 2.5, 1.0, 3),
(4, 1.0, 0.5, 4),
(5, 2.0, 1.0, 5),
(6, 1.5, 0.5, 6),
(7, 3.0, 1.0, 7),
(8, 2.0, 1.0, 8),
(9, 4.0, 1.5, 9),
(10, 1.0, 0.5, 1),
(1, 2.0, 1.0, 2),
(2, 3.5, 1.5, 3);

-- Roles
INSERT INTO roles (role_name, role_description) VALUES
('administrator', 'Full system access with ability to manage users and system configuration'),
('technician', 'Can manage chemicals and inventory'),
('inventory-taker', 'Can update inventory quantities and locations'),
('manager', 'Can view reports and approve chemical orders');

-- Users table is left empty as per requirements
