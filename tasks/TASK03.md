Application Setup

*** Refer to PLANNING.md for general guidance

Reference for CloudFormation:
- Each file should have an AppName parameter with the default value "chemtrack"
- AppName should be used as the prefix for all resource names
- Resource names should follow the pattern "<appname>-<resource type>"
- ARNs should be exported for use in other scripts
- name fields should use "-"
- name fields should not use "_"
- Default should be the last property of each parameter
- Desired count for all services should be 1

Reference for Docker:
- Base image for all containers public.ecr.aws/docker/library/python:3.13.3


1) Create a CSS file for the overall look of the application
    - The application should have a modern look and feel with neutral colors
    - The file should be stored in the /source/static folder
    - The application should have a header section with the application name
    - The application should have a left navigation with items the user is allowed to access

2) Login page
    - Should be a full page with the login dialog centered on the page
    - The page URI should be "/login"
    - The page should be created as a container and stored in ECR under "chemtrack/login"
    - There should be fields for user name and password
    - The password field should not show what the user types
    - There should be a login button that attempts to login the user when pressed
    - The login page should always be shown if the user doesn't have an active session
    - The login process should involve a call to the backend api call /login passing the user name and password
    - The backend process will return either success or failure
    - If the backend returns a success, a user session should be created and maintained for the user and the user should be forwarded to the main page
    - If the backend returns a failure, then a message in red should appear below the fields to indicate the user name or password are invalid
    - If the user comes to the login page but already has a valid session, then they should be redirected to the main page

3) Backend API
    - Create an API container using FastAPI
    - The api URL should be "/backend"
    - The api should have a connection to the PostgreSQL database using the user "chemuser"
    - The database definition can be found in "/scripts/setup_database.sql"
    - The url for the database is stored in secrets manager
    - Available API calls
        URI: /login
            Takes the user name and password as arguments
            Use hashlib to create a hash of the password
            - use SHA256
            Compares those values to the values stored in the user table
            Returns true if they match or false if they don't
            Should be implemented as a parameterized query
        URI: /createuser
            Take the user name, password, email address and role as parameters
            Check to make sure the user doesn't already exist, if so return an error
            Use hashlib to create a hash of the password
            Store the fields in the user table
            Return true if successful and an error if not
            Should be implemented as a parameterized query
        URI: /updateuser
            Take the user name, password, email address and role as parameters
            Check to make sure already exists, if not then return an error
            Use hashlib to create a hash of the password
            - use SHA256
            Update the fields in the user table
            - user name can not be changed
            Return true if successful and an error if not
            Should be implemented as a parameterized query
        URI: /chemsearch
            Runs a query against the inventory
            Parameters: name, building name, lab room number, locker number
            Columns: id, name, unit of measure, quantity, reorder quantity, building name, lab room number, locker number
            Details:
                The name and building name fields can be partial matches
                The inventory, chemicals and locations tables must be joined
                The request parameters should be sent in json format
                The results should be returned in json format

4) Create the ECS environment with CloudFormation
    - ECS cluster should be in the private subnets
    - An application load balancer for the cluster should be in the intranet subnets
    - A DNS entry should be created for the application: "chemtrack.767397980456.aws.glpoly.net"
    - Initially it should direct all traffic to the login page
    - A certificate was created for HTTPS traffic already in the initial-environment-setup.yaml file
    - Access logs should be enabled for the ALB.  They should be stored in the access logs bucket
    - Service naming convention: <appname>-<page name>-service
    - Container naming convention: <appname>-<page name>-container
    - Task definition characteristics:
                aws logs should be turned on and retained for 7 days
                CPU: 256
                Memory: 512

5) Create a bash script to build and check into ECR the containers


Revisions

1) I've added another task to @/TASK03.md.  Please implement #5
2) When I try to login and hit the login button I get the message "Could not connect to authentication service".  I looked at the log for the backend and it doesn't appear that it was called.
3) Manually worked out getting local environment running, database connection issues, and had cline rework main.py to switch it to psycopg2