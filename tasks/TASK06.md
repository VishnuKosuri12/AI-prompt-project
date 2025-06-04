Search Page

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

General
    We are going to add a new container to the application called "search".  It will contain all the chemical search functions for the application.  It will share the same header and left navigation as the main page.

    Characteristics:
        Display name for the page: Chemical Search
        Upper portion of the page will have filters and a search button
        Lower portion of the page will have a Excel like grid to display the results

    Filters
        chemical name
        building name
        lab room number
        locker number

    Grid columns
        name, uom (for unit of measure), qty (for quantity), reorder qty (for reorder quantity), bld name (for building name), lab room (for lab rum number), locker (for locker number)
        Each column should allow sort ascending or descending
        The grid should have a scroll bar if there are more rows than 10
 
    Behavior
        Clicking on the search button will run the search by calling the /backend/search function in the backend api
        The default sort order for all search should be ascending order by chemical name
        The names of the chemicals in the grid should be links to "/details" using the chemical id. The details page will be implemented later.

    Technical
        URI for this process will be /search
        Code file for this process will be search.py
        Folder will be /source/search
        Use the requirements.txt file from login as a starting point
        The search is actually the combinatin of the inventory, chemical and location tables

Revisions:
    The default sort order will be handled by the query in the backend.  It should not be done in the python file.  Assume the sort order is handled by the backend.  Do not pass the sort to the backend.
    The Home button doesn't work on the search page.  It should take the user back to the main page.

New Requirements:
    1) The search page grid column headings should allow sorting ascending/descending by pressing the column name
        The sort should be implemented locally for column sorting
    2) The filter field values are lost when you hit the search button.  They need to be persistant as long as the user is logged on.  Meaning that even if the user goes to another pages, the filter values should reappear when the user returns to the search page.