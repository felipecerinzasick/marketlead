IP_TRY = [
    "HTTP_X_FORWARDED_FOR",
    "X_FORWARDED_FOR",
    "HTTP_CLIENT_IP",
    "HTTP_X_REAL_IP",
    "HTTP_X_FORWARDED",
    "HTTP_X_CLUSTER_CLIENT_IP",
    "HTTP_FORWARDED_FOR",
    "HTTP_FORWARDED",
    "HTTP_VIA",
    "REMOTE_ADDR"
]


def ip_from_request(request):
    ip = None
    for attempt in IP_TRY:
        possible = request.META.get(attempt)
        if possible:
            ip = possible
            break
    return ip
