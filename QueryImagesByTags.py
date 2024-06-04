import json
import boto3
import re


def extract_useremail_from_filename(filename):
    match = re.match(r"([^@]+)-.*", filename)
    return match.group(1).replace('_', '@') if match else None


def lambda_handler(event, context):
    # 解析传入的JSON请求
    try:
        body = json.loads(event['body'])
        user_email = body.get('useremail', None)
        tags = body.get('tags', [])
        counts = body.get('counts', [])
    except (json.JSONDecodeError, KeyError):
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'message': 'Invalid request format'})
        }

    if not user_email or not tags or not counts or len(tags) != len(counts):
        return {
            'statusCode': 400,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(
                {'message': 'User email, tags, and counts lists must be provided and counts must match tags length'})
        }

    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('ImageTags')  # 请确保使用正确的表名

    try:
        # 扫描所有项
        response = table.scan()

        matching_urls = []

        for item in response['Items']:
            # 检查当前项目的文件名是否包含指定的用户邮箱
            image_url = item.get('image_url', {})
            filename = image_url.split('/')[-1]
            email_in_filename = extract_useremail_from_filename(filename)

            if email_in_filename == user_email:
                item_tags = item.get('tags', [])
                match = all(item_tags.count(tag) >= count for tag, count in zip(tags, counts))

                if match and 'thumbnail_url' in item:
                    matching_urls.append(item['thumbnail_url'])

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'links': matching_urls})
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # 或者指定你的域名
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(f'Error fetching data: {str(e)}')
        }
