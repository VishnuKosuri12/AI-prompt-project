Serving Static Content

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
- Base image for all containers public.ecr.aws/docker/library/python:3.13.2

1) Create an nginx server container to server static content to the other containers in this application
    - Use the image: public.ecr.aws/nginx/nginx:1.27-alpine3.21-slim
    - create it under the source/nginx folder
    - move the styles.css file from /source/static into the folder
    - create a basic copyright page for ChemTrack called copyright.html
        Owner: Covestro LLC
    - create an ECR repository for it in the existing initial-environment-setup.yaml file
    - the container should respond to the URI: /static
    - update the login container to find the styles.css file in this new container
    - update the build_and_run_local.sh file to run this container

2) Create the CloudFormation for the nginx container and place it in the ecs-environment.yaml file

Revisions
    Added #2