from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import UpdateView, CreateView, DeleteView, ListView, TemplateView, DetailView

from src.accounts.decorators import company_required
from src.portals.company.bll import get_user_company_bll
from .models import Job, Company, Candidate


@method_decorator(company_required, name='dispatch')
class DashboardView(TemplateView):
    template_name = 'company/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        jobs = Job.objects.filter(company__user=self.request.user)
        context['jobs'] = jobs
        context['jobs_all_count'] = jobs.count()
        context['jobs_open_count'] = jobs.filter(status='o').count()
        context['jobs_close_count'] = jobs.filter(status='c').count()
        return context


@method_decorator(company_required, name='dispatch')
class CompanyUpdateView(UpdateView):
    model = Company
    fields = [
        'name', 'tag_line', 'description',
        'business_type', 'contact_number',
        'contact_email', 'contact_address'
    ]

    def get_success_url(self):
        return reverse_lazy('company:company-update')

    def get_object(self, queryset=None):
        return get_user_company_bll(self.request.user)


@method_decorator(company_required, name='dispatch')
class JobListView(ListView):
    model = Job

    def get_queryset(self):
        return Job.objects.filter(company__user=self.request.user)


@method_decorator(company_required, name='dispatch')
class JobCreateView(CreateView):
    model = Job
    fields = ['title', 'category', 'description']
    success_url = reverse_lazy('company:job-list')

    def form_valid(self, form):
        form.instance.company = get_user_company_bll(self.request.user)
        return super(JobCreateView, self).form_valid(form)


@method_decorator(company_required, name='dispatch')
class JobUpdateView(UpdateView):
    model = Job
    fields = ['title', 'category', 'description', 'status']
    success_url = reverse_lazy('company:job-list')

    def get_object(self, queryset=None):
        return get_object_or_404(
            Job.objects.filter(
                company__user=self.request.user
            ), pk=self.kwargs['pk']
        )


@method_decorator(company_required, name='dispatch')
class JobDeleteView(DeleteView):
    model = Job
    success_url = reverse_lazy('company:job-list')

    def get_object(self, queryset=None):
        return get_object_or_404(
            Job.objects.filter(
                company__user=self.request.user
            ), pk=self.kwargs['pk']
        )


@method_decorator(company_required, name='dispatch')
class CandidateListView(ListView):

    def get_queryset(self):
        return Candidate.objects.filter(job=self.kwargs['pk'])


@method_decorator(company_required, name='dispatch')
class JobLikeListView(DetailView):
    model = Job

    def get_object(self, queryset=None):
        job = get_object_or_404(
            Job.objects.filter(
                company__user=self.request.user
            ), pk=self.kwargs['pk']
        )
        return job

    def get_context_data(self, **kwargs):
        context = super(JobLikeListView, self).get_context_data(**kwargs)
        context['likes'] = self.get_object().likes.all()
        return context


@method_decorator(company_required, name='dispatch')
class CandidateDetailView(DetailView):
    model = Candidate

    def get_object(self, queryset=None):
        job = get_object_or_404(Job.objects.filter(company__user=self.request.user), pk=self.kwargs['job'])
        return get_object_or_404(Candidate.objects.filter(job=job), pk=self.kwargs['pk'])


@method_decorator(company_required, name='dispatch')
class CandidateStatusUpdate(View):

    def get(self, request, job, pk, action, *args, **kwargs):
        job_ = get_object_or_404(Job.objects.filter(company__user=self.request.user), pk=job)
        candidate_ = get_object_or_404(Candidate.objects.filter(job=job_), pk=pk)

        if action not in ['pen', 'app', 'acc']:
            messages.error(request, 'Wrong request parameters')
            return redirect('company:candidate-list', job)

        candidate_.status = action
        candidate_.save()
        messages.success(request, 'Candidate Status changed successfully.')

        return redirect("company:candidate-detail", job, pk)


@method_decorator(company_required, name='dispatch')
class JobStatusUpdate(View):

    def get(self, request, pk, *args, **kwargs):
        job = get_object_or_404(Job.objects.filter(company__user=self.request.user), pk=pk)

        if job.status == 'o':
            job.status = 'c'
        else:
            job.status = 'o'
        job.save()
        messages.success(request, 'Job Status changed successfully.')
        return redirect("company:job-list")
