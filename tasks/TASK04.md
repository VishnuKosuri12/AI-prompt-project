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

1) Main page
    - The main page of the application is the home page for the application
    - The page should be created as a container and stored in ECR under "chemtrack/main"
    - Should have its own CloudFormation file called ecs-process-main.yaml
    - It should be the page that responds to the application URL
    - It should first check to see if the user has an active session, if not the user should be forwarded to the login page
    - The main page consists of a header and a left navigation
    - The header contains the application name and a logout button at the far right
        Clicking on logout should invalidate the user's session and return them to the login page
    - The left navigation shows the various funtions of the application.  Each link takes the user to a new page/container.
    - Below is the list of left navigation items:
        Home: takes the user back to the main page
            - all users can see this link and access this page
        Search: takes the user to a chemical search page
            - all users can see this link and access this page
            - the link will go to a module URI /search to be developed later
        Reports: takes the user to a reporting page
            - all users can see this link and access this page
            - the link will go to a module URI /reports to be developed later
        Recipes: take the user to a page for managing chemical recipes
            - the link will go to a module URI /recipes to be developed later
            - only technicians, managers and administrators can see this link
        Admin: takes the user to the administration page
            - only administrators and managers can see this link and access this page
            - the link will go to a module URI /admin to be developed later

2) Add the company logo to the main page of the application
    - The file is stored in static under the name covestro.png
    - Place it in the top left corner of the header
    Revision:
        The image covers the entire page. Please limit it to a square in the top left corner. It should be no taller than the header.
        That didn't work. The image still covers most of the page.
        Looks better but the image should be to the left of the application name "ChemTrack"
        Made some manual changes to fix