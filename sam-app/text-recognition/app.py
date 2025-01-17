import json

import boto3
import base64
import io

from PIL import Image
import pytesseract

client = boto3.client('textract')

def lambda_handler(event, context):

    print(json.dumps(event, indent=2))

    base64_body = event['body']

    image_data = base64.b64decode(base64_body)

    # Load the binary data as an image
    image = Image.open(io.BytesIO(image_data))

    # Perform OCR using pytesseract
    text = pytesseract.image_to_string(image)

    print(f"{text=}")

    # Perform OCR using textract
    try:
        response = client.detect_document_text(
            Document={
                'Bytes': base64.b64decode(base64_body)
            }
        )

        print(json.dumps(response))

        return json.dumps(response)

    except Exception as e:
        print(e)
        pass


    # TODO: Perform confidence scores..

    return None
