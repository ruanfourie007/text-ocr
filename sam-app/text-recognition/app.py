import json

import boto3
import base64
import io

from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = '/opt/bin/tesseract'

client = boto3.client('textract')

class OcrResult:
    def __init__(self, text, confidence):
        self.text = text
        self.confidence = confidence

    def to_dict(self):
        return {
            "text": self.text,
            "confidence": self.confidence
        }


def lambda_handler(event, context):

    print(json.dumps(event, indent=2))

    base64_body = event['body']

    ocr_results = []

    image_data = base64.b64decode(base64_body)

    # Load the binary data as an image
    image = Image.open(io.BytesIO(image_data))

    # Perform OCR using pytesseract
    try:

        text = pytesseract.image_to_string(image)
        print(f"tesseract {text=}")
    except Exception as e:
        print(e)
        pass

    # Perform OCR using textract
    try:
        response = client.detect_document_text(
            Document={
                'Bytes': image_data
            }
        )

        line_blocks = [block for block in response['Blocks'] if block['BlockType'] == 'LINE']
        # Making some assumptions here..
        best_line = max(line_blocks, key=lambda block: block['Confidence'])

        ocr_results.append(OcrResult(best_line['Text'], best_line['Confidence']))

    except Exception as e:
        print(e)
        pass

    for ocr_result in ocr_results:
        print("OCR result:", ocr_result.to_dict())

    # Return most confident result.
    return max(ocr_results, key=lambda ocr_result: ocr_result.confidence).to_dict()
