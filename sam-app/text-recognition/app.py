import os

import boto3
import base64
import io

from PIL import Image
import pytesseract


if os.getenv('AWS_EXECUTION_ENV') is not None:
    os.environ['LD_LIBRARY_PATH'] = '/opt/tesseract-layer/lib'
    os.environ['TESSDATA_PREFIX'] = '/opt/tesseract-layer/tesseract/share/tessdata'
    pytesseract.pytesseract.tesseract_cmd = '/opt/tesseract-layer/bin/tesseract'


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


def ocr_tesseract(image_data: bytes) -> OcrResult:
    image = Image.open(io.BytesIO(image_data))

    # Use pytesseract to get detailed OCR data
    ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)

    concatenated_text = ""
    total_confidence = 0
    total_words = 0

    # Loop through the OCR results
    for i in range(len(ocr_data['text'])):
        word = ocr_data['text'][i]
        confidence = ocr_data['conf'][i]

        if word.strip() and confidence != -1:
            concatenated_text += f"{word} "
            total_confidence += confidence
            total_words += 1

    # Calculate the overall average confidence
    overall_confidence = total_confidence / total_words if total_words > 0 else 0

    return OcrResult(concatenated_text.strip(), overall_confidence)


def ocr_textract(image_data: bytes) -> OcrResult:
    response = client.detect_document_text(
        Document={
            'Bytes': image_data
        }
    )

    line_blocks = [block for block in response['Blocks'] if block['BlockType'] == 'LINE']
    # Making some assumptions here..
    best_line = max(line_blocks, key=lambda block: block['Confidence'])

    return OcrResult(best_line['Text'], best_line['Confidence'])


def lambda_handler(event, context):
    base64_body = event['body']

    ocr_results = []

    image_data = base64.b64decode(base64_body)

    # Perform OCR using pytesseract
    try:
        ocr_results.append(ocr_tesseract(image_data))
    except Exception as e:
        print(f"ocr_tesseract failed with error: {e}")
        pass

    # Perform OCR using textract
    try:
        ocr_results.append(ocr_textract(image_data))
    except Exception as e:
        print(f"ocr_textract failed with error: {e}")
        pass

    print(f"OCR results: {len(ocr_results)}")
    for ocr_result in ocr_results:
        print("OCR result:", ocr_result.to_dict())

    # Return most confident result.
    return max(ocr_results, key=lambda ocr_result: ocr_result.confidence).to_dict()
