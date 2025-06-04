# ChemTrack AWS Architecture Diagram

## Overview
This diagram provides a visual representation of the ChemTrack application's AWS architecture. It illustrates how different components interact with each other, from user access to supporting AWS services. The diagram uses the standard AWS architecture icons from the draw.io AWS shape library for accurate and recognizable AWS service representation.

## How to Open the Diagram
The diagram is created using draw.io (diagrams.net), a free online diagramming tool.

1. Visit [diagrams.net](https://app.diagrams.net/)
2. Click "Open Existing Diagram"
3. Select "Open from Device"
4. Navigate to and open the `aws-architecture-diagram.drawio` file

Alternatively, you can use the desktop version of draw.io if installed.

## Architecture Components

### User Layer
- **Users**: End users accessing the ChemTrack application
- **Developers**: Technical personnel who develop and maintain the application

### Intranet Subnets
- **Application Load Balancer**: Handles HTTPS traffic and distributes it to the containers
- **Network Load Balancer**: Provides database access for developers

### Private Subnets
- **ECS Fargate Environment**: Contains all application containers:
  - Login Container
  - Main Container
  - Admin Container
  - Search Container
  - Shared Templates Container
  - Backend API Container
  - NGINX Container
- **Lambda Function**: Manages email notifications
- **PostgreSQL Database**: Stores all application data

### Supporting Services
- **Amazon ECR**: Container Registry for storing Docker images
- **AWS Secrets Manager**: Stores credentials and secrets
- **AWS Parameter Store**: Manages configuration data and API keys
- **Amazon SNS**: Handles notification distribution

## Network Information
- **VPC ID**: vpc-019e35a7f8ca205e5
- **Intranet Subnets**: subnet-0ee959776d1683aa5, subnet-07257f93f815ce77c
- **Private Subnets**: subnet-08de8ae010ebfa1f3, subnet-0205ddf1053073b5c

## Notes
- HTTP traffic to the ALB is redirected to HTTPS
- The Backend API container communicates directly with the PostgreSQL database
- Containers pull images from ECR
- API key security is implemented in the backend container with keys stored in Parameter Store
