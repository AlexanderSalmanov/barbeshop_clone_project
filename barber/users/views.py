from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.views import generic

from .forms import SignUpForm
# Create your views here.

class RegisterView(generic.CreateView):
    template_name = 'account/signup.html'
    form_class = SignUpForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('/')
        return super(SignupView, self).form_valid(form)
