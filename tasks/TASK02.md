Database Setup

*** Refer to PLANNING.md for general guideance

Reference for CloudFormation:
- Each file should have an AppName parameter with the default value "chemtrack"
- AppName should be used as the prefix for all resource names
- Resource names should follow the pattern "<appname>-<resource type>"
- ARNs should be exported for use in other scripts
- name fields should use "-"
- name fields should not use "_"
- Default should be the last property of each parameter

1) Create a PostgreSQL RDS database using CloudFormation
    - Use PostgreSQL version 17.4
    - Characteristics:
        20 GB storage with 500 GB max
        Storage type gp3
        Database should be encrypted
        MultiAZ: false
        Backup window: 22:00-22:59 (make this a parameter)
        Backups should be retained for 14 days (make this a parameter)
        Preferred maintenance window Saturday 23:00-23:59 (make this a parameter)
        Instance class db.t4g.medium (make this a parameter)
        Enhanced monitoring should be disabled
        Connections should not be forced to use SSL by using the database parameter rds.force_ssl and setting it to zero
        The database should not be public
        Deletion protection should be turned off
    - Do not use custom resources
    - Do not use Lambda functions
    - Database should be located in the private subnets
    - The administrative user name and password are available in the secret chemtrack-db-admin-user

2) Create a network load balancer to allow developers access to the database
    - This should be done in a separate CloudFormation script
    - The load balancer should be located in the intranet subnets
    - The IP address of the database for the target group should be a parameter
    - TargetType should be ip
    - Targets property should be used in the TargetGroup to specify the ip
    - A DNS entry should be created for the NLB.  
        - The Name should be "ctrds.767397980456.aws.glpoly.net"
        - The resource record should be the dns name of the NLB
        - The type should be CNAME

3) Create an SQL file to setup the database structure
    - Create a database called chemtrack
    - A user should be created called "chemuser"
    - The password for chemuser should be passed as a parameter to the SQL script
    - It should have access to read, write, delete any records in the chemtrack database
    - The user "chemuser" should not have the ability to modify the database structure
    - Table Definitions are listed below:
        chemicals
            id: a sequentially generated number
            name: the name of the chemical up to 100 characters
            unit of measure: a character field of no more than 20 characters

        inventory
            id: a sequentially generated number
            chemical id: id from the chemical table
            quantity: a decimal field
            reorder quantity: a decimal field
            location id: a link to a record in the locations table

        locations
            location id: a sequentially generated number
            building name: a character field of up to 50 characters
            lab room number: an integer field with a value up to 9999 starting with zero
            locker number: an integer field with a value up to 999 starting with zero

        users
            user name: a character field up to 40 characters
            password: a character field with up to 200 characters
            email address which can be up to 120 characters long
            role name which is a reference to a role in the roles table
            rev_ts: a date/time field that gets updated any time the record is changed

        roles
            role name: name of the role with up to 50 characters
            role description: description of the role with up to 200 characters
    - Initial data for each table is listed below
        chemicals
            Generate a list of 10 different chemicals
        inventory
            Generate inventory in each of the locations in the locations table.  Have 1 or more for each location.
        locations
            building 202, 100, 1
            building 202, 100, 2
            building 202, 120, 1
            building 202, 120, 2
            building 202, 120, 5
            building 202, 140, 2
            building 202, 140, 5
            building 202, 140, 6
            building 202, 140, 9
        users
            leave the user table blank
        roles
            administrator
            technician
            inventory-taker
            manager

Revisions:

1) I'd like to rerun @/TASK02.md but only create the file for the network load balancer.