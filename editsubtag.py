#lambda function for editing subscription according to user's input
import json
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('UserSubscriptions')
sns_client = boto3.client('sns')
ses_client = boto3.client('ses', region_name='us-east-1')  # 确保使用正确的区域


def lambda_handler(event, context):
    try:
        # 解析请求体
        body = json.loads(event['body'])
        email = body['useremail']
        new_tags = set(body['tags'])

        # 查询当前订阅的标签
        current_entry = table.get_item(Key={'email': email})
        current_tags = set(current_entry['Item']['tags']) if 'Item' in current_entry and 'tags' in current_entry[
            'Item'] else set()

        # 确定新增和已取消的标签
        tags_to_add = new_tags - current_tags
        tags_to_remove = current_tags - new_tags

        # 订阅新增的标签
        for tag in tags_to_add:
            topic_arn = f"arn:aws:sns:us-east-1:187701342705:{tag}"
            response = sns_client.subscribe(
                TopicArn=topic_arn,
                Protocol='email',
                Endpoint=email
            )

        # 取消不再订阅的标签
        for tag in tags_to_remove:
            # 需要检索对应的订阅ARN
            response = sns_client.list_subscriptions_by_topic(TopicArn=f"arn:aws:sns:us-east-1:187701342705:{tag}")
            subscriptions = response['Subscriptions']
            for sub in subscriptions:
                if sub['Endpoint'] == email:
                    sns_client.unsubscribe(SubscriptionArn=sub['SubscriptionArn'])
            # 发送取消订阅的邮件通知
            ses_client.send_email(
                Source='noreply@yourdomain.com',
                Destination={'ToAddresses': [email]},
                Message={
                    'Subject': {'Data': f'Unsubscribed from {tag} Notifications'},
                    'Body': {
                        'Text': {'Data': f'You have successfully unsubscribed from notifications about {tag}.'}
                    }
                }
            )

        # 更新DynamoDB
        response = table.update_item(
            Key={'email': email},
            UpdateExpression='SET tags = :val',
            ExpressionAttributeValues={
                ':val': list(new_tags)
            },
            ReturnValues="UPDATED_NEW"
        )

        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps("Subscription updated successfully")
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'OPTIONS,POST,GET'
            },
            'body': json.dumps(f'Error processing request: {str(e)}')
        }
