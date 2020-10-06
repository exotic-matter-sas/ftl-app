#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import re
from datetime import datetime, timezone, timedelta
from unittest import skip
from unittest.mock import patch, Mock

from django.conf.global_settings import SESSION_COOKIE_AGE
from django.contrib import messages
from django.contrib.auth.signals import user_logged_out
from django.contrib.sessions.backends.base import SessionBase
from django.core import mail
from django.test import TestCase, RequestFactory
from django.utils import timezone as django_timezone
from django.urls import reverse_lazy
from django_otp.middleware import OTPMiddleware
from django_otp.oath import TOTP
from django_otp.plugins.otp_static.models import StaticDevice

from core.models import FTLUser, FTL_PERMISSIONS_USER
from ftests.test_account import TotpDevice2FATests, totp_time_setter, totp_time_property, mocked_totp_time_setter, \
    mocked_verify_user
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import (
    setup_org,
    setup_admin,
    setup_user,
    setup_authenticated_session,
    setup_2fa_totp_device,
    setup_2fa_static_device,
    setup_2fa_fido2_device
)
from ftl.otp_plugins.otp_ftl.views_static import StaticDeviceCheck, StaticDeviceAdd
from .forms import FTLUserCreationForm


class FtlPagesTests(TestCase):
    def test_index_redirects(self):
        """Index redirect to correct page according to setup state"""
        response = self.client.get("", follow=True)
        self.assertRedirects(response, reverse_lazy("setup:create_admin"))

        org = setup_org()
        setup_admin(org)
        response = self.client.get("", follow=True)
        self.assertRedirects(
            response, f"{reverse_lazy('login')}?next={reverse_lazy('home')}"
        )

    @skip("Multi users feature disabled")
    def test_signup_returns_correct_html(self):
        """Signup page returns correct html"""
        org = setup_org()

        response = self.client.get(f"/signup/{org.slug}/")
        self.assertContains(response, "Create your account")
        self.assertTemplateUsed(response, "ftl/registration/signup.html")

    @skip("Multi users feature disabled")
    def test_signup_context(self):
        """Signup page get proper context"""
        org = setup_org()

        response = self.client.get(f"/signup/{org.slug}/")
        self.assertEqual(response.context["org_name"], org.name)
        self.assertIsInstance(response.context["form"], FTLUserCreationForm)

    @skip("Multi users feature disabled")
    def test_signup_get_success_url(self):
        """Signup get_success_url working properly"""
        org = setup_org()

        response = self.client.post(
            f"/signup/{org.slug}/",
            {
                "email": tv.USER1_EMAIL,
                "password1": tv.USER1_PASS,
                "password2": tv.USER1_PASS,
            },
        )

        self.assertRedirects(
            response, reverse_lazy("signup_success"), fetch_redirect_response=False
        )

    def test_signup_success_returns_correct_html(self):
        """Signup success page returns correct html"""

        response = self.client.get(f"/signup/success/")
        self.assertContains(response, "verify your email")
        self.assertTemplateUsed(response, "ftl/registration/signup_success.html")

    @skip("Multi users feature disabled")
    def test_user_permissions_signup(self):
        org = setup_org()

        self.client.post(
            f"/signup/{org.slug}/",
            {
                "email": tv.USER1_EMAIL,
                "password1": tv.USER1_PASS,
                "password2": tv.USER1_PASS,
            },
        )

        user = FTLUser.objects.get(email=tv.USER1_EMAIL)
        self.assertIsNotNone(user)

        # To test permission, we need an account activated otherwise the permissions are not set
        self.assertEqual(len(mail.outbox), 1)
        activate_link = re.search(
            r"(https?://.+/accounts/activate/.+/)", mail.outbox[0].body
        )
        response = self.client.get(activate_link.group(1), follow=True)
        self.assertEqual(response.status_code, 200)
        user = FTLUser.objects.get(email=tv.USER1_EMAIL)
        self.assertTrue(user.has_perms(FTL_PERMISSIONS_USER))

    @patch.object(user_logged_out, "send")
    def test_logout_call_proper_signal(self, mocked_signal):
        # Setup org, admin, user and log the user
        org = setup_org()
        setup_admin(org)
        user = setup_user(org)
        setup_authenticated_session(self.client, org, user)

        self.client.get("/logout/")

        mocked_signal.assert_called_once()

    @patch.object(messages, "success")
    def test_logout_signal_trigger_django_messages(self, messages_mocked):
        # Setup org, admin, user and log the user
        org = setup_org()
        setup_admin(org)
        user = setup_user(org)
        setup_authenticated_session(self.client, org, user)

        message_to_display_on_login_page = "bingo!"
        messages_mocked.return_value = message_to_display_on_login_page
        mocked_request = Mock()
        mocked_request.GET = {}
        mocked_request.axes_attempt_time = datetime.now()
        user_logged_out.send(self.__class__, request=mocked_request, user=user)

        messages_mocked.assert_called_once()

########################
# Otp_ftl plugin views #
########################


class OTPCheckViewTests(TestCase):
    def setUp(self):
        # Setup org, admin, user, 2fa totp device already setup and user is logged
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        setup_authenticated_session(self.client, self.org, self.user)
        # reset mock
        self.addCleanup(totp_time_setter.reset_mock, side_effect=True)

    @patch.object(TOTP, "time", totp_time_property)
    def test_session_timeout_reduced_during_2fa_check(self):
        totp_device = setup_2fa_totp_device(
            self.user, secret_key=TotpDevice2FATests.secret_key
        )
        totp_time_setter.side_effect = mocked_totp_time_setter

        self.client.get("/app/", follow=True)

        # During 2fa session duration must be less than 10 mins
        now = datetime.now(timezone.utc)
        cookie_expiration_time = self.client.cookies["sessionid"]["expires"]
        cookie_expiration_time = datetime.strptime(
            cookie_expiration_time, "%a, %d %b %Y %H:%M:%S GMT"
        )
        cookie_expiration_time = django_timezone.make_aware(
            cookie_expiration_time, timezone.utc
        )
        delta = cookie_expiration_time - now
        self.assertLessEqual(delta, timedelta(minutes=10))

        self.client.post(
            "/accounts/2fa/totp/check/",
            {
                "otp_device": totp_device.persistent_id,
                "otp_token": TotpDevice2FATests.valid_token,
            },
            follow=True,
        )

        # After 2FA check session have to be restore to default value
        cookie_expiration_time = self.client.cookies["sessionid"]["expires"]
        cookie_expiration_time = datetime.strptime(
            cookie_expiration_time, "%a, %d %b %Y %H:%M:%S GMT"
        )
        cookie_expiration_time = django_timezone.make_aware(
            cookie_expiration_time, timezone.utc
        )
        delta = cookie_expiration_time - now

        self.assertAlmostEqual(round(delta.total_seconds()), SESSION_COOKIE_AGE, delta=5)

    def test_otp_check_redirect_to_proper_view(self):
        # Given no 2fa devices are setup
        response = self.client.get("/app/")
        # Home page is displayed
        self.assertTemplateUsed(response, "core/home.html")

        # Given a static device is setup
        setup_2fa_static_device(self.user, codes_list=tv.STATIC_DEVICE_CODES_LIST)
        response = self.client.get("/app/", follow=True)
        # User is redirect to otp_static_check
        self.assertRedirects(
            response, reverse_lazy("otp_static_check")
        )

        # Given static + totp device are setup
        setup_2fa_totp_device(self.user)
        response = self.client.get("/app/", follow=True)
        # User is redirect to otp_static_check
        self.assertRedirects(
            response, reverse_lazy("otp_totp_check")
        )

        # Given static + totp device are setup
        setup_2fa_fido2_device(self.user)
        response = self.client.get("/app/", follow=True)
        # User is redirect to otp_static_check
        self.assertRedirects(
            response, reverse_lazy("otp_fido2_check")
        )


class OTPFtlViewsTests(TestCase):
    def setUp(self):
        # Setup org, user
        self.org = setup_org()
        self.user = setup_user(self.org)
        setup_authenticated_session(self.client, self.org, self.user)
        # mock OTPMiddleware._verify_user() to skip check page
        self.middleware_patcher = patch.object(
            OTPMiddleware, "_verify_user", mocked_verify_user
        )
        self.middleware_patcher.start()
        self.addCleanup(
            patch.stopall
        )  # ensure mock is remove after each test, even if the test crash
        self.addCleanup(totp_time_setter.reset_mock, side_effect=True)

    def test_otp_list_returns_correct_html(self):
        # Make TOTP.time setter set a hard coded secret_time to always be able to confirm app with the same valid_token
        totp_time_setter.side_effect = mocked_totp_time_setter

        # Given no 2fa devices are setup
        response = self.client.get("/accounts/2fa/")
        self.assertContains(response, "Protect your Paper Matter account")
        self.assertTemplateUsed(response, "otp_ftl/device_list.html")

        # Given 2fa devices are setup
        setup_2fa_static_device(self.user, codes_list=tv.STATIC_DEVICE_CODES_LIST)
        setup_2fa_fido2_device(self.user)
        setup_2fa_totp_device(self.user)

        response = self.client.get("/accounts/2fa/")
        self.assertContains(response, "Emergency codes")
        self.assertContains(response, "Security keys (U2F/FIDO2)")
        self.assertContains(response, "Authenticator apps")

    def test_otp_list_context(self):
        # Make TOTP.time setter set a hard coded secret_time to always be able to confirm app with the same valid_token
        totp_time_setter.side_effect = mocked_totp_time_setter

        # Given 2fa devices are setup
        static_device_1 = setup_2fa_static_device(self.user, "SD1", codes_list=tv.STATIC_DEVICE_CODES_LIST)
        static_device_2 = setup_2fa_static_device(self.user, "SD2", codes_list=tv.STATIC_DEVICE_CODES_LIST)
        totp_device_1 = setup_2fa_totp_device(self.user, "TD1")
        totp_device_2 = setup_2fa_totp_device(self.user, "TD2")
        fido2_device_1 = setup_2fa_fido2_device(self.user, "FD1")
        fido2_device_2 = setup_2fa_fido2_device(self.user, "FD2")

        response = self.client.get("/accounts/2fa/")

        self.assertCountEqual(response.context["static_devices"],
                              [static_device_1, static_device_2])
        self.assertCountEqual(response.context["totp_devices"],
                              [totp_device_1, totp_device_2])
        self.assertCountEqual(response.context["fido2_devices"],
                              [fido2_device_1, fido2_device_2])


class OTPFtlViewsStaticTests(TestCase):
    def setUp(self):
        # Setup org, user, a static device and the user is logged
        self.org = setup_org()
        self.user = setup_user(self.org)
        self.static_device = setup_2fa_static_device(self.user, codes_list=tv.STATIC_DEVICE_CODES_LIST)
        setup_authenticated_session(self.client, self.org, self.user)
        # mock OTPMiddleware._verify_user() to skip check page
        self.middleware_patcher = patch.object(
            OTPMiddleware, "_verify_user", mocked_verify_user
        )
        self.middleware_patcher.start()
        self.addCleanup(
            patch.stopall
        )  # ensure mock is remove after each test, even if the test crash
        self.addCleanup(totp_time_setter.reset_mock, side_effect=True)

    def test_otp_static_check_returns_correct_html(self):
        response = self.client.get("/accounts/2fa/static/check/")

        self.assertTemplateUsed(response, "otp_ftl/staticdevice_check.html")

    def test_otp_static_check_context(self):
        response = self.client.get("/accounts/2fa/static/check/")

        self.assertEqual(response.context["have_static"], True)
        self.assertEqual(response.context["have_fido2"], False)
        self.assertEqual(response.context["have_totp"], False)

        # given user setup static + fido2 devices
        setup_2fa_fido2_device(self.user)

        response = self.client.get("/accounts/2fa/static/check/")

        self.assertEqual(response.context["have_static"], True)
        self.assertEqual(response.context["have_fido2"], True)
        self.assertEqual(response.context["have_totp"], False)
        # given user setup static + fido2 + totp devices
        setup_2fa_totp_device(self.user)

        response = self.client.get("/accounts/2fa/static/check/")

        self.assertEqual(response.context["have_static"], True)
        self.assertEqual(response.context["have_fido2"], True)
        self.assertEqual(response.context["have_totp"], True)

    def test_otp_static_check_success_url(self):
        # Given there is no next querystring set
        request_factory = RequestFactory()
        request = request_factory.get("/accounts/2fa/static/check/")
        request.user = self.user
        request.session = SessionBase()

        otp_static_check_view = StaticDeviceCheck()
        otp_static_check_view.request = request

        # Success url is set to Home
        self.assertEqual(otp_static_check_view.get_success_url(), reverse_lazy("home"))

        # Given there is a safe url in next querystring
        request = request_factory.get("/accounts/2fa/static/check/")
        request.user = self.user
        request.session = SessionBase()
        request.session["next"] = reverse_lazy("account_index")

        otp_static_check_view = StaticDeviceCheck()
        otp_static_check_view.request = request

        # Success url is set to next url
        self.assertEqual(otp_static_check_view.get_success_url(), reverse_lazy("account_index"))

        # Given there is a unsafe url in next querystring
        request = request_factory.get("/accounts/2fa/static/check/")
        request.user = self.user
        request.session = SessionBase()
        request.session["next"] = "https://buymybitcoins.plz"

        otp_static_check_view = StaticDeviceCheck()
        otp_static_check_view.request = request

        # Success url is set NOT set to next url, it default to Home
        self.assertEqual(otp_static_check_view.get_success_url(), reverse_lazy("home"))

    def test_otp_static_detail_returns_correct_html(self):
        response = self.client.get(f"/accounts/2fa/static/{self.static_device.id}/")

        self.assertTemplateUsed(response, "otp_ftl/staticdevice_detail.html")

    def test_otp_static_update_returns_correct_html(self):
        response = self.client.get(f"/accounts/2fa/static/{self.static_device.id}/update/")

        self.assertTemplateUsed(response, "otp_ftl/device_update.html")

    def test_otp_static_add_returns_correct_html(self):
        response = self.client.get(f"/accounts/2fa/static/")

        self.assertTemplateUsed(response, "otp_ftl/staticdevice_form.html")

    def test_otp_static_add_get_success_url(self):
        response = self.client.post(
            f"/accounts/2fa/static/",
            data={
                "name": tv.STATIC_DEVICE_NAME
            }
        )

        # get_success_url redirect to the detail of the static device just created
        self.assertRedirects(response, reverse_lazy(
            "otp_static_detail",
            kwargs={"pk": StaticDevice.objects.last().id}
        ))

    def test_otp_static_add_form_valid_set_data(self):
        request_factory = RequestFactory()
        request = request_factory.post("/accounts/2fa/static/check/", {"name": tv.STATIC_DEVICE_NAME})
        request.user = self.user

        otp_static_add_view = StaticDeviceAdd()
        otp_static_add_view.request = request
        form = otp_static_add_view.get_form(otp_static_add_view.form_class)
        form.is_valid()
        otp_static_add_view.form_valid(form)

        # instance attribute is populate the model of the static device just created
        self.assertEqual(otp_static_add_view.instance, StaticDevice.objects.last())

    def test_otp_static_delete_returns_correct_html(self):
        response = self.client.get(f"/accounts/2fa/static/{self.static_device.id}/delete/")

        self.assertTemplateUsed(response, "otp_ftl/device_confirm_delete.html")
