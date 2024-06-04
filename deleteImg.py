import json
import boto3
import logging

logging.basicConfig(level=logging.INFO)

def lambda_handler(event, context):
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # 或者指定你的域名
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'message': 'Preflight check successful'})
        }

    # 处理POST请求
    body = json.loads(event['body'])
    urls = body['urls']

    # 初始化 AWS S3 和 DynamoDB
    s3 = boto3.client('s3')
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ImageTags')  # 替换为你的表名

    # 定义你的桶名称
    image_bucket = 'image-bucket-as3'
    thumbnail_bucket = 'image-resized-as3'

    try:
        for url in urls:
            logging.info(f"Processing URL: {url}")
            # 根据缩略图 URL 从 DynamoDB 中找到原始图片 URL
            response = table.scan(
                FilterExpression="thumbnail_url = :url",
                ExpressionAttributeValues={":url": url}
            )
            if response['Items']:
                for item in response['Items']:
                    # 从 DynamoDB 中删除条目
                    table.delete_item(Key={'image_url': item['image_url']})
                    logging.info(f"Deleted item from DynamoDB: {item['image_url']}")

                    # 提取原始图片和缩略图的键
                    image_key = item['image_url'].split('/')[-1]
                    thumbnail_key = item['thumbnail_url'].split('/')[-1]

                    # 确保键不为空
                    if image_key:
                        s3.delete_object(Bucket=image_bucket, Key=image_key)
                        logging.info(f"Deleted original image from S3: {image_key}")
                    else:
                        logging.error(f"Failed to extract image key from URL: {item['image_url']}")

                    if thumbnail_key:
                        s3.delete_object(Bucket=thumbnail_bucket, Key=thumbnail_key)
                        logging.info(f"Deleted thumbnail from S3: {thumbnail_key}")
                    else:
                        logging.error(f"Failed to extract thumbnail key from URL: {item['thumbnail_url']}")

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # 或者指定你的域名
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'message': 'Images and thumbnails deleted successfully'})
        }
    except Exception as e:
        logging.error(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # 或者指定你的域名
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'message': 'Error deleting images and thumbnails', 'error': str(e)})
        }