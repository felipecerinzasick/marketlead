from django.http import HttpResponse
from django.template.loader import get_template
from io import BytesIO
from urllib.parse import urlparse
from xhtml2pdf import pisa


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


def stripped_scheme_url(url):
    parsed_url = urlparse(url)
    domain = str(parsed_url.hostname).replace('www.', '')  # ignored www match
    if parsed_url.path == '/':
        return domain
    return domain + str(parsed_url.path)


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

