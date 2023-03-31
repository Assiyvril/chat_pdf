"""
WSGI config for GPT project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/wsgi/
"""

import os
from channels.routing import ProtocolTypeRouter
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'GPT.settings')

django_asgi_application = get_wsgi_application()

application = ProtocolTypeRouter({
    "http": get_wsgi_application(),
    # Just HTTP for now. (We can add other protocols later.)
})
