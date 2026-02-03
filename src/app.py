import json
import os
from unittest import result
import boto3
from botocore.exceptions import ClientError


bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")


bedrock = boto3.client(service_name='bedrock-runtime')


def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        user_prompt = body.get('prompt', 'Hello!')

        # Amazon Titan payload structure
        native_request = {
            "inputText": user_prompt,
            "textGenerationConfig": {
                "maxTokenCount": 512,
                "temperature": 0.5,
            }
        }

        response = bedrock.invoke_model(
            modelId="amazon.titan-text-lite-v1",
            body=json.dumps(native_request)
        )

        model_response = json.loads(response['body'].read())
        # Titan returns 'results' list
        response_text = model_response['results'][0]['outputText']

        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'completion': response_text})
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}


def build_response(status_code, message):

    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"response": message})
    }
