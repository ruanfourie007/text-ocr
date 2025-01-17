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



    response = lambda_client.invoke(
        FunctionName="sam-app-TextRecogProxyFunction-dRR4gqzXUjGe",
        InvocationType='RequestResponse',
        Payload=event
    )

    print(f"{response=}")

    return {
        "statusCode": 200,
        "body": json.dumps({
            "text": text,
            "valid_body": is_body_valid,
            "error": error,
        }),
    }
