Rearchitect navigation Page

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
1) Create shortcut links on the login page to make testing quicker
    - Create the links below the login button
    - Each link should fill in the user name and password field then submit the page
    - the user names and passwords are identical
    - Create the following links for these users: sally, john, bob, oscar

2) Handle password resets
    - Add a column to the users table called "pswd_reset" which is either Y or N with the default being N
    - Generate this database change as a psql script that can be run manually.
    - Update the user account dialog so that when the user clicks on the "Change Password" link it does the following:
        - sets the pswd_reset field for that user in the database to Y
        - logs the user out and returns them to the login page
    - Update the login dialog box as follows:
        - When a user logs in, after validation, the paswd_reset flag will be checked, if it is a Y the user will be presented with the change password dialog
    - Create a new change password dialog box
        - Create it as a separate route under the login process container
        - The page should have the following characteristics:
            Title: ChemTrack
            Subtitle: Password Change
            A field for the user to enter their existing password
            A field for the user to enter a new password
            A field for the user to reenter their new password
            A button labelled "Change" to submit the form
            The form should verify that the new password and the reentered new password are identical
            An error should be displayed if they are not and the form can't be submitted
        - Submitting the form will first validate the user name and password like login
            - The password should be run through the hash_password function
            - Then update the user table with the new password.
            - The  user should then be returned to the login page to try to login again with the new password

3) Expiring passwords
    - Need to add a field last_reset (date field) into the users table to hold the last date the user updated their password
        For existing users set the date to one week ago
    - When a user logs on, after validation, check the last_reset date, if it is older than 3 days:
        Set the pswd_reset field to Y in the database
        Force the user to the password change screen

4) Low inventory warning
    - New feature that notifies users by email when the quantity of any chemical in their lab falls below the reorder quantity
    - A new preference should be added called: Reorder notification
    - The preference should be added to the user account page so it can be changed
    - On the user account page, it should be represented as a radio button with the default as off for new users
    - It should be set to off initially for all existing users
    - Create an SNS topc called chemtrack-reorder-sns
    - When the user account page is saved, and the user choses to get the notification, then they should be added to the sns topic
    - If a users changes their preference from yes to no then they should be removed from subscribing to the sns topic
    - Add an api call to backend (name: /backend/reorder_notif) that returns a list of all users that should be notified
        The query should look at all chemicals from all labs
        The query should determine if any chemical quantity is below reorder quantity
        A user should only be notified if their user preferences associate them with that lab
        The query should join the user preference and the location tables to get this information
    - A lambda function triggered once per day at 3pm should make the call to the new backend api /backend/reorder_notif
        The lambda function should then send an email to each person
        The email information should be:
            title: Chemtrack -- reorder alert
            body: The following chemical(s) need to be reordered
        The body of the email should list all chemicals that need to be reordered for the lab the user is associated with
        Only one email should be sent per person
    - Create a new cloudformation script for the AWS resources and call it sns-reorder-email.yaml

5) Administration section
    - Create a new ECS container for administration
    - Using a new CloudFormation file
    - The route for accessing it should be /admin
    - It should appear as a link on the left naviagation with the title Administration
    - It should only be visible for managers and administrators
    - If a user tries to access a route from the administration container who isn't a manager or administrator they should be returned to the main page
    - Once you click on Adminstration a submenu should appear on the left navigation indented under Adminstration
        The submenu should contain the following links:
            Users
            Locations
    - User management
        Clicking on users should open the user management page
        It should be contained in the administration container and have the route /admin/users
        The user management page should be divided into sections
        The upper left portion should have a scrolling list box of all the users in the system
            It should have the following fields: name, email address, role
        The lower left portion should have fields for a selected user
            The fields should be: name, email address, role, building and lab room
            It should be possible to change these fields
            Clicking on a name in the list above should populate the fields in this section
        On the right side of the page should be a create user button, save changes, cancel changes
        Create user
            The create user button should:
                clear the list section in the top left list box
                blank the fields in the bottom left
                enable the save changes button
                enable the cancel changes button
                disable selecting users from the top left
            Clicking save changes will validate that all the fields have been filled then create the user with the password set to 'fred'
                Missing fields should be highlighted to show the user what they still have to fill in
            Clicking the cancel changes button will clear the fields in the lower left and reenable selection of users from the top left
        Select user
            Selecting a user from the top left list box should populate the fields in the lower left with the user values
            If the user modifies one of the fields then the save changes and cancel changes buttons should be enabled
                Also disable the selecting of users from the top left until changes have been saved or cancelled
        Cancel Changes
            Clicking on cancel changes when it is enabled will blank the fields in the lower left section
            Enable selection in the user list in the top left
        Save Changes
            Save changes should validate that all the fields have been filled in
            If not, then fields with missing data should be highlighted
            Changes should then be saved to the database
            The save and cancel changes buttons should be disabled
    - Location Management
        Location management should work similarly to user management
        The list box should show all the locations in the system ordered by building, room and locker
        The list box should have filters above it for building and room
        They should automatically filter the contents of the list box as the user types
        The building field should be a partial match so typing "20" should match "building 202"
        The buttons on the right should be create location, save changes, cancel changes and work like the ones in user management
        Additionally there should be a delete location button
            The button should be active only when an existing location is selected in the list box
            When this button is pressed it should make a call to the database to ensure there is no inventory at that location
                If there is no inventory, then it should proceed with deleting with the location
                If there is inventory, it should notify the user with an alert
    Revisions
        Many revisions to get the system to work
        Let's enhance the left navigation for administration
            Currently the top level items get a highlight when the mouse is over them.  Add this to the submenu items
            Currently the top level items get a highlight when it is selected.  Add a highlight for the submenu items as well when one is selected.
            Add icons to the submenu items to give them a similar look and feel to the top level menu items.