from django.contrib import messages
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView, RedirectView

from core.models import FTLOrg, permissions_names_to_objects, FTL_PERMISSIONS_USER
from ftl.forms import FTLUserCreationForm


class CreateFTLUserFormView(FormView):
    template_name = 'ftl/signup.html'
    form_class = FTLUserCreationForm

    def get_success_url(self):
        # We redefine the method instead of the field because the success url is dynamic (org slug)
        return reverse('signup_success', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        org = get_object_or_404(FTLOrg.objects.filter(slug=self.kwargs['org_slug']))
        data['org_name'] = org.name
        return data

    def form_valid(self, form):
        org = get_object_or_404(FTLOrg, slug=self.kwargs['org_slug'])
        instance = form.save(commit=False)
        instance.org = org
        instance.save()

        instance.user_permissions.set(permissions_names_to_objects(FTL_PERMISSIONS_USER))

        instance.save()

        return super().form_valid(form)


def signup_success(request, org_slug):
    context = {
        'org_slug': org_slug,
    }

    return render(request, 'ftl/signup_success.html', context)


class SetMessageAndRedirectView(RedirectView):
    """
    View for showing a flash message
    """
    message_type = messages.SUCCESS
    message = None

    def get(self, request, *args, **kwargs):
        messages.add_message(request, self.message_type, self.message)
        return super().get(request, *args, **kwargs)


class PasswordResetAsked(SetMessageAndRedirectView):
    url = reverse_lazy('login')
    message = _(
        'We’ve emailed you instructions for setting your password, if an account exists with the email '
        'you entered. You should receive them shortly (check your spam folder if that\'s not the case).')


class PasswordResetDone(SetMessageAndRedirectView):
    url = reverse_lazy('login')
    message = _('Your password has been set. You may go ahead and log in now.')
