#  Copyright (c) 2021 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE in the project root for more information.

from datetime import timedelta

from axes.models import AccessLog
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core import signing, management
from django.core.signing import SignatureExpired, BadSignature
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.generic import FormView
from django_otp.decorators import otp_required
from ua_parser import user_agent_parser

from account.forms import EmailSendForm, DeleteAccountForm, SettingsAccountForm
from core.ftl_account_processors_mixin import FTLAccountProcessorContextMixin
from core.models import FTLUser
from core.tasks import send_email_async


@method_decorator(login_required, name="dispatch")
@method_decorator(otp_required(if_configured=True), name="dispatch")
class AccountView(FTLAccountProcessorContextMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, "account/account_index.html", self.get_context_data())


@method_decorator(login_required, name="dispatch")
@method_decorator(otp_required(if_configured=True), name="dispatch")
class AccountActivityView(FTLAccountProcessorContextMixin, View):
    def get(self, request, *args, **kwargs):
        # When using 2FA, we have a duplicate access log. For now, exclude those from listing.
        access_logs = (
            AccessLog.objects.filter(username=request.user.email)
            .exclude(path_info__icontains="2fa")
            .order_by("-attempt_time")[:10]
        )

        access_logs_parsed = []

        for access_log in access_logs:
            access_log.parsed = user_agent_parser.Parse(access_log.user_agent)
            access_logs_parsed.append(access_log)

        context = self.get_context_data()
        context["access_log"] = access_logs_parsed

        return render(request, "account/account_activity.html", context)


@method_decorator(login_required, name="dispatch")
@method_decorator(otp_required(if_configured=True), name="dispatch")
class AccountEmailChangeView(
    FTLAccountProcessorContextMixin, SuccessMessageMixin, FormView
):
    template_name = "account/account_email.html"
    email_change_subject = "account/account_email_change_subject.txt"
    email_warn_subject = "account/account_email_warn_subject.txt"
    email_change_body = "account/account_email_change_body.txt"
    email_warn_body = "account/account_email_warn_body.txt"
    form_class = EmailSendForm
    success_url = reverse_lazy("account_index")
    success_message = _("A confirmation email has been sent.")

    def get_email_context(self, activation_key):
        scheme = "https" if self.request.is_secure() else "http"
        return {
            "scheme": scheme,
            "activation_key": activation_key,
            "expiration_minutes": 10,
            "site": get_current_site(self.request),
        }

    def form_valid(self, form):
        email_ = form.cleaned_data["email"]

        # Encode new email and sign it
        activation_key = signing.dumps(
            obj={
                "id": self.request.user.id,
                "old_email": self.request.user.email,
                "new_email": email_,
            },
            salt="email_change",
        )

        # Email sent to the new address for validation
        subject_change = render_to_string(
            template_name=self.email_change_subject,
            context=self.get_email_context(activation_key),
            request=self.request,
        )
        subject_change = "".join(subject_change.splitlines())
        message_change = render_to_string(
            template_name=self.email_change_body,
            context=self.get_email_context(activation_key),
            request=self.request,
        )

        # Email sent to the current address for notification
        subject_warn = render_to_string(
            template_name=self.email_warn_subject, context={}, request=self.request
        )
        subject_warn = "".join(subject_warn.splitlines())
        message_warn = render_to_string(
            template_name=self.email_warn_body, context={}, request=self.request
        )

        self.request.user.email_user(
            subject_warn, message_warn, settings.DEFAULT_FROM_EMAIL
        )

        # Send to new user email
        send_email_async.delay(
            subject_change, message_change, settings.DEFAULT_FROM_EMAIL, [email_]
        )

        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
@method_decorator(otp_required(if_configured=True), name="dispatch")
class AccountEmailChangeValidateView(View):
    success_message = _("Email successfully updated.")
    expired_message = _("The link expired. Please try again.")
    incorrect_signature = _("Could not validate your email. Please try again.")

    def get(self, request, *args, **kwargs):
        if "token" in kwargs:
            # check for validity
            try:
                email_change_request = signing.loads(
                    kwargs["token"], salt="email_change", max_age=timedelta(minutes=10)
                )

                user = self.request.user

                if (
                    user.email == email_change_request["old_email"]
                    and user.id == email_change_request["id"]
                ):
                    user.email = email_change_request["new_email"]
                    user.save()
                    messages.success(self.request, self.success_message)
                else:
                    messages.error(self.request, self.incorrect_signature)
            except SignatureExpired:
                messages.error(self.request, self.expired_message)
            except BadSignature:
                messages.error(self.request, self.incorrect_signature)

        return HttpResponseRedirect(reverse_lazy("account_index"))


@method_decorator(login_required, name="dispatch")
@method_decorator(otp_required(if_configured=True), name="dispatch")
class AccountPasswordView(
    FTLAccountProcessorContextMixin, SuccessMessageMixin, PasswordChangeView
):
    template_name = "account/account_password.html"
    form_class = PasswordChangeForm
    success_url = reverse_lazy("account_index")
    success_message = _("Password updated!")
    email_warn_subject = "account/account_password_warn_subject.txt"
    email_warn_body = "account/account_password_warn_body.txt"

    def form_valid(self, form):
        # Email sent to the current address for notification
        subject_warn = render_to_string(
            template_name=self.email_warn_subject, context={}, request=self.request
        )
        subject_warn = "".join(subject_warn.splitlines())
        message_warn = render_to_string(
            template_name=self.email_warn_body, context={}, request=self.request
        )

        self.request.user.email_user(
            subject_warn, message_warn, settings.DEFAULT_FROM_EMAIL
        )

        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
@method_decorator(otp_required(if_configured=True), name="dispatch")
class AccountImportExportView(FTLAccountProcessorContextMixin, View):
    def get(self, request, *args, **kwargs):
        return render(
            request,
            "account/account_import_export.html",
            context=self.get_context_data(),
        )


@method_decorator(login_required, name="dispatch")
@method_decorator(otp_required(if_configured=True), name="dispatch")
class AccountDeleteView(FTLAccountProcessorContextMixin, SuccessMessageMixin, FormView):
    template_name = "account/account_delete.html"
    form_class = DeleteAccountForm
    success_url = reverse_lazy("login")
    success_message = _("Your account was deleted.")
    email_warn_subject = "account/account_delete_warn_subject.txt"
    email_warn_body = "account/account_delete_warn_body.txt"

    def get_context_data(self, **kwargs):
        context_ = super().get_context_data(**kwargs)

        count_admins = FTLUser.objects.filter(is_superuser=True).count()

        if count_admins <= 1 and self.request.user.is_superuser:
            context_["last_admin_no_delete"] = True

        return context_

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        management.call_command("disable_account", org_slug=self.request.user.org.slug)

        subject_warn = render_to_string(
            template_name=self.email_warn_subject, context={}, request=self.request
        )
        subject_warn = "".join(subject_warn.splitlines())
        message_warn = render_to_string(
            template_name=self.email_warn_body, context={}, request=self.request
        )

        self.request.user.email_user(
            subject_warn, message_warn, settings.DEFAULT_FROM_EMAIL
        )

        return super().form_valid(form)


@method_decorator(login_required, name="dispatch")
@method_decorator(otp_required(if_configured=True), name="dispatch")
class AccountSettingsView(
    FTLAccountProcessorContextMixin, SuccessMessageMixin, FormView
):
    template_name = "account/account_settings.html"
    form_class = SettingsAccountForm
    success_url = reverse_lazy("account_index")
    success_message = _("Your settings were saved.")

    def get_initial(self):
        initial = super().get_initial()
        initial["tz"] = self.request.user.tz
        initial["lang"] = self.request.user.lang
        return initial

    def form_valid(self, form):
        tz_ = form.cleaned_data["tz"]
        lang_ = form.cleaned_data["lang"]

        user = self.request.user
        user.tz = tz_
        user.lang = lang_
        user.save(update_fields=["tz", "lang"])

        return super().form_valid(form)
