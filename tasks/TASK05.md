Main Application Page

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
- All pages should use the CSS in the folder: /source/static
- Base the requirements.txt file for this image on the login page

Reference for Docker:
- Base image for all containers public.ecr.aws/docker/library/python:3.13.3

Other General Requirements:
- All pages should use the styles.css file now available from the nginx container

1) The mapping of the containers is wrong.  
    - Each container should have a URI that it responds to
    - All the traffic should go through the HTTPS listener and then directed to the containers based on URI
    - Containers that call one another need to use the same approach
    - What I think is missing are the listener rules for HTTPSListener
    - Here's the mapping
        main responds to /
        login responds to /login
        nginx responds to /static
        backend responds to /backend
        other pages will use the same pattern as login and backend

2) Create a deploy script for the containers using AWS CLI commands
    - Do not build
    - Assume the images have already been checked into ECR
    - All you have to do is call update service from ECS and force a deployment

Revisions:
    There were lots of edits here to get this working both locally and on the server.  I had to resort to hand coding to solve these issues.
