import json
import os
import boto3
from botocore.exceptions import ClientError


bedrock = boto3.client(service_name="bedrock-runtime", region_name="us-east-1")


def lambda_handler(event, context):

    try:
        body = json.loads(event.get("body", "{}"))
        prompt = body.get("prompt")
    except (json.JSONDecodeError, AttributeError):
        return build_response(400, "Invalid JSON input")

    if not prompt:
        return build_response(400, "Missing 'prompt' in request body")

    if os.environ.get("MOCK_MODE") == "true":
        return build_response(200, f"MOCK RESPONSE: Your prompt was '{prompt}'")

    model_id = "anthropic.claude-3-haiku-20240307-v1:0"

    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "messages": [
            {
                "role": "user",
                "content": [{"type": "text", "text": prompt}]
            }
        ]
    }

    try:
        response = bedrock.invoke_model(
            modelId=model_id,
            body=json.dumps(payload)
        )

        result = json.loads(response.get("body").read())
        output_text = result["content"][0]["text"]

        return build_response(200, output_text)

    except ClientError as e:
        print(f"Error: {e}")
        return build_response(500, "Internal Server Error during model inference")


def build_response(status_code, message):

    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({"response": message})
    }
