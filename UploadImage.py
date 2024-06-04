import json
import boto3
import base64

s3 = boto3.client('s3')
BUCKET_NAME = 'image-bucket-as3'


def sanitize_filename(filename):
    # 将@替换为_
    return filename.replace('@', '_')


def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        image_data = base64.b64decode(body['image'])
        image_name = body['name']
        user_email = body['useremail']

        # Create new image name with useremail prefix and sanitize it
        new_image_name = f"{user_email}-{image_name}"
        sanitized_image_name = sanitize_filename(new_image_name)

        # Upload the image to S3 bucket with new name
        s3.put_object(Bucket=BUCKET_NAME, Key=sanitized_image_name, Body=image_data)

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # 或者指定域名
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps('Image uploaded successfully')
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # 或者指定你的域名
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(f'Error uploading image: {str(e)}')
        }
