import json
import logging

from transcribe import transcribe
from context import generate_social_media_script

logger = logging.getLogger()
logger.setLevel(logging.INFO)

DEFAULT_BUCKET = 'meida-ai-content'
DEFAULT_LANGUAGE = 'en-US'


def lambda_handler(event, context):
    """
    AWS Lambda entry point.
    Handler setting in AWS console: lambda.lambda_handler

    Supports two trigger modes:

    1. S3 event trigger (audio uploaded to the bucket):
       Automatically picks up bucket + key from the S3 event Records payload.

    2. Direct / API Gateway invocation:
       Event body: {"s3_key": "audio/clip.mp3"}
       Optional:   "bucket_name", "language_code"
    """
    try:
        # --- Parse the incoming event ---
        if 'Records' in event:
            record = event['Records'][0]['s3']
            bucket_name = record['bucket']['name']
            s3_key = record['object']['key']
            language_code = DEFAULT_LANGUAGE
        elif 'body' in event:
            body = json.loads(event['body']) if isinstance(event['body'], str) else event['body']
            s3_key = body['s3_key']
            bucket_name = body.get('bucket_name', DEFAULT_BUCKET)
            language_code = body.get('language_code', DEFAULT_LANGUAGE)
        else:
            s3_key = event['s3_key']
            bucket_name = event.get('bucket_name', DEFAULT_BUCKET)
            language_code = event.get('language_code', DEFAULT_LANGUAGE)

        logger.info("Processing s3://%s/%s", bucket_name, s3_key)

        # --- Step 1: Transcribe audio via AWS Transcribe ---
        transcribed_text = transcribe(s3_key, bucket_name=bucket_name, language_code=language_code)
        logger.info("Transcription complete (%d chars)", len(transcribed_text))

        # --- Step 2: Generate platform scripts via Bedrock ---
        scripts = generate_social_media_script(transcribed_text)
        logger.info("Script generation complete")

        # --- Return JSON response ---
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "s3_key": s3_key,
                "bucket": bucket_name,
                "transcription": transcribed_text,
                "scripts": scripts
            })
        }

    except KeyError as e:
        logger.error("Missing required field: %s", e)
        return {
            "statusCode": 400,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"Missing required field: {e}"})
        }

    except Exception as e:
        logger.exception("Lambda execution failed")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
