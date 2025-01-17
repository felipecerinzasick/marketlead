import datetime
import json

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.edit import DeleteView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import ClientForm, PageForm
from .models import Client, Page, PageVisit, SiteVisit
from .utils import ip_from_request, stripped_scheme_url, render_to_pdf
from fb_api.models import FbAdAccount, InsightData
from fb_api.api_caller import ApiParser


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
        self.initial.update({'user': self.request.user, })
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


@method_decorator([login_required, ], name='dispatch')
class CopyJsCode(LoginRequiredMixin, TemplateView):
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
    """Report Page"""
    model = Page
    template_name = 'analytics/page/all.html'
    last_days = 30

    def dispatch(self, request, *args, **kwargs):
        user_obj = request.user
        website = Client.objects.filter(user=user_obj)
        if not website.exists():
            return redirect('analytics:new-campaign')
        client = website.last()
        pages = Page.objects.filter(host=client).order_by('id')
        if not pages.exists():
            return redirect('analytics:new-page')
        self.queryset = pages
        self.extra_context = {
            "site": client,
        }
        fb_acc = user_obj.get_social_auth_obj()
        if fb_acc:
            fbad_accounts = FbAdAccount.objects.filter(fb_acc=fb_acc)
            if fbad_accounts.exists():
                selected_fbad_acc = fbad_accounts.filter(is_selected=True).first()
                if not selected_fbad_acc:
                    """
                    Generally this is unnecessary.
                    but if 'somehow' any ad account is not selected, this exception is required
                    which is generally not possible
                    """
                    selected_fbad_acc = fbad_accounts.first()
                    selected_fbad_acc.is_selected = True
                    selected_fbad_acc.save()
                created_time = datetime.datetime.now() - datetime.timedelta(minutes=settings.API_REQUEST_EXPIRE_TIME)
                ins_data_obj = InsightData.objects.filter(ad_acc=selected_fbad_acc, created_at__gte=created_time)
                last_days = request.GET.get('last_days')
                if last_days:
                    self.last_days = int(last_days)
                if ins_data_obj.exists() and ins_data_obj.filter(days_count=self.last_days).exists():
                    non_expired_data = ins_data_obj.filter(days_count=self.last_days).latest()
                else:
                    today = datetime.date.today()
                    days_ago = today - datetime.timedelta(days=self.last_days)
                    ad_insight_data = selected_fbad_acc.get_insight_data(days_ago, today)
                    non_expired_data = InsightData.objects.create(
                        ad_acc=selected_fbad_acc,
                        data=ad_insight_data,
                        days_count=self.last_days,
                    )

                self.extra_context.update({
                    "ad_accounts": fbad_accounts,
                    "selected_ad_acc": selected_fbad_acc,
                    "ad_data": non_expired_data.data,
                    "last_days": self.last_days,
                })
            else:
                ap = ApiParser(user_obj.get_access_token())
                acc_data = ap.get_all_ad_accounts()
                for item in acc_data:
                    FbAdAccount.objects.create(fb_acc=fb_acc, ads_id=item.get('id', ''), account_id=item.get('account_id', ''))
                self.extra_context.update({
                    "ad_accounts": FbAdAccount.objects.filter(fb_acc=fb_acc),
                    "selected_ad_acc": None
                })
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        adac = request.GET.get('ad_account')
        is_pdf = request.GET.get('pdf')
        if adac:
            user_obj = request.user
            fb_acc = user_obj.get_social_auth_obj()
            if fb_acc:
                fbad_accounts = FbAdAccount.objects.filter(fb_acc=fb_acc)
                if fbad_accounts.exists():
                    try:
                        selected_fbadac = FbAdAccount.objects.get(fb_acc=fb_acc, account_id=adac)
                        for fbac in fbad_accounts:
                            if fbac is not selected_fbadac:
                                fbac.is_selected = False
                                fbac.save()
                        selected_fbadac.is_selected = True
                        selected_fbadac.save()
                        return redirect('analytics:report')
                    except FbAdAccount.DoesNotExist:
                        pass
        elif is_pdf:
            context = {
                "pages": self.queryset,
                "ad_data": self.extra_context.get('ad_data', {}),
            }
            pdf = render_to_pdf('analytics/pdf-report.html', context)
            if pdf:
                response = HttpResponse(pdf, content_type='application/pdf')
                if not self.queryset.exists():
                    filename = "Report.pdf"
                else:
                    filename = "Report_{}.pdf".format(self.queryset.first().host.domain)
                content = "inline; filename='{}'".format(filename)
                download = request.GET.get("download")
                if download:
                    content = "attachment; filename={}".format(filename)
                response['Content-Disposition'] = content
                return response
            return HttpResponse("Not found")
        return super().get(request, *args, **kwargs)


@method_decorator([login_required, ], name='dispatch')
class DeletePageView(LoginRequiredMixin, DeleteView):
    model = Page
    success_url = reverse_lazy('analytics:report')

    def get(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


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

