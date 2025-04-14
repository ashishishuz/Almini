import os
from pathlib import Path

# Media files configuration
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Static files configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Add this to your INSTALLED_APPS if not already present
INSTALLED_APPS = [
    # ... other apps ...
    'channels',
]

# Add at the end of the file
ASGI_APPLICATION = 'Almini.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer'
    }
}