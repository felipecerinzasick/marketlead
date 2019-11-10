from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseNotAllowed


def get_full_url(request, rel_url=None):
    """
    :param rel_url: relative url, eg: /users/
    :return: absolute url, eg: http://www.example.com/users/
    """
    domain = "http://{}".format(get_current_site(request))
    if not rel_url:
        return domain
    return "{}{}".format(domain, rel_url)


def allowed_post_only(func):
    def decorated(request, *args, **kwargs):
        if request.method != 'POST':
            return HttpResponseNotAllowed('Not allowed to see content')
        return func(request, *args, **kwargs)
    return decorated
