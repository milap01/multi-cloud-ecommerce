import json
import boto3
import os
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3_client = boto3.client('s3')

def handler(event, context):
    """
    Lambda function triggered by S3 upload events.
    Processes uploaded images and creates metadata.
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    try:
        # Parse S3 event
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            size = record['s3']['object']['size']
            
            logger.info(f"Processing file: {key} from bucket: {bucket}")
            
            # Create metadata object
            metadata = {
                'original_key': key,
                'size_bytes': size,
                'processed_at': datetime.utcnow().isoformat(),
                'status': 'processed'
            }
            
            # Save metadata to S3
            metadata_key = f"metadata/{key}.json"
            s3_client.put_object(
                Bucket=bucket,
                Key=metadata_key,
                Body=json.dumps(metadata),
                ContentType='application/json'
            )
            
            logger.info(f"Successfully processed {key}")
            
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Files processed successfully',
                'processed_count': len(event['Records'])
            })
        }
        
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        raise e