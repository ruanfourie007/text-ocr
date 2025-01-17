import json
import base64
import boto3

lambda_client = boto3.client('lambda')

def image_preprocessing(image):
    # TODO: Perform necessary processing before sending to OCR API's
    return image

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

    text = ""
    error = None
    confidence = None
    is_valid_base64_body = is_valid_base64(base64_body)

    if is_valid_base64_body:

        base64_body = image_preprocessing(base64_body)

        response = lambda_client.invoke(
            FunctionName="sam-app-TextRecogFunction-rPvJ5r2opfSU",
            InvocationType='RequestResponse',
            Payload=json.dumps({"body": base64_body})
        )

        response_payload = json.loads(response['Payload'].read().decode('utf-8'))

        if 'text' in response_payload:
            text = response_payload['text']
            confidence = response_payload['confidence']
        else:
            error = "Failed to extract text."
    else:
        error = "Invalid base64 body."

    return {
        "statusCode": 200,
        "body": json.dumps({
            "text": text,
            "confidence": confidence,
            "error": error,
        }),
    }
