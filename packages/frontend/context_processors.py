from django.conf import settings


def base_settings(request):
    is_fb_connected = False
    user = request.user
    if user.is_authenticated:
        is_fb_connected = bool(user.get_social_auth_obj())
    return {
        "base_settings": {
            "debug": settings.DEBUG,
        },
        "is_fb_connected": is_fb_connected,
    }

