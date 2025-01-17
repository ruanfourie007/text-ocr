import json
import base64
import boto3

lambda_client = boto3.client('lambda')


def is_valid_base64(content):
    try:
        decoded_data = base64.b64decode(content, validate=True)
        if base64.b64encode(decoded_data).decode('utf-8') == content.strip():
            return True
    except Exception:
        pass
    return False


def lambda_handler(event, context):
    base64_body = event['body']

    print(f"{base64_body=}")

    text = ""
    error = ""
    is_body_valid = is_valid_base64(base64_body)

    if is_body_valid:
        response = lambda_client.invoke(
            FunctionName="sam-app-TextRecogProxyFunction-dRR4gqzXUjGe",
            InvocationType='RequestResponse',
            Payload={
                'body': base64_body,
            }
        )

        if 'text' in response:
            text = response['text']
        else:
            error = "Failed to extract text."
    else:
        error = "Invalid base64 body."

    return {
        "statusCode": 200,
        "body": json.dumps({
            "valid_body": is_body_valid,
            "text": text,
            "error": error,
        }),
    }
