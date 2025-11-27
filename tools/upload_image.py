import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError

def upload_image_to_s3(file_path, bucket_name, object_name=None):
    """
    Upload a file to an S3 bucket to trigger the Image Processor Lambda.

    :param file_path: File to upload (e.g., 'images/my-photo.jpg')
    :param bucket_name: The name of your S3 bucket (e.g., 'mce-uploads-mce-2')
    :param object_name: S3 object name. If not specified, file_path is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_path)

    # Initialize S3 client
    # ensure your environment has AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY set
    # or that you have run 'aws configure'
    s3_client = boto3.client('s3', region_name='us-east-1')

    try:
        print(f"Uploading {file_path} to {bucket_name}/{object_name}...")
        
        response = s3_client.upload_file(file_path, bucket_name, object_name)
        
        print("✅ Upload Successful")
        return True

    except NoCredentialsError:
        print("❌ Error: AWS credentials not found. Please configure your AWS credentials.")
        return False
    except ClientError as e:
        print(f"❌ Error: {e}")
        return False

# --- Usage Example ---
if __name__ == "__main__":
    # REPLACE THIS with your actual bucket name from Terraform output
    # It will look like: mce-uploads-<project_suffix>
    BUCKET_NAME = "mce-uploads-mce-2" 
    
    # The image you want to process
    IMAGE_PATH = "hello.png"

    # Create a dummy file for testing if it doesn't exist
    if not os.path.exists(IMAGE_PATH):
        with open(IMAGE_PATH, "wb") as f:
            f.write(b"dummy image content")

    upload_image_to_s3(IMAGE_PATH, BUCKET_NAME)