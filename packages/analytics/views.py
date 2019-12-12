import datetime
import json

from django.http import JsonResponse
from django.shortcuts import redirect, reverse, get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import ClientForm, PageForm
from .models import Client, Page, PageVisit, SiteVisit
from .utils import ip_from_request, stripped_scheme_url


# 1. Fresh
# 2. Have site but no page
# 3. have site have page


@method_decorator([login_required, ], name='dispatch')
class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/home.html'

    def dispatch(self, request, *args, **kwargs):
        website = Client.objects.filter(user=request.user)
        if not website.exists():
            # fresh user
            return super().dispatch(request, *args, **kwargs)
        client = website.last()
        if not Page.objects.filter(host=client).exists():
            # registered website but no page
            return redirect('analytics:new-page')
        # have website and page
        return redirect('analytics:report')


@method_decorator([login_required, ], name='dispatch')
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


@method_decorator([login_required, ], name='dispatch')
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


@method_decorator([login_required, ], name='dispatch')
class AllPageView(LoginRequiredMixin, ListView):
    model = Page
    template_name = 'analytics/page/all.html'

    def dispatch(self, request, *args, **kwargs):
        website = Client.objects.filter(user=request.user)
        if not website.exists():
            return redirect('analytics:new-campaign')
        client = website.last()
        pages = Page.objects.filter(host=client).order_by('id')
        if not pages.exists():
            return redirect('analytics:new-page')
        self.queryset = pages
        return super().dispatch(request, *args, **kwargs)


@method_decorator([login_required, ], name='dispatch')
class SingleCampaignView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'analytics/campaign/single.html'


@method_decorator([login_required, ], name='dispatch')
class SingleCampaignAllPagesView(SingleCampaignView):
    template_name = 'analytics/campaign/all-pages.html'


@method_decorator([login_required, ], name='dispatch')
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


@method_decorator([login_required, ], name='dispatch')
class AllCampaignView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'analytics/campaign/all.html'


@method_decorator([login_required, ], name='dispatch')
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


@method_decorator([login_required, ], name='dispatch')
class SingleCampaignPageView(LoginRequiredMixin, DetailView):
    model = Page
    template_name = 'analytics/page/single.html'


@method_decorator([login_required, ], name='dispatch')
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


@method_decorator([login_required, ], name='dispatch')
class AllCampaignPageView(LoginRequiredMixin, ListView):
    model = Page
    template_name = 'analytics/page/all.html'


@method_decorator([csrf_exempt, ], name='dispatch')
class TrafficCounter(View):
    http_method_names = ['get', 'post']

    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        ip_address = ip_from_request(request)
        json_str = request.GET.get('json')
        try:
            json_obj = json.loads(json_str)
            keys_list = ('origin', 'track_id', 'keyword')
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
                        sv_obj, sv_created = SiteVisit.objects.get_or_create(
                            site=site,
                            ip_addr=ip_address,
                        )
                        if not sv_created:
                            sv_obj.updated = datetime.datetime.now()
                            sv_obj.save()
                    if kw:
                        try:
                            pg = Page.objects.get(keyword=kw)
                            pv_obj, pv_created = PageVisit.objects.get_or_create(
                                page=pg,
                                ip_addr=ip_address,
                            )
                            if not pv_created:
                                pv_obj.updated = datetime.datetime.now()
                                pv_obj.save()
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

