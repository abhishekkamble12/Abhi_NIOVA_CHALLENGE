import boto3
import json
import time
import uuid
import logging
from urllib.request import urlopen

logger = logging.getLogger(__name__)

DEFAULT_BUCKET = 'meida-ai-content'
DEFAULT_REGION = 'us-east-1'
DEFAULT_LANGUAGE = 'en-US'


def transcribe(s3_key, bucket_name=DEFAULT_BUCKET, region_name=DEFAULT_REGION, language_code=DEFAULT_LANGUAGE):
    """
    Starts an AWS Transcribe job for an audio file in S3 and polls until complete.
    Returns the transcribed text.
    """
    transcribe_client = boto3.client('transcribe', region_name=region_name)

    job_name = f"transcribe-{uuid.uuid4().hex[:12]}"
    s3_uri = f"s3://{bucket_name}/{s3_key}"

    media_format = s3_key.rsplit('.', 1)[-1].lower()
    supported_formats = {'mp3', 'mp4', 'wav', 'flac', 'ogg', 'amr', 'webm', 'm4a'}
    if media_format not in supported_formats:
        media_format = 'mp3'

    transcribe_client.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': s3_uri},
        MediaFormat=media_format,
        LanguageCode=language_code,
    )

    logger.info("Started transcription job %s for %s", job_name, s3_uri)

    while True:
        status = transcribe_client.get_transcription_job(TranscriptionJobName=job_name)
        job_status = status['TranscriptionJob']['TranscriptionJobStatus']

        if job_status == 'COMPLETED':
            transcript_url = status['TranscriptionJob']['Transcript']['TranscriptFileUri']
            with urlopen(transcript_url) as resp:
                transcript_json = json.loads(resp.read().decode('utf-8'))
            return transcript_json['results']['transcripts'][0]['transcript']

        if job_status == 'FAILED':
            reason = status['TranscriptionJob'].get('FailureReason', 'Unknown')
            raise RuntimeError(f"Transcription job failed: {reason}")

        time.sleep(3)
