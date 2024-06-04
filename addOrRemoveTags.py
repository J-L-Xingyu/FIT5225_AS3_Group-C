import json
import boto3

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        urls = body.get('url', [])
        tags = body.get('tags', [])
        operation_type = body.get('type')  # 1 for add, 0 for remove

        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('ImageTags')  # 替换为你的表名

        for url in urls:
            response = table.scan(
                FilterExpression="image_url = :url or thumbnail_url = :url",
                ExpressionAttributeValues={":url": url}
            )

            if response['Items']:
                item = response['Items'][0]
                current_tags = item.get('tags', [])

                if operation_type == 1:  # 添加标签
                    for tag in tags:
                        current_tags.append(tag)
                elif operation_type == 0:  # 删除标签
                    for tag in tags:
                        if tag in current_tags:
                            current_tags.remove(tag)


                # 更新DynamoDB项
                table.update_item(
                    Key={'image_url': item['image_url']},
                    UpdateExpression="set tags = :t",
                    ExpressionAttributeValues={':t': list(current_tags)},
                    ReturnValues="UPDATED_NEW"
                )
            else:
                print(f"Item not found for URL: {url}")

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # 或者指定你的域名
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'message': 'Tags updated successfully'})
        }

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',  # 或者指定你的域名
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps({'error': str(e)})
        }