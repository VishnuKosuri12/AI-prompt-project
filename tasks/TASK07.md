Enhancement Page

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

Enhancements
1) We need to enhance our user information
    - Create a table for storing user preferences in a key value pair arrangement (use a .sql file to be run manually)
        Include in this sql file an entry for user 'john'.  Set his building to 'building 202' and his lab room to '120'
    - Add a call in the backend for retreiving the user preferences (login process should use this call)
    - On login the user's preference should be loaded into the session
    - Pages that need the preferences can access them from the session
    - Preferences:
        user building:   same as building_name field in location
        user lab room:   same as the lab_room_number field in location

2) More enhancements to the search page
    - Implement drop down lists for the fields on the search page
        Building name should be a drop down list
            A query should be added to the backend to pull a unique list of buildings from the locations table and sort them ascending
            The filter field on the search page should be replaced with a drop down list containing those values for the user to pick from
            The default value should be blank
            The new URI for backend should
        Lab room number should be a drop down list
            A query should be added to the backend to pull a unique list of lab rooms from the location table based on the selected building
            The drop down should be sorted them ascending
            If no building is selected, then the lab room should be an empty drop down list
            If the lab room is blank, then the locker number should also be blank
            Changing the building filter should blank the lab room drop down
        The user preferences should still work for these fields
    - Allow partial name matches for the chemical name
        The user should be able to enter a partial name match into the chemical name field and the search should find it
        Should work like a "contains" operation.  The string provided could be anywhere in the name

3) User account page
    - Create a page as part of the main process to allow the user to see and modify personal characteristics
    - It should be part of main and not a separate Docker file
    - It should popup like a dialog in front of the current applicaton page
    - In the top right where the user name appears is where we will add a link
        Add an icon to the left of the name that represents the user account
        Make both the icon and the user name an active link that will bring up the user account page
    - The user account page should show the following
        title: User Account
        user name (read only)
        email address (editable)
        user preferences (editable)
        a link to change the user's password (just a place holder for now)
        Save and cancel buttons

    Revisions:
        On the new user account page, the email address field is blank.  It should be pulling from the users table.
        The email address is being erased when the user hits cancel from the user account page.  It should not make changes on cancel.
