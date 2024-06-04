import json
import boto3
from boto3.dynamodb.conditions import Key

def lambda_handler(event, context):
    # 检查是否存在queryStringParameters
    if 'queryStringParameters' in event and 'thumbnail_url' in event['queryStringParameters']:
        thumbnail_url = event['queryStringParameters']['thumbnail_url']
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing thumbnail_url in query parameters'})
        }
    
    # 初始化DynamoDB资源
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ImageTags')  # 使用你创建的表名
    
    # 查询DynamoDB以找到对应的全尺寸图像URL和标签
    response = table.query(
        IndexName='thumbnail_url-index',  # 使用你创建的索引名
        KeyConditionExpression=Key('thumbnail_url').eq(thumbnail_url)
    )
    
    if response['Items']:
        item = response['Items'][0]
        image_url = item['image_url']
        tags = item['tags']
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*', 
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },

            'body': json.dumps({'image_url': image_url})
        }
    else:
        return {
            'statusCode': 404,
            'headers': {
                'Access-Control-Allow-Origin': '*',  
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },

            'body': json.dumps({'error': 'Thumbnail URL not found'})
        }