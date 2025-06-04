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

Description
    The header and left navigation on the main page needs to be used on all pages.  Currently it is being copied.  For example you can see this on the search page.
    This doesn't work because changes to the left navigation have to be implemented on every page.
    Please redesign this so the header and left navigation are pulled from one place (put it in the main process)
    It should be pulled into the other pages programmatically and/or by included files

Revisions:
- The new shared header and navigation are not being used by the search page.
- The problem is that the shared header and navigation should NOT be in main or search. They should be in shared-templates only and the content should be pulled from there.
- The main page now comes up without any header or navigation at all. They are blank. The center portion of the page however does come up.
- Still no header or navigation. The shared-templates process is running. Looking at the page source for the main page it appears that no code was included for the header or navigation into the generated html.
- I'm now getting the error header and navigation. I checked the shared-template process is running and I can access it using the http://localhost:8005/test url you provided.
- Main is now working however it appears that the search page is still pulling the header and navigation from local copies of the html files.  It should be using shared-templates like main.