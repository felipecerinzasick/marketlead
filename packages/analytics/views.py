import json

from django.http import JsonResponse
from django.shortcuts import redirect, reverse, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import ClientForm, PageForm
from .models import Client, Page, PageVisit, SiteVisit
from .utils import ip_from_request, stripped_scheme_url


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/home.html'

    def dispatch(self, request, *args, **kwargs):
        client = Client.objects.filter(user=request.user).last()
        if not client:
            return redirect('analytics:new-campaign')
        else:
            return super().dispatch(request, *args, **kwargs)


class NewCampaignView(LoginRequiredMixin, CreateView):
    form_class = ClientForm
    template_name = 'analytics/campaign/form.html'

    def get_initial(self):
        self.initial.update({'user': self.request.user })
        return self.initial

    def get_success_url(self):
        return reverse('analytics:new-page')

    def dispatch(self, request, *args, **kwargs):
        self.queryset = Client.objects.filter(user=request.user).last()
        if self.queryset:
            return redirect('analytics:home')
        else:
            return super().dispatch(request, *args, **kwargs)


class NewPageView(LoginRequiredMixin, CreateView):
    form_class = PageForm
    template_name = 'analytics/page/form.html'
    client_obj = None

    def dispatch(self, request, *args, **kwargs):
        self.client_obj = Client.objects.filter(user=request.user).last()
        if not self.client_obj:
            return redirect('analytics:new-campaign')
        else:
            return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        if not self.client_obj:
            return redirect('analytics:new-campaign')
        form.instance.host = self.client_obj
        self.success_url = "{}?{}={}".format(
            reverse('analytics:copy-code'),
            'kw', form.instance.keyword
        )
        return super().form_valid(form)


class CopyJsCode(HomeView, TemplateView):
    template_name = 'analytics/add-code-to-site.html'

    def dispatch(self, request, *args, **kwargs):
        client_obj = Client.objects.filter(user=request.user).last()
        if not client_obj:
            return redirect('analytics:new-campaign')
        if self.extra_context is None:
            self.extra_context = {}
        self.extra_context['tid'] = client_obj.track_id
        keyword = request.GET.get('kw')
        if keyword:
            self.extra_context['kw'] = keyword
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class AllPageView(LoginRequiredMixin, ListView):
    model = Page
    template_name = 'analytics/page/all.html'

    def dispatch(self, request, *args, **kwargs):
        client = Client.objects.filter(user=request.user).last()
        if not client:
            return redirect('analytics:new-campaign')
        self.queryset = Page.objects.filter(host=client)
        return super().dispatch(request, *args, **kwargs)


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
        return super().dispatch(request, *args, **kwargs)

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

