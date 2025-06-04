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

1) Let's add functionality to the reports module
    - The reports module is found in ./source/reports
    - We are going to need a new database table to store reports
        Call it: reports
        With these fields:
            report_id   should be a sequenced key
            report_name text field 50 characters max
            sql_query large text field
            parameters should be a json string of field names
        Create an sql script for creating the table and store it in the scripts folder
        Here is our first report:
            Name: Inventory Totals
            Query:
                SELECT c.name, c.chemical_description, sum(i.quantity), c.unit_of_measure
                FROM chemicals c, inventory i
                WHERE c.id = i.id
                GROUP BY c.name, c.chemical_description, c.unit_of_measure
                ORDER BY c.name
            Parameters: None
        Add this to the sql file as an insert statement
        All calls to the database should be made through the backend module
    - On the reports page we should have a list of available reports pulled from the reports table
        Populate the list on the page template using Jinja
    - The user should be able to select a report and click a "Run report" button to generate the output
    - The report results should be displayed in a grid in the lower half of the page
    - The grid should be limited to 10 visible rows and have a scrollbar
    - Make sure you place all styles into a css file and have it served from the nginx module
    - Provide an export to Excel button next to the run button
        When the user clicks the export button it should generate html that is suitable to be read into Excel and place the results in the clipboard
    - Do not generate test cases for now
    - Use Jinja where possible instead of Javascript when building the page template

2)  Adding Prometheus
    - I'd like to add a Prometheus Workspace and monitor with Grafana
    - I've looked at the options and I think I'd like it done using ECS Service Discovery with an AMP scraper
    - Can you please create the CloudFormation code to add this to my application
    - scraping interval should be 15 seconds
    - The metrics path should be /metrics
    - If there is anything else I'm missing please ask