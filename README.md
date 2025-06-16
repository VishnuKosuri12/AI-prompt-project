# ChemTrack Application

ChemTrack is a chemical tracking application designed for multiple users across many labs. Each lab maintains its own list of chemicals, and users can check out quantities, check in new purchases, reconcile inventory, search for chemicals by characteristics, and mark chemicals for deletion when no longer available

## Project Structure

- `/infrastructure`: Contains CloudFormation templates for AWS infrastructure
- `/scripts`: Contains database scripts for PostgreSQL
- `/source`: Contains Python code for the application containers

## Infrastructure

The application is deployed on AWS using the following services:

- **ECS Fargate**: For containerized application components
- **PostgreSQL**: For data storage
- **ECR**: For container image repositories
- **Secrets Manager**: For storing sensitive information
- **S3**: For project files and access logs
- **ALB**: For routing traffic to the application containers
- **NLB**: For developer access to the database

## Architecture Diagram

An AWS application architecture diagram is available in the `aws-architecture-diagram.drawio` file. This diagram illustrates the complete architecture including:

- User access (Users and Developers)
- Network layout (Intranet and Private Subnets)
- Application components (ALB, NLB, ECS Fargate with all containers)
- Supporting AWS services (ECR, Secrets Manager, Parameter Store, SNS)

To view the diagram:
1. Open [diagrams.net](https://app.diagrams.net/)
2. Select "Open Existing Diagram"
3. Open the `aws-architecture-diagram.drawio` file from your device

For detailed information about the diagram, refer to `aws-architecture-diagram-README.md`.

## CloudFormation Templates

### Initial Environment Setup (`infrastructure/initial-environment-setup.yaml`)

This template sets up the initial environment for the ChemTrack application:

**Parameters**:
   - `AppName`: Name of the application (default: "chemtrack")
   - `CertificateGlpolyCatalogVersion`: Version of the SSL Certificate catalog product

**Resources**:

1. **Secrets Manager Secrets**:
   - `chemtrack-db-admin-user`: Database admin user credentials (username: postgre)
   - `chemtrack-db-app-user`: Database application user credentials (username: chemuser)
   - `env-vars`: Environment variables for the application

2. **ECR Repositories**:
   - `chemtrack/main`: Main application container
   - `chemtrack/search`: Search functionality container
   - `chemtrack/backend`: Backend API container
   - `chemtrack/details`: Details page container
   - `chemtrack/login`: Login page container
   - `chemtrack/nginx`: Static content server container

3. **S3 Buckets**:
   - `chemtrack-project-bucket`: For project files (private, encrypted)
   - `chemtrack-access-logs`: For access logs (private, encrypted)

4. **SSL Certificate**:
   - Creates an SSL certificate using AWS Service Catalog
   - Certificate is provisioned with the name "certificate-{AppName}"
   - Certificate ID is exported as "{AppName}-certificate-id" for use in other templates

### Database Setup (`infrastructure/database.yaml`)

This template creates a PostgreSQL RDS database for the ChemTrack application:

- PostgreSQL version 17.4
- 20 GB storage with 500 GB max (gp3 storage type)
- Database encryption enabled
- Backup window: 22:00-22:59 (configurable parameter)
- Backups retained for 14 days (configurable parameter)
- Maintenance window: Saturday 23:00-23:59 (configurable parameter)
- Instance class: db.t4g.medium (configurable parameter)
- Located in private subnets
- Not publicly accessible
- SSL not forced (using rds.force_ssl parameter set to 0)
- Deletion protection disabled

### Network Load Balancer (`infrastructure/database-nlb.yaml`)

This template creates a network load balancer to allow developer access to the database:

- Located in intranet subnets
- Forwards traffic to the RDS database
- Creates a CNAME DNS record using the db_url from the env-vars secret that points to the NLB's DNS name

## Deployment

To deploy the initial environment:

```bash
aws cloudformation create-stack --stack-name chemtrack-initial-env \
  --template-body file://infrastructure/initial-environment-setup.yaml \
  --parameters ParameterKey=AppName,ParameterValue=chemtrack \
  ParameterKey=CertificateGlpolyCatalogVersion,ParameterValue=v1 \
  --capabilities CAPABILITY_IAM
```

Note: Replace `v1` with the actual version of the SSL Certificate catalog product.

## Application Components

The application consists of multiple containers, each serving a specific purpose:

- **Main**: Main application interface
- **Search**: Chemical search functionality
- **Backend**: API for database communication using FastAPI
- **Details**: Chemical details page
- **Login**: User authentication

### Container Mapping and URI Routing

The application uses an Application Load Balancer (ALB) to route traffic to the appropriate containers based on URI paths:

- **Main Container**: Responds to the root path (`/`)
- **Login Container**: Responds to `/login`
- **Backend Container**: Responds to `/backend`
- **Nginx Container**: Responds to `/static`
- **Search Container**: Responds to `/search`
- **Admin Container**: Responds to `/admin`
- **Recipes Container**: Responds to `/recipes`

All traffic goes through the HTTPS listener on the ALB, which then directs requests to the appropriate container based on the URI path. This routing is configured using listener rules in the CloudFormation template (`infrastructure/ecs-environment.yaml`).

The containers communicate with each other using these URI paths, not by directly addressing each other. For example, the login container redirects to the main container by using the path `/`, and the main container redirects to the login container by using the path `/login`.

### Login Container

The login container provides user authentication functionality:

- Located at `/source/login`
- Built with Flask and Uvicorn (using WsgiToAsgi adapter)
- Provides a login page at the `/login` URI
- Authenticates users against the backend API
- Creates and maintains user sessions
- Loads user preferences into the session during login
- Redirects to the main application after successful login
- Uses static files (CSS, JS) from the `/source/static` directory

### Main Container

The main container provides the main application interface:

- Located at `/source/main`
- Built with Flask and Uvicorn (using WsgiToAsgi adapter)
- Provides the main application page at the root URI (`/`)
- Checks for active user sessions and redirects to login if none exists
- Displays user preferences (building and lab room) from the session
- Features a header with company logo, application name, and logout button
- Includes a left navigation panel with role-based access control:
  - Home: Visible to all users
  - Search: Visible to all users
  - Reports: Visible to all users
  - Recipes: Visible only to technicians, managers, and administrators
  - Administration: Visible only to administrators and managers, with submenu for Users and Locations when selected
- Uses static files (CSS) from the nginx container
- Logout functionality redirects to the login service using the LOGIN_URL environment variable

**Note**: The login container uses the `asgiref.wsgi.WsgiToAsgi` adapter to make the Flask WSGI application compatible with Uvicorn's ASGI server. This is necessary because Flask is a WSGI framework while Uvicorn is an ASGI server.

### Search Container

The search container provides chemical search functionality:

- Located at `/source/search`
- Built with Flask and Uvicorn
- Provides a search page at the `/search` URI
- Pre-fills search form with user preferences (building and lab room) from the session
- Features a search form with filters for chemical name, building name, lab room number, and locker number
- Displays search results in a grid with columns for name, UOM, quantity, reorder quantity, building name, lab room, and locker
- Allows sorting of results by any column in ascending or descending order
- Chemical names in the results are links to the details page
- Calls the backend API's `/chemsearch` endpoint to perform searches
- Uses static files (CSS) from the nginx container
- Shares the same header and left navigation as the main page
- Home button in the navigation redirects to the main page using the MAIN_URL environment variable

**Static Files**: The login container's Dockerfile copies the static files from `/source/static` into the container at `/app/static`. The Flask application is configured to serve static files from this directory using `static_folder="static"`. This ensures that CSS and JavaScript files are properly served when the application is running.

**Local Development**: When running the login container locally, it will attempt to connect to the backend API at `http://localhost:8000` by default. To override this, set the `BACKEND_API_URL` environment variable to the appropriate backend API URL.

## Local Development

For local development and testing, you have several options to run the application:

### Option 1: Docker Compose (Recommended)

Use the provided `docker-compose.yml` file to run all application containers:

```bash
# Run the application using the convenience script
./run_docker_compose.sh

# Or run directly with Docker Compose
docker compose up

# Run in detached mode
docker compose up -d

# To stop the application
docker compose down
```

This will:
1. Build all containers (backend, login, main, nginx, search, shared-templates)
2. Create a Docker network for container communication
3. Run the containers with appropriate port mappings and environment variables
4. Set up health checks to ensure services start in the correct order

With this option, you can access:
- Backend API: http://localhost:8000
- Login Page: http://localhost:8001/login
- Main Page: http://localhost:8003
- Search Page: http://localhost:8004/search
- Static Content: http://localhost:8002/static
- Shared Templates: http://localhost:8005/shared-templates

#### Setting up AWS Credentials for Docker Compose

The backend service requires AWS credentials to access AWS services like Secrets Manager for database credentials. You can provide these credentials in two ways:

1. **Environment Variables**: Set the following environment variables before running Docker Compose:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_SESSION_TOKEN=your_session_token  # if using temporary credentials
   export AWS_REGION=us-east-1  # defaults to us-east-1 if not specified
   ```

2. **.env File**: Create a `.env` file in the same directory as the `docker-compose.yml` file with the following content:
   ```
   AWS_ACCESS_KEY_ID=your_access_key
   AWS_SECRET_ACCESS_KEY=your_secret_key
   AWS_SESSION_TOKEN=your_session_token  # if using temporary credentials
   AWS_REGION=us-east-1  # defaults to us-east-1 if not specified
   ```
   
   A template `.env.example` file is provided that you can copy and modify:
   ```bash
   cp .env.example .env
   # Edit .env with your actual credentials
   ```

The `run_docker_compose.sh` script will check if AWS credentials are set and provide guidance if they are missing.

### Option 2: No-Volume Docker Compose

Use the provided `run_novolume.sh` script to run both the backend and login containers using a Docker Compose setup that avoids app volume mounts:

```bash
# Make the script executable (if not already)
chmod +x run_novolume.sh

# Run the services
./run_novolume.sh
```

This script will:
1. Check if Docker and Docker Compose are installed
2. Check if the required ports are available
3. Clean up any existing containers to avoid conflicts
4. Start the containers using lightweight Alpine-based Python images
5. Copy the source files into the containers instead of using app volume mounts
6. Set up service discovery between containers using a Docker network
7. Configure the login service to connect to the backend API using the service name

This option avoids potential Docker volume-related issues that can occur with certain Docker versions or configurations. It also:
- Installs the necessary PostgreSQL development packages required for building the psycopg2 Python package
- Uses host networking to ensure the containers can communicate with each other
- Configures the login service to connect to the backend API at http://localhost:8000

### Option 2: Alpine Docker Compose

Use the provided `run_alpine.sh` script to run both the backend and login containers using an Alpine-based Docker Compose setup:

```bash
# Make the script executable (if not already)
chmod +x run_alpine.sh

# Run the services
./run_alpine.sh
```

This script uses Alpine Linux-based Python images which are more lightweight and may avoid some Docker-related issues.

### Option 2: Simple Docker Compose

Use the provided `run_simple.sh` script to run both the backend and login containers using a simplified Docker Compose setup:

```bash
# Make the script executable (if not already)
chmod +x run_simple.sh

# Run the services
./run_simple.sh
```

This script uses Docker Compose with a simplified configuration that builds containers from Dockerfiles.

### Option 3: Docker Compose with Health Checks

Use the provided `run_local.sh` script for a more robust Docker Compose setup with health checks:

```bash
# Make the script executable (if not already)
chmod +x run_local.sh

# Run the services
./run_local.sh
```

This script includes additional health checks to ensure the backend is ready before starting the login service.

### Option 4: Direct Execution (No Docker)

If you prefer not to use Docker, you can use the `run_direct.sh` script to run the services directly:

```bash
# Make the script executable (if not already)
chmod +x run_direct.sh

# Run the services
./run_direct.sh
```

This script will:
1. Check if the required ports are available
2. Start the backend service directly using Python and Uvicorn
3. Start the login service directly using Python and Uvicorn
4. Configure the login service to connect to the backend API at http://localhost:8000

### Option 5: Podman Build and Run

Use the provided `build_and_run_local.sh` script to build and run all application containers using Podman:

```bash
# Make the script executable (if not already)
chmod +x build_and_run_local.sh

# Build and run the application locally
./build_and_run_local.sh
```

This script will:
1. Build all containers (backend, login, main, nginx) using Podman
2. Create a Podman network for container communication
3. Stop and remove any existing containers with the same names
4. Run the containers with appropriate port mappings
5. Display access URLs and commands for viewing logs

Alternatively, you can use the `build_and_run_container.sh` script to build and run a specific container:

```bash
# Make the script executable (if not already)
chmod +x build_and_run_container.sh

# Build and run a specific container (e.g., backend)
./build_and_run_container.sh backend
```

This script accepts a single argument specifying which container to build and run:
- Valid options: backend, login, main, nginx, search
- The script will validate the input and show an error if an invalid container name is provided
- Dependencies between containers are checked (e.g., login depends on backend)

With this option, you can access:
- Backend API: http://localhost:8000
- Login page: http://localhost:8001
- Main page: http://localhost:8003
- Search page: http://localhost:8004/search
- Static content: http://localhost:8002/static

The main container is configured with the LOGIN_URL environment variable to ensure proper redirection when logging out.

To stop the containers:
```bash
podman stop chemtrack-backend chemtrack-login
```

With any of these options, you can access:
- Backend API: http://localhost:8000
- Login page: http://localhost:8001/login
- Search page: http://localhost:8004/search

To stop the services, press Ctrl+C in the terminal running the script.

### Docker Compose Configuration

The application uses Docker Compose for local development. The `docker-compose.yml` file defines the following services:

- **backend**: The backend API service
  - Built from the Dockerfile in `source/backend`
  - Exposed on port 8000
  - Configured with development environment variables
  - Includes health checks to ensure other services start only when backend is ready

- **login**: The login page service
  - Built from the Dockerfile in `source/login`
  - Exposed on port 8001
  - Configured to connect to the backend service using service discovery
  - Depends on the backend service being healthy before starting

- **main**: The main application interface
  - Built from the Dockerfile in `source/main`
  - Exposed on port 8003
  - Configured to connect to other services using environment variables
  - Depends on the backend service being healthy before starting

- **nginx**: The static content server
  - Built from the Dockerfile in `source/nginx`
  - Exposed on port 8002
  - Serves static CSS files and the copyright page
  - Includes health checks

- **search**: The search functionality
  - Built from the Dockerfile in `source/search`
  - Exposed on port 8004
  - Configured to connect to the backend service
  - Depends on the backend service being healthy before starting

- **shared-templates**: The shared templates service
  - Built from the Dockerfile in `source/shared-templates`
  - Exposed on port 8005
  - Provides shared header and navigation components
  - Depends on the backend service being healthy before starting

The services are connected via a Docker network named `chemtrack-network`, which enables service discovery between containers. The Docker Compose configuration ensures that services start in the correct order, with the backend service starting first and other services waiting for it to be healthy before starting.

### Backend API Container

The backend API container provides database communication:

- Located at `/source/backend`
- Built with FastAPI
- Provides API endpoints for application functionality
- Connects to PostgreSQL database using the chemuser credentials
- Available API endpoints:
  - `/login`: Authenticates users against the database and returns user preferences
  - `/chemsearch`: Searches for chemicals in inventory based on various criteria
  - `/get_user_preferences`: Retrieves user preferences by username

### Nginx Static Content Container

The nginx container serves static content for the application:

- Located at `/source/nginx`
- Built with the nginx:1.27-alpine3.21-slim image
- Serves static CSS files at the `/static` URI
- Provides a copyright page at the `/copyright` URI
- Configured with caching and performance optimizations for static content

### Application Styling

The application uses a modern, neutral color scheme defined in:

- `/source/nginx/styles.css`: Main CSS file for the application
- Provides styling for all application components
- Includes responsive design for various screen sizes
- Features a header with application name and a left navigation panel

## Testing

The application includes a comprehensive testing strategy outlined in the `docs/testing-strategy.md` document. This strategy covers:

- Module testing approach for backend API and frontend Flask components
- Selenium testing for end-to-end functionality
- Testing strategy recommendations (module-level, integration, end-to-end)
- Test harness implementation guidelines

## Authentication

The application uses username and password authentication. Credentials are stored in AWS Secrets Manager.

## Database

The application uses PostgreSQL for data storage. Database scripts are located in the `/scripts` directory.

### Database Structure (`scripts/setup_database.sql` and `scripts/user_preferences.sql`)

The database includes the following tables:

1. **chemicals**:
   - id: Sequential number (primary key)
   - name: Chemical name (up to 100 characters)
   - unit_of_measure: Unit of measure (up to 20 characters)

2. **inventory**:
   - id: Sequential number (primary key)
   - chemical_id: Reference to chemicals table
   - quantity: Current quantity (decimal)
   - reorder_quantity: Threshold for reordering (decimal)
   - location_id: Reference to locations table

3. **locations**:
   - location_id: Sequential number (primary key)
   - building_name: Building name (up to 50 characters)
   - lab_room_number: Lab room number (0-9999)
   - locker_number: Locker number (0-999)

4. **users**:
   - user_name: Username (up to 40 characters, primary key)
   - password: Password hash (up to 200 characters)
   - email_address: Email address (up to 120 characters)
   - role_name: Reference to roles table
   - rev_ts: Timestamp of last update (auto-updated)
   - pswd_reset: Flag indicating if password reset is required ('Y' or 'N')
   - last_reset: Timestamp of when the password was last reset

5. **roles**:
   - role_name: Role name (up to 50 characters, primary key)
   - role_description: Role description (up to 200 characters)

6. **user_preferences**:
   - id: Sequential number (primary key)
   - user_name: Reference to users table (foreign key)
   - preference_key: Preference name (up to 50 characters)
   - preference_value: Preference value (up to 200 characters)
   - created_at: Timestamp of creation
   - updated_at: Timestamp of last update (auto-updated)
   - UNIQUE constraint on (user_name, preference_key)

The setup_database.sql script creates a database user 'chemuser' with permissions to read, write, and delete records, but not modify the database structure. It also includes initial data for the chemicals, inventory, locations, and roles tables.

The user_preferences.sql script creates the user_preferences table and includes initial data for user 'john' with building set to 'building 202' and lab room set to '120'.

The add_pswd_reset_column.sql script adds a pswd_reset column to the users table to track password reset requests.

The add_last_reset_column.sql script adds a last_reset column to the users table to track when passwords were last reset. For existing users, it sets the last_reset date to one week ago.

### Deployment

To deploy the database infrastructure:

```bash
# 1. Deploy the RDS database
aws cloudformation create-stack --stack-name chemtrack-database \
  --template-body file://infrastructure/database.yaml \
  --parameters ParameterKey=AppName,ParameterValue=chemtrack

# 2. Get the database endpoint
DB_ENDPOINT=$(aws cloudformation describe-stacks --stack-name chemtrack-database \
  --query "Stacks[0].Outputs[?OutputKey=='DBInstanceEndpoint'].OutputValue" --output text)

# 3. Deploy the network load balancer
aws cloudformation create-stack --stack-name chemtrack-db-nlb \
  --template-body file://infrastructure/database-nlb.yaml \
  --parameters ParameterKey=AppName,ParameterValue=chemtrack \
  ParameterKey=DatabaseIP,ParameterValue=$(dig +short $DB_ENDPOINT)

# 4. Initialize the database (replace {{password}} with the actual password)
psql -h ctrds.767397980456.aws.glpoly.net -U postgre -d postgres -f scripts/setup_database.sql

# 5. Add user preferences table
psql -h ctrds.767397980456.aws.glpoly.net -U postgre -d postgres -f scripts/user_preferences.sql

#6. Add last reset column
psql -h ctrds.767397980456.aws.glpoly.net -U postgre -d postgres -f scripts/add_last_reset_column.sql

#7. Add password reset column
psql -h ctrds.767397980456.aws.glpoly.net -U postgre -d postgres -f scripts/add_pswd_reset_column.sql

#8. Enhance chemical table and generate data
psql -h ctrds.767397980456.aws.glpoly.net -U postgre -d postgres -f scripts/update_chemicals_data.sql
```

## Building, Pushing, and Deploying Containers

The application containers are built using Podman and pushed to Amazon ECR. Both Bash and PowerShell scripts are provided to automate this process:

### Bash Container Build Script (`build_and_push.sh`)

This script automates the process of building and pushing application containers to ECR:

- Builds the backend and login containers using Podman
- Creates ECR repositories if they don't exist
- Tags containers with the appropriate ECR repository URI
- Pushes containers to ECR

Usage:

```bash
# Build and push containers to ECR (default region: us-east-1)
./build_and_push.sh

# Build and push containers to a specific AWS region
./build_and_push.sh us-west-2
```

### PowerShell Container Build Script (`scripts/Build-And-Push.ps1`)

This script provides similar functionality to the bash script:

- Automatically discovers all container directories under `/source`
- Builds each container using Podman
- Creates ECR repositories if they don't exist
- Tags containers with the appropriate ECR repository URI
- Pushes containers to ECR

Usage:

```powershell
# Build and push containers to ECR (default region: us-east-1)
.\scripts\Build-And-Push.ps1

# Build and push containers to a specific AWS region
.\scripts\Build-And-Push.ps1 -AwsRegion "us-west-2"
```

Requirements:
- AWS CLI configured with appropriate permissions
- Podman installed and configured
- Authentication to AWS ECR

### Container Deployment Script (`deploy_containers.sh`)

This script automates the deployment of containers to ECS Fargate:

- Forces new deployments of the ECS services
- Waits for services to stabilize
- Verifies deployment status
- Assumes images have already been built and pushed to ECR
- Allows deploying specific services by name

Usage:

```bash
# Make the script executable (if not already)
chmod +x deploy_containers.sh

# Deploy all containers to ECS (default region: us-east-1)
./deploy_containers.sh

# Deploy containers to a specific AWS region
./deploy_containers.sh us-west-2

# Deploy specific services only (e.g., only backend and nginx)
./deploy_containers.sh us-east-1 backend nginx

# Deploy specific services to a different region
./deploy_containers.sh us-west-2 login main
```

Available services: backend, login, main, nginx, search

The script deploys the containers with the following URI mapping:
- Main container responds to `/`
- Login container responds to `/login`
- Nginx container responds to `/static`
- Backend container responds to `/backend`
- Search container responds to `/search`

All traffic goes through the HTTPS listener and is directed to the appropriate container based on the URI path.

Requirements:
- AWS CLI configured with appropriate permissions
- Authentication to AWS ECR
