import json
import os
from unittest import result
import boto3
from botocore.exceptions import ClientError


bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")


bedrock = boto3.client(service_name='bedrock-runtime', region_name='us-east-1')


def lambda_handler(event, context):
    try:
        # 1. Parse Input
        body = json.loads(event.get('body', '{}'))
        prompt = body.get('prompt')

        if not prompt:
            return build_response(400, {'error': 'Missing prompt'})

        # 2. Llama 3.1 Payload Structure
        # Note: Llama 3.1 8B Instruct Model ID
        model_id = "meta.llama3-1-8b-instruct-v1:0"

        native_request = {
            "prompt": f"<|begin_of_text|><|start_header_id|>user<|end_header_id|>\n\n{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n",
            "max_gen_len": 512,
            "temperature": 0.5,
        }

        # 3. Invoke Bedrock
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(native_request)
        )

        # 4. Parse Response
        response_body = json.loads(response['body'].read())
        generation = response_body.get('generation', '')

        return build_response(200, {'completion': generation})

    except Exception as e:
        print(f"Error: {str(e)}")
        return build_response(500, {'error': 'Internal Server Error'})


def build_response(status_code, body):
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps(body)
    }


def build_response(status_code, message):

    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"response": message})
    }
