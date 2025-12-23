# Add these to your Django settings.py

# D-ID API Configuration
DID_API_KEY = "your-did-api-key-here"  # Get from https://studio.d-id.com/

# Background Removal API (Optional)
UNSCREEN_API_KEY = "your-unscreen-api-key"  # Get from https://www.unscreen.com/

# Media Files Configuration
import os
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Create avatars directory
AVATARS_DIR = os.path.join(MEDIA_ROOT, 'avatars')
os.makedirs(AVATARS_DIR, exist_ok=True)

# Static Files
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# CORS Settings (if using separate frontend)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# Celery Configuration (for background video processing)
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'

# Cache Configuration (for video caching)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}