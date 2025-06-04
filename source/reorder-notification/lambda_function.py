import json
import os
import boto3
import requests
from datetime import datetime
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    """
    Lambda function that calls the backend API to get users that need to be notified
    about chemicals that need to be reordered, and then sends them emails via SNS.
    
    This function is triggered by a scheduled CloudWatch event once per day at 3pm.
    """
    
    try:
        print('Starting reorder notification processing')
        
        # Get environment variables
        backend_url = os.environ.get('BACKEND_URL')
        sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
        aws_region = os.environ.get('AWS_REGION', 'us-east-1')
        
        if not backend_url or not sns_topic_arn:
            raise ValueError("Required environment variables BACKEND_URL and SNS_TOPIC_ARN not set")
        
        # Clean up backend URL - remove trailing slash if present
        if backend_url.endswith('/'):
            backend_url = backend_url[:-1]
            
        # Call the backend API to get users who need to be notified
        reorder_api_url = f"{backend_url}/backend/reorder_notif"
        print(f"Calling API at {reorder_api_url}")
        
        # Get API key from Parameter Store
        api_key = get_api_key_from_parameter_store(aws_region)
        
        # Add timeout and helpful headers
        headers = {
            'User-Agent': 'ChemTrack-Lambda-Function/1.0',
            'Accept': 'application/json',
            'X-API-Key': api_key
        }
        
        # Print for logging
        print(f"Making HTTP request to: {reorder_api_url}")
        response = requests.get(reorder_api_url, headers=headers, timeout=30)
        print(f"Response status code: {response.status_code}")
        
        # Raise exception for non-200 responses
        response.raise_for_status()
        
        data = response.json()
        
        if not data.get('success') or 'users' not in data:
            print(f"API returned unsuccessful response or missing users: {data}")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'No users to notify or API error',
                    'data': data
                })
            }
        
        users = data.get('users', [])
        
        if not users:
            print("No users need to be notified")
            return {
                'statusCode': 200,
                'body': json.dumps({
                    'message': 'No users need to be notified'
                })
            }
        
        # Create SNS client
        sns_client = boto3.client('sns', region_name=aws_region)
        
        # Send notifications to each user
        for user in users:
            username = user.get('username')
            email = user.get('email')
            chemicals = user.get('chemicals', [])
            
            if not email or not chemicals:
                continue
            
            # Prepare email content
            subject = "Chemtrack -- reorder alert"
            
            # Format the email body
            body = "The following chemical(s) need to be reordered:\n\n"
            
            # Group chemicals by lab
            labs = {}
            for chemical in chemicals:
                lab_key = f"{chemical.get('building_name')} - Room {chemical.get('lab_room_number')}"
                
                if lab_key not in labs:
                    labs[lab_key] = []
                
                labs[lab_key].append(chemical)
            
            # Format chemicals by lab
            for lab, lab_chemicals in labs.items():
                body += f"\n{lab}:\n"
                for chemical in lab_chemicals:
                    body += f"- {chemical.get('name')}: Current quantity: {chemical.get('quantity')} {chemical.get('unit_of_measure')}, " \
                           f"Reorder quantity: {chemical.get('reorder_quantity')} {chemical.get('unit_of_measure')}\n"
            
            body += f"\n\nThank you,\nChemtrack System\n\nSent: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            try:
                # Publish message to SNS topic
                response = sns_client.publish(
                    TopicArn=sns_topic_arn,
                    Subject=subject,
                    Message=body
                )
                print(f"Notification sent to {email} (user: {username}), SNS message ID: {response.get('MessageId')}")
            except Exception as e:
                print(f"Error sending notification to {email} (user: {username}): {str(e)}")
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': f'Successfully processed notifications for {len(users)} users'
            })
        }
    
    except Exception as e:
        print(f"Error in lambda_handler: {str(e)}")
        raise

def get_api_key_from_parameter_store(region):
    """Fetch API key from AWS Parameter Store"""
    try:
        print("Retrieving API key from Parameter Store")
        ssm_client = boto3.client('ssm', region_name=region)
        
        response = ssm_client.get_parameter(
            Name="chemtrack-api-key",
            WithDecryption=True
        )
        
        api_key = response.get('Parameter', {}).get('Value')
        
        if not api_key:
            raise ValueError("API key not found in Parameter Store")
            
        print("API key retrieved successfully")
        return api_key
    except ClientError as e:
        print(f"Error retrieving API key from Parameter Store: {e}")
        raise ValueError(f"Failed to retrieve API key: {str(e)}")
