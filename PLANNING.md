
I'm trying to build a chemical tracking application.  There will be multiple users in many labs.  Each lab has its own list of chemicals.  The users need to be able to check out quantities of chemicals, check in new quantities when they are purchases, reconcile inventory periodically, search for chemicals by their characteristics, mark a chemical for deletion when it is no longer available.

General guidelines:
    The application will be created in an AWS account.
    It should use ECS Fargate
    It will store data in PostgreSQL
    Each page should be its own container
    Container code will be written in Python with Flask and run with Gunicorn
    APIs should be written in Python using FastAPI
    An existing VPC will be used in the AWS account

Authentication:
    The application should have a login page
    After login the user should have a session
    All resources should be protected to only allow requests from users with a session, if not the user should be returned to the login page
    Login will be with a user name and password which will be stored in a secret in Secrets Manager as key/value pairs

Reference information:
    VPC id: vpc-019e35a7f8ca205e5
    Private subnets: subnet-08de8ae010ebfa1f3, subnet-0205ddf1053073b5c
    Intranet subnets: subnet-0ee959776d1683aa5, subnet-07257f93f815ce77c
    These should be passed as parameters into CloudFormation where needed

Database:
    The application should store data in PostgreSQL
    Any SQL scripts for creating or updating the database structure should be written in sql to be run with the psql tool
    The database will sit in the private subnets
    For developer access a network load balancer in the intranet subnets will be created
    The application will have a special database user "chemuser" who's credentials will be stored in Secrets Manager
    Do not use a mock database connection for local.  Use the normal database connection.

Container environment:
    The application will use ECS Fargate
    It should be placed in the private subnets
    An application load balancer in the intranet subnets will be used for access
    Traffic to the ALB should be HTTPS
    HTTP traffic to the ALB should be redirected to HTTPS
    Traffic out of the ALB to ECS will be HTTP
    Each page of the application will be created as a separate container and service in ECS

Backend API environment:
    The application will have a backend api for communicating with the database
    It should be written in Python using FastAPI
    It will have its own container and service in ECS
    The API should be secured so that only calls from other containers are allowed
    
Project layout information:
    The file build_and_push.sh is designed to build all the containers and push them to ECR
        It needs to be maintained when there are changes or new containers added
    The file deploy_containers.sh deploys a container to ECS from ECS
        It takes the container name as an argument
    The file local_go.sh builds all the containers and deploys them locally into docker with no arguments
        If you specifiy a container name then it only builds and deploys the specified container
        It uses a hardcoded network "chemtrack-network"
        URLs are customized to run in the local environment
        Calls to request.post require the local URL to reference the docker name for the container instead of "localhost"
        It needs to be maintained when there are changes or new containers added
