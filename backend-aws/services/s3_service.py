"""S3 Service for EC2 in ap-south-1"""
import httpx
from datetime import datetime
from aws_requests_auth.aws_auth import AWSRequestsAuth
from config.aws_config import get_aws_settings

settings = get_aws_settings()

class S3Service:
    def __init__(self):
        self.bucket = settings.S3_BUCKET
        self.region = settings.AWS_REGION
        self.base_url = f"https://{self.bucket}.s3.{self.region}.amazonaws.com"
        self.auth = AWSRequestsAuth(
            aws_access_key=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            aws_host=f"{self.bucket}.s3.{self.region}.amazonaws.com",
            aws_region=self.region,
            aws_service='s3'
        )
    
    async def upload_file(self, file_data: bytes, key: str, content_type: str = "application/octet-stream") -> str:
        """Upload file to S3"""
        url = f"{self.base_url}/{key}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.put(
                url,
                content=file_data,
                headers={"Content-Type": content_type},
                auth=self.auth
            )
            response.raise_for_status()
        
        return url
    
    async def download_file(self, key: str) -> bytes:
        """Download file from S3"""
        url = f"{self.base_url}/{key}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, auth=self.auth)
            response.raise_for_status()
            return response.content
    
    async def delete_file(self, key: str):
        """Delete file from S3"""
        url = f"{self.base_url}/{key}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(url, auth=self.auth)
            response.raise_for_status()
    
    async def head_file(self, key: str) -> bool:
        """Check if file exists"""
        url = f"{self.base_url}/{key}"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.head(url, auth=self.auth)
                return response.status_code == 200
        except:
            return False
    
    async def upload_video(self, file_data: bytes, filename: str) -> str:
        key = f"videos/{datetime.utcnow().strftime('%Y/%m/%d')}/{filename}"
        return await self.upload_file(file_data, key, "video/mp4")
    
    async def upload_thumbnail(self, file_data: bytes, video_id: str) -> str:
        key = f"thumbnails/{video_id}.jpg"
        return await self.upload_file(file_data, key, "image/jpeg")

def get_s3_service() -> S3Service:
    return S3Service()
