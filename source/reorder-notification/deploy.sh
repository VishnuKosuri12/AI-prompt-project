#!/bin/bash
# Script to package and upload the reorder notification Lambda function to S3

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Set variables
APP_NAME="chemtrack"
S3_BUCKET="chemtrack-project-bucket"
LAMBDA_NAME="reorder-notification"
ZIP_FILE="${LAMBDA_NAME}.zip"

echo "Packaging the Lambda function: ${LAMBDA_NAME}"

# Install dependencies to a local 'package' directory
echo "Installing dependencies..."
pip install -r requirements.txt --target ./package

# Copy the Lambda function code to the package directory
echo "Copying Lambda function code..."
cp lambda_function.py package/

# Create the zip file
echo "Creating zip file: ${ZIP_FILE}"
cd package
zip -r ../${ZIP_FILE} .
cd ..

# Upload to S3
echo "Uploading to S3: s3://${S3_BUCKET}/${ZIP_FILE}"
aws s3 cp ${ZIP_FILE} s3://${S3_BUCKET}/${ZIP_FILE}

# Clean up
echo "Cleaning up temporary files..."
rm -rf package
rm -f ${ZIP_FILE}

echo "Deployment package uploaded successfully to S3!"
echo "You can now deploy the CloudFormation template: sns-reorder-email.yaml"
cd ../..