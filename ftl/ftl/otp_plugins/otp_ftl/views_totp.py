import qrcode
import qrcode.image.svg
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, HttpResponseForbidden
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.generic import FormView, DeleteView, DetailView
from django.views.generic.detail import SingleObjectMixin
from django_otp.decorators import otp_required
from django_otp.plugins.otp_totp.models import TOTPDevice

from ftl.otp_plugins.otp_ftl.forms import TOTPDeviceForm, TOTPDeviceCheckForm, TOTPDeviceConfirmForm


@method_decorator(login_required, name='dispatch')
class TOTPDeviceCheck(LoginView):
    template_name = 'otp_ftl/totpdevice_check.html'
    form_class = TOTPDeviceCheckForm
    success_url = reverse_lazy('home')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class TOTPDeviceDisplay(DetailView):
    template_name = 'otp_ftl/totpdevice_detail.html'
    model = TOTPDevice

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = TOTPDeviceConfirmForm(None, None)
        return context


@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class TOTPDeviceConfirm(SingleObjectMixin, FormView):
    template_name = 'otp_ftl/totpdevice_detail.html'
    form_class = TOTPDeviceConfirmForm
    success_url = reverse_lazy('otp_list')
    model = TOTPDevice

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        kwargs['obj'] = self.object
        return kwargs

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return HttpResponseForbidden()
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        self.object.confirmed = True
        self.object.save()

        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class TOTPDeviceDetail(View):
    def get(self, request, *args, **kwargs):
        view = TOTPDeviceDisplay.as_view()
        return view(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        view = TOTPDeviceConfirm.as_view()
        return view(request, *args, **kwargs)


@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class TOTPDeviceAdd(FormView):
    template_name = 'otp_ftl/totpdevice_form.html'
    form_class = TOTPDeviceForm

    def get_success_url(self):
        return reverse_lazy('otp_totp_detail', kwargs={'pk': self.instance.id})

    def form_valid(self, form):
        self.instance = form.save(self.request.user)
        return super().form_valid(form)


@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class TOPTDeviceViewQRCode(View):
    def get(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        device = TOTPDevice.objects.get(pk=pk, user=request.user)
        img = qrcode.make(device.config_url, image_factory=qrcode.image.svg.SvgImage)
        response = HttpResponse(content_type='image/svg+xml')
        img.save(response)

        return response


@method_decorator(login_required, name='dispatch')
@method_decorator(otp_required(if_configured=True), name='dispatch')
class TOTPDeviceDelete(DeleteView):
    template_name = 'otp_ftl/totpdevice_confirm_delete.html'
    model = TOTPDevice
    success_url = reverse_lazy('otp_list')
