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

Items:
1) Refactor backend
    The backend.py file is getting too big.  Let's look at refactoring it into several files based on the types of calls.  Propose a possible solution but don't make and changes.
2) Implement app key security
    The backend module should implement api key security.  It should be enabled when deployed to ECS but not enabled when deploying locally via docker compose.  For the ECS environment store the key in Parameter Store.  Add the creation of the parameter to the initial-environment.yaml file.
3) Generate better chemical data
    Generate an SQL file for PostgreSQL to update the database
    Add more fields to the chemicals table
        id (existing)
        chemical name (existing)
        chemical description
        unit of measure (existing)
        cas number
        chemical formula
        molecular weight
        physical state
        signal word
        hazard classification
        sds link
    Create a brand new list of chemicals that have all these fields
        At least 50 chemicals
        Make sure all the SDS links come from the same source
        Make this list into insert statements for the updated chemicals table
    Using the locations table randomly assign inventory to all the locations
        There should be no fewer than 5 chemicals in any one location and no more than 20
    At this point, do not make any code changes to the applications.
4) Create an AWS application architecture diagram using draw.io
    - Place the two user types (Users, Developers) at the top
    - Below that have the Intranet Subnets
        In this section have the Application Load Balancer with its Certificate for HTTPS
        Also have the Network Load Balancer for database access
    - Below that have the Private Subnets
        Include the Lambda function used for email notifications
        Include the Fargate environment
            It should be represented as its own large box
                Inside the box show each of the containers running in it
    - At the bottom have a section for other AWS resources: Supporting Services
        Include ECR, Secrets Manager, Parameter Store and SNS
    When creating this diagram do not iterate over the file more than 5 times
    Do not wrap the metadata tag with CDATA
5) Enhance the search page
    Let's add the following columns to the search results: cas number, chemical formula, signal word, physical state
        If the screen isn't wide enough, then show a horizontal scroll bar
    Add the following filter to the search page: hazard classification
        It should be a partial match filter
    The column headings used to sort by the column.  They don't work anymore.  Please fix this.
6) Chemical details page
    Let's add a chemical details dialog as part of the search container
    It should come up when the user click on the chemical name in the search results
    When you close the chemical details dialog, it should return you to your search where you left off
    The details page should show all the fields from the chemicals table (except for id) plus the location fields (except locations id)
    The quantity and reorder quantity fields should be grouped together with two buttons
        The buttons are: Receive material, Check out material
        These buttons will be implemented later
    At the top right there should be a Close button to close the dialog
    The sds link field should be shown as a hyperlink that opens the connected document in a new window
7) Update to chemical details dialog
    When the user clicks on the receive material button a small dialog should popup to allow the user to enter a quantity
        It should have an Add and a Cancel button
        Hitting cancel will close the small dialog
        Hitting Add will add the new quantity to what is already saved in the current record and save it into the database
            After that the small dialog should disappear
    The Check out material button should work similarly to the Receive material button
        The difference is the buttons on the small dialog should be Remove and Cancel
        The Remove button should take the quantity entered and subtract it from what is currently stored in the record then update the database
8) Add Prometheus
    I'd like to add Prometheus to my application using AWS
    - Add a workspace in the cf01-initial-env-setup.yaml file
        Create a CloudWatch log called: /chemtrack-prometheus
    - Add the prometheus client to all the flask and fastapi containers: admin, backend, login, main, search, shared-templates
        Make sure to add the name of the container to the setup
        Use port 5000 for metrics
    - Add a separate container to collect and send all the metrics to CloudWatch
9) Refactor Search
    Let's refactor the search page to move the chemical details dialog out into its own page
    - Keep the chemicals details as part of the search module, give it its own template
    - Use calls via search.py instead of using javascript to call the backend or other search functions
    - Give the new chemical details page a close button
    - When the user closes the details page return them to the search
    - The position of the scrollbar should be maintained
