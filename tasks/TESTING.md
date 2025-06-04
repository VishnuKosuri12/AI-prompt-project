I'd like to build a testing harness to fully test the application functionality on a module level.  The tests should be runnable from a script and should be targeted at a locally deployed environment initially.  A script for testing the deployed application deployed can be done later.

1) Planning
    What is the best way to test the modules?
    What about testing using Selenium?
    Should we test deployed or each module separately?

    Don't generate any code, just give me ideas.
    Put your answer into a file and store it in the docs folder

2) Unit Testing -- Main
    - Let's start by setting up unit testing for the main module
    - Use the existing database connection
    - If making changes that affect the database, use specific rows for testing purposes

3) Unit Testing -- Search
    - Implement unit testing for Search module
    - Use the same pattern implemented for Main in item #2 above

4) Unit Testing -- Admin
    - Implement unit testing for the Admin module
    - Use the same pattern implemented for Main in item #2 above

5) Unit Testing -- Backend
    - Implement unit testing for the backend api module
    - Use a similar pattern implemented for Main in item #2 above

6) Integration Testing -- Backend
    - Use FastAPIs TestClient to test all of the endpoints in the backend module
    - Verify correct responses, status codes, and error handling

7) The testing is garbage.  We need to start over with backend.
    - If you are not connecting to the database, then the test is garbage.
    - All tests of backend must execute their database connections
    - We need to execute the tests against the database in an order that makes sense
    - Remove the old tests because they are no good
    - Let's rebuild the tests starting with the user related calls
    - Create these tests in a file called tests_user.py under the tests folder under backend.
        user roles
            Verify a successful return
            Verify the following roles are returned: administrator, inventory-taker, manager, technician
        users
            Verify a successful return
            Verify that there are at least 3 users returned
            Spot check the following users are present: john, oscar, bob
            Verify the following fields are returned: user_name, email_address, role_name
        create user
            Provide the following data:
                username: testuser
                password: testuser
                email: john.heaton@covestro.com
                role: technician
            Verify a successful return
        get user info
            Provide the username: testuser
            Verify a successful return
            Verify the fields using the data from the create user test case above
        update user
            Provide the user information from the create user function above but change the role to manager
            Verify a successful return
            Call get user info to verify the role is now manager
        delete user
            Provide the username: testuser
            Verify a successful return
            Call get user info for testuser and verify an error is returned since the user has been deleted

8) Let's redo the testing for preferences in backend similarly to item #7
    - Create these tests in the existing tests_user.py
    - Place these tests between update user and delete user in the file
    - Implement these tests
        delete user preferences:
            username: testuser
        update user preferences
            Use these parameters:
                username: testuser
                key: building
                value: building 202
                Verify success
            Repeat the test with these parameters:
                username: testuser
                key: building
                value: building 319
                Verify success
        get user preferences
            username: testuser
            Verify success
            Verify this preferences:
                username: testuser
                key: building
                value: building 319
        repeat delete user preferences test:
            username: testuser
            Verify success

9) Let's redo the testing for locations in backend similar to item #7
    - Create a new testing file called tests_location.py
    - Allow these tests to be called from run_tests.sh but allow them to be run separately be providing the parameter "locations"
    - Implement these tests
        building
            Call the buildings route
            Verify success
            Verify there are at least 3 buildings in the response
            Verify "building 202" is in the list
        lab rooms by building
            Call the labrooms route and pass it the building "building 202"
            Verify success
            Verify there are at least 3 lab rooms
            Verify one lab room is named "100"
        locations
            Call the locations route
            Verify success
            Verify there are at least 12 locations in the list
            Verify one of the locations matches:
                building_name: building 202
                lab_room_number: 120
                locker_number: 5
        create location
            Call the create route with the following values:
                building: "test 999"
                lab room: "900"
                locker: "9"
            Verify success
            Save the location id for the delete location test
            Make a call to the locations route
                Verify the new location is in the list returned
        update location
            Call the update route with these values:
                building: "test 999"
                lab room: "909"
                locker: "99"
            Verify success
            Make a call to the locations route
                Verify the location we just updated is in the list
        check location
            Call the check location route with these parameters:
                building: "building 202"
                lab room: "100"
                locker: "1"
                Verify that inventory exists
            Call check location route with these parameters:
                building: "test 999"
                lab room: "909"
                locker: "99"
                Verify no inventory is found
        delete location
            Call the delete location route give it the location id saved from the create location test
            Verify success

10) Let's redo the testing for chemical in backend similar to item #7
    - Create a new testing file called tests_chemical.py
    - Allow these tests to be called from run_tests.sh but allow them to be run separately be providing the parameter "chemical"
    - Implement these tests
        chemical search starts with name test
            Execute the chemsearch route with a partial name match of "Amm"
            Verify success
            Verify there are at least 5 rows in the results
        chemical search contains name test
            Execute the chemsearch route with a partial name match of "acid"
            Verify success
            Verify there are at least 20 rows in the results
            Check for the following chemical names in the results: Acetic Acid, Boric Acid, Nitric Acid
        chemical search by building
            Execute the chemsearch route with a building name of "building 202"
            Verify success
            Verify there are at least 20 rows in the results
        chemical search by building and lab
            Execute the chemsearch route with a building name of "building 202" and a lab room of "120"
            Verify success
            Verify there are at least 20 rows in the results
        chemical search by building, lab and locker
            Execute the chemsearch route with a building name of "building 202", lab room of "120" and locker of "2"
            Verify success
            Verify there are at least 5 rows in the results
        chemical search by hazard
            Execute the chemsearch route with a hazard classification partial match of "skin"
            Verify success
            Verify there are at least 30 rows in the results
        chemical search by hazard and building
            Execute the chemsearch route with a hazard classification partial match of "skin" and building of "building 404"
            Verify success
            Verify there are at least 10 rows in the results
        reorder notification
            Execute the reorder route
            Verify success
            Verify at least one chemical in the results
        chemical by inventory id
            Execute the chemical by inventory id route private it with an id of "165"
            Verify success
            Save the quantity for later tests
        update inventory add inventory test
            Execute update inventory with id = 165, quantity = 1.1, action = add
            Verify success
            Verify the new quantity is the saved quantity from the test above plus 1.1
        update inventory remove inventory test
            Execute update inventory with id = 165, quantity = 1.1, action = remove
            Verify success
            Verify the new quantity equal to the saved quantity from above

11) Let's redo the testing for auth in backend similarly to item #7
    - Create these tests in the existing tests_user.py
    - Place these tests just before delete user in the file
    - Implement these tests
        Execute the login route with the user we created "testuser" in #7 above
            Verify success
        Execute the update password route for "testuser"
            Change the password to "fred"
            Verify success
            Retry the login to make sure it works with the new password

12) Let's implement integration testing for our application
    - Let's do this by running the application locally using docker compose so that backend is running for api calls
    - We should use our existing database connection via backend
    - Do not modify backend or the backend tests setup without explicitly asking me
    - Create a tests folder under the module
    - Create a shell to run the tests and a python file called test_login.py for the pytest code
    - We will start with testing the login module for now
    - Here are the tests to implement
        Try login with user Sally and password sally
            Verify success
            Execute log out so we can run other tests
        Try login with user Sally and password fred
            Verify a failed login
        Try login with no user or password entered
            Verify a failed login
        Try login with user Sally but no password
            Verify a failed login
        Try login with no user but enter a password of sally
            Verify a failed login
    - Make sure you shutdown the docker compose environment at the end of the tests

13) Let's implement integration testing for the main module now
    - Use item #12 above as an example which was for the login module
    - Remove the old tests under main
    - Create a new python file called test_main.py for the pytest code
    - Here are the tests to implement
        Display the main page
            Login using user sally with password sally
            Verify the main page comes up after login
            Verify the following items on the left navigation: Home, Search, Reports, Recipes
            Verify in the center of the page Sally's user preferences for building and lab room are displayed
                The displayed value should be:
                    building: building 319
                    lab room: 100
            Verify in the top right is a button with her name on it "sally"
            Verify there is a logout button in the top right
        User account test -- basic
            Continuing from the test above, click on button in the top right with sally's name on it
            Verify the user account dialog comes up
            Verify the user name field contains: "sally"
            Verify the email address field contains: "john.heaton@covestro.com"
            Verify there is a change password link in the middle of the page
            Under user preferences verify the building is set to "building 319"
            Under user preferences verify the lab room is set to "100"
            Check that the reorder notification radio button is set to On
            Click the cancel button at the bottom
                Verify you are returned to the main page
        User account test -- update
            Continuing from the test above, click on button in the top right with sally's name on it
            Verify the user account dialog comes up
            Verify the user name field contains: "sally"
            Change the building preference to "building 404"
            Change the lab room preference to "105"
            Click save changes
            Verify the user has been returned to the main page
            Click again on sally's name in the top right
            Verify the user account dialog comes up
            Verify the building user preference is "building 404"
            Verify the lab room user preference is "105"
            Change the building back to "building 319"
            Change the lab room back to "100"
            Click save changes
            Verify the user has been returned to the main page
        User logout
            Continuing from the test above
            Click on the logout button
            Verify the user has been logged out and returned to the login page
            Verify the session has been cancelled
        User test for manager
            Login using user bob with password bob
            Verify the main page comes up after login
            Verify the following items on the left navigation: Home, Search, Reports, Recipes, Administration
            Click on the logout button
            Verify the user has been logged out and returned to the login page
        User test for administrator
            Login using user oscar with password oscar
            Verify the main page comes up after login
            Verify the following items on the left navigation: Home, Search, Reports, Recipes, Administration
            Click on the logout button
            Verify the user has been logged out and returned to the login page
