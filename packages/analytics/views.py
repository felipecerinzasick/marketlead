from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import ClientForm
from .models import Client


@login_required
def home(request):
    return render(request, 'analytics/home.html')


@login_required
def add_code_to_site(request):
    return render(request, 'analytics/add-code-to-site.html')


class NewCampaignView(LoginRequiredMixin, CreateView):
    form_class = ClientForm
    template_name = 'analytics/campaign-form.html'

    def get_initial(self):
        self.initial.update({'user': self.request.user })
        return self.initial

    def get_success_url(self):
        return reverse('analytics:view-campaign', kwargs={'pk': self.object.pk})


class SingleCampaignView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'analytics/single-campaign.html'


class EditCampaignView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = 'analytics/campaign-form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editing'] = True
        return context

    def get_success_url(self):
        return reverse('analytics:view-campaign', kwargs={'pk': self.object.pk})


class AllCampaignView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'analytics/all-campaign.html'


class TrafficCounter(View):
    http_method_names = ['get', 'post']

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(TrafficCounter, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        print("GET: {}".format(request.GET))
        return JsonResponse({
            "Gg": 1
        })

    def post(self, request, *args, **kwargs):
        print("POST: {}".format(request.POST))
        return JsonResponse({
            "pP": 1000
        })

