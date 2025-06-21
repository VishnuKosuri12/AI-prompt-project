Pre-environment Setup

*** Refer to PLANNING.md for general guideance

Reference for CloudFormation:
- Each file should have an AppName parameter with the default value "chemtrack"
- name fields should use "-"
- name fields should not use "_"

1) Create a CloudFormation script for the initial application environment setup
    - Create secret "chemtrack-db-admin-user" with a user name of "postgre" and a random password
    - Create secret "chemtrack-db-app-user" with the user name of "chemuser" and a random password
    - Create secret "env-vars" with the following key pairs:
        "app_url": "chemtrack.767397980456.aws.glpoly.net"
        "db_url": "ctrds.767397980456.aws.glpoly.net"

2) Add the following repositories to ECR
    - Create repository: "chemtrack/main"
    - Create repository: "chemtrack/search"
    - Create repository: "chemtrack/backend"
    - Create repository: "chemtrack/details"
    - Create repository: "chemtrack/login"

3) Add an S3 bucket for the project
    - Call the bucket "chemtrack_project_bucket"
    - The bucket should be private
    - Turn off versioning
    - It should be encrypted
    - Create a bucket policy with a deny for any s3 action when aws:SecureTransport is false.

4) Add an S3 bucket for access logs
    - Call it "chemtrack_access_logs"
    - The bucket should be private, no versioning, and encrypted
    - Create a bucket policy for "s3:PutObject" from principle "arn:aws:iam::127311923021:root".
    - Export the bucket info for use in other CloudFormation scripts

5) Use the following CloudFormation script to create a certificate for SSL.
    The reference to "CertificateGlpolyCatalogVersion" below should be a parameter.
        ALBCertificate:
            Type: "AWS::ServiceCatalog::CloudFormationProvisionedProduct"
            Properties:
            ProductName: "SSL Certificate aws.glpoly.net"
            ProvisionedProductName:
                !Sub "certificate-${AppName}"
            ProvisioningArtifactName: !Ref CertificateGlpolyCatalogVersion
            ProvisioningParameters:
                - Key: "Domain"
                Value: !Ref AppName  

Revisions:

1)  I have a problem with @/TASK01.md. The resource names should use dashes instead of underscores.
2) I'd like to rerun @/TASK01.md.  I've added an item #5.  I've also updated the CloudFormation rules at the top.


#not counted line
