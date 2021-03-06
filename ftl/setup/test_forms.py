#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.

from django.test import TestCase

from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_user
from .forms import FirstOrgAndAdminCreationForm


class FtlAdminCreationFormTests(TestCase):
    def test_form_render_email_input(self):
        """Form render email input"""
        form = FirstOrgAndAdminCreationForm()
        self.assertIn("Email address", form.as_p())

    def test_form_refuse_blank_email(self):
        """Form refuse blank email"""
        form = FirstOrgAndAdminCreationForm(
            data={
                "org_name": tv.ORG_NAME_1,
                "email": "",
                "password1": tv.USER1_PASS,
                "password2": tv.USER1_PASS,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_form_refuse_non_unique_email(self):
        """Form refuse non unique email"""
        org = setup_org()
        setup_user(org, email=tv.USER1_EMAIL)

        form = FirstOrgAndAdminCreationForm(
            data={
                "org_name": tv.ORG_NAME_2,
                "email": tv.USER1_EMAIL,
                "password1": tv.USER2_PASS,
                "password2": tv.USER2_PASS,
            }
        )
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_admin_creation_permissions(self):
        form = FirstOrgAndAdminCreationForm(
            data={
                "org_name": tv.ORG_NAME_1,
                "email": tv.ADMIN1_EMAIL,
                "password1": tv.ADMIN1_PASS,
                "password2": tv.ADMIN1_PASS,
            }
        )

        user = form.save()
        self.assertIsNotNone(user)
        self.assertTrue(user.is_superuser)
