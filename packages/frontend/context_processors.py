from django.conf import settings


def base_settings(request):
    print("wtf")
    return {
        "base_settings": {
            "debug": settings.DEBUG,
        }
    }

