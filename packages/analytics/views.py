import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, reverse, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import ClientForm, PageForm
from .models import Client, Page, PageVisit, SiteVisit
from .utils import ip_from_request, stripped_scheme_url


@login_required
def home(request):
    return render(request, 'analytics/home.html')


@login_required
def add_code_to_site(request):
    return render(request, 'analytics/add-code-to-site.html')


class NewCampaignView(LoginRequiredMixin, CreateView):
    form_class = ClientForm
    template_name = 'analytics/campaign/form.html'

    def get_initial(self):
        self.initial.update({'user': self.request.user })
        return self.initial

    def get_success_url(self):
        return reverse('analytics:view-campaign', kwargs={'pk': self.object.pk})


class SingleCampaignView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'analytics/campaign/single.html'


class SingleCampaignAllPagesView(SingleCampaignView):
    template_name = 'analytics/campaign/all-pages.html'


class EditCampaignView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'analytics/campaign/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editing'] = True
        return context

    def get_success_url(self):
        return reverse('analytics:view-campaign', kwargs={'pk': self.object.pk})


class AllCampaignView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'analytics/campaign/all.html'


class NewCampaignPageView(LoginRequiredMixin, CreateView):
    form_class = PageForm
    template_name = 'analytics/page/form.html'

    def get_success_url(self):
        return reverse('analytics:view-campaign-page', kwargs={'pk': self.object.pk})


class NewCampaignPageByClientView(NewCampaignPageView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = get_object_or_404(Client, pk=self.kwargs['pk'])
        context['client_obj'] = client
        return context


class SingleCampaignPageView(LoginRequiredMixin, DetailView):
    model = Page
    template_name = 'analytics/page/single.html'


class EditCampaignPageView(LoginRequiredMixin, UpdateView):
    model = Page
    form_class = PageForm
    template_name = 'analytics/page/form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editing'] = True
        return context

    def get_success_url(self):
        return reverse('analytics:view-campaign-page', kwargs={'pk': self.object.pk})


class AllCampaignPageView(LoginRequiredMixin, ListView):
    model = Page
    template_name = 'analytics/page/all.html'


class TrafficCounter(View):
    http_method_names = ['get', 'post']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TrafficCounter, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        ip_address = ip_from_request(request)
        json_str = request.GET.get('json')
        try:
            json_obj = json.loads(json_str)
            keys_list = ('origin', 'track_id')
            if set(keys_list).issubset(json_obj):
                track_id = json_obj.get('track_id')
                host_url = json_obj.get('origin')
                kw = json_obj.get('keyword')
                try:
                    site = Client.objects.get(track_id=track_id)

                    if stripped_scheme_url(site.url) != stripped_scheme_url(host_url):
                        return JsonResponse({
                            "success": False,
                            "error": {
                                "message": "URL is not registered"
                            }
                        })
                    else:
                        site.is_verified = True
                        site.save()
                        SiteVisit.objects.create(
                            site=site,
                            ip_addr=ip_address,
                        )
                    if kw:
                        try:
                            pg = Page.objects.get(keyword=kw)
                            PageVisit.objects.create(
                                page=pg,
                                ip_addr=ip_address,
                            )
                        except Page.DoesNotExist:
                            return JsonResponse({
                                "success": True,
                                "error": {
                                    "message": "Keywords doesn't match",
                                }
                            })
                except Client.DoesNotExist:
                    return JsonResponse({
                        "success": True,
                    })
        except json.JSONDecodeError:
            return JsonResponse({
                "success": False,
                "error": {
                    "message": "Error data",
                }
            })


        return JsonResponse({
            "success": True,
        })

    def post(self, request, *args, **kwargs):
        print("POST: {}".format(request.POST))
        return JsonResponse({
            "pP": 1000
        })


