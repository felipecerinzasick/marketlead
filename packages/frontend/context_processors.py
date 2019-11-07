from django.conf import settings


def base_settings(request):
    return {
        "base_settings": {
            "debug": settings.DEBUG,
        }
    }

