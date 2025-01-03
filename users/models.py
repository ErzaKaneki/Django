from django.db import models
from django.core.files.storage import default_storage
from django.contrib.auth.models import User
from PIL import Image
from io import BytesIO
import boto3
from django.core.files.base import ContentFile


    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        default='profile_pics/default.png',
        blank=True,
        null=True
        )
    
    def save(self, *args, **kwargs):
        if self.profile_picture:
            # get the image from the profile_picture field
            img = Image.open(self.profile_picture)
            
            # Convert the image to RGB if it is in P mode
            if img.mode == 'P':
                img = img.convert('RGB')
            
            # Resize the image
            img = img.resize((150, 150), Image.Resampling.LANCZOS)
            
            # Save resized image to BytesIO object
            buffer = BytesIO()
            img.save(buffer, format='JPEG')
            buffer.seek(0)
            
            # Create a new ContentFile
            file_content = ContentFile(buffer.getvalue())
            file_name = f'{self.user.username}_profile.jpg'
            
            # Save the resized image to s3
            s3 = boto3.client('s3')
            bucket_name = 'echoe5-files'
            s3.put_object(Bucket=bucket_name, Key=f'profile_pics/{file_name}', Body=file_content)
            
            # Update the profile picture field to the point to S3 URL
            self.profile_picture = f'profile_pics/{file_name}'
            
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.user.username} Profile'
    