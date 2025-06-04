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
- New containers should get their own CloudFormaton yaml files with the patterhn "ecs-<name>-environment.yam"

Reference for Docker:
- Base image for all containers public.ecr.aws/docker/library/python:3.13.3

Other General Requirements:
- All pages should use the styles.css file now available from the nginx container

1) Let's create a new module for recipes
    - Use the main module as a template
    - The primary page will be a place holder with just a title: Recipe Management and a brief description
    - The inventory-taker roll should not see this menu item in the left navigation nor should they be able to access this module
        This needs to be changed in the shared-template module
        The recipes module should also check roll and bounce anyone with the inventory-taker role back to the main page
    - Like main, the left navigation and header should both come from shared-templates
    - For now no additional functionality should be implemented

2) Let's create a new module for reports
    - Use the recipes module as a template
    - The primary page will be a place holder with just a title: Reporting and a brief description
    - All users should have access to this module
    - Like recipes, the left navigation and header should both come from shared-templates
    - For now no additional functionality should be implemented
    - Make sure you update shared-templates with the navigation change
    - Make sure you add the prefix /reports to the URL
    - When you create a CloudFormation script for reports please follow the resource naming conventions from recipes
    - Make sure you update the scripts for building and deploying for both local and ECS
    - When you build the testing we only need the following tests:
        Verify a technician can login and navigate to the reports page
        Verify if you navigate to the page without logging in, you are thrown back to the login page

3) Let's implement a new module that serves the api key to all the containers
    - Look at source/main/api_client.py for reference
    - The new module should pull the key from Parameter store and save it in a variable
    - It should have a get key method that can be called to get the api key
    - The module should only be callable by other containers not by a user
    - Use a security group to add extra protection for the container
    - Make sure this approach still works for running locally where we don't use the key
    - Make sure you update all the shell scripts for building and deploying locally and into AWS
    - Use the prefix /secrets to refer to it
    - Create a CloudFormation script to deploy the new container
    - Do not build test scripts
    - Do not change any other modules at this time.