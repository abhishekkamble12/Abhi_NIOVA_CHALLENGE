import boto3
import json


def generate_social_media_script(transcribed_text, model_id='amazon.nova-lite-v1:0', region_name='us-east-1'):
    """
    Takes transcribed text and uses Amazon Nova on AWS Bedrock
    to generate scripts for YouTube, Instagram, X, and TikTok.

    Returns a dict with platform-keyed scripts and the raw generated text.
    """
    bedrock_runtime = boto3.client(service_name='bedrock-runtime', region_name=region_name)

    prompt = f"""You are a social media content expert. Based on the following transcribed text:

<text>
{transcribed_text}
</text>

Generate a full script for each of these platforms: YouTube, Instagram, X (Twitter), and TikTok.

Return your answer strictly as valid JSON with the following structure (no extra text outside the JSON):
{{
  "youtube": "...",
  "instagram": "...",
  "x_twitter": "...",
  "tiktok": "..."
}}"""

    body = {
        "messages": [
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ],
        "inferenceConfig": {
            "max_new_tokens": 2000,
            "temperature": 0.7,
            "topP": 0.9
        }
    }

    response = bedrock_runtime.invoke_model(
        modelId=model_id,
        contentType='application/json',
        accept='application/json',
        body=json.dumps(body)
    )

    response_body = json.loads(response['body'].read())
    raw_text = response_body["output"]["message"]["content"][0]["text"]

    try:
        scripts = json.loads(raw_text)
    except json.JSONDecodeError:
        scripts = {
            "youtube": raw_text,
            "instagram": raw_text,
            "x_twitter": raw_text,
            "tiktok": raw_text,
            "_note": "Model did not return structured JSON; raw text used for all platforms."
        }

    return scripts
