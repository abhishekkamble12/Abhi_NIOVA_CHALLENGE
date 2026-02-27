# AI Engine

Converts audio files into ready-to-post social media scripts.

## How It Works

1. **Audio uploaded** to S3 bucket (`meida-ai-content`)
2. **AWS Transcribe** converts speech to text
3. **Amazon Nova (Bedrock)** generates platform-specific scripts
4. **JSON response** returned with scripts for YouTube, Instagram, X, and TikTok

## Files

| File | Role |
|---|---|
| `lambda.py` | Lambda entry point (`lambda.lambda_handler`) |
| `transcribe.py` | Audio-to-text via AWS Transcribe |
| `context.py` | Text-to-scripts via Amazon Nova on Bedrock |

## Trigger Modes

- **S3 event** — auto-triggers when audio is uploaded to the bucket
- **API Gateway** — POST with `{"s3_key": "audio/clip.mp3"}`
- **Direct invoke** — pass `{"s3_key": "..."}` as the Lambda test event

## Sample Response

```json
{
  "statusCode": 200,
  "body": {
    "s3_key": "audio/clip.mp3",
    "bucket": "meida-ai-content",
    "transcription": "...",
    "scripts": {
      "youtube": "...",
      "instagram": "...",
      "x_twitter": "...",
      "tiktok": "..."
    }
  }
}
```

## IAM Permissions Required

- `transcribe:StartTranscriptionJob`
- `transcribe:GetTranscriptionJob`
- `bedrock:InvokeModel`
- `s3:GetObject` on `arn:aws:s3:::meida-ai-content/*`

## Lambda Config

- **Handler:** `lambda.lambda_handler`
- **Runtime:** Python 3.12
- **Timeout:** 120s+ (transcription polling needs time)
