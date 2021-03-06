#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from core.models import FTLUser, FTLOrg


class FirstOrgAndAdminCreationForm(UserCreationForm):
    org_name = forms.CharField(
        label=_("Organization name"),
        max_length=100,
        widget=forms.TextInput(attrs={"autofocus": ""}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # remove default autofocus on email field
        del self.fields["email"].widget.attrs["autofocus"]

    class Meta(UserCreationForm.Meta):
        model = FTLUser
        fields = (
            "org_name",
            "email",
        )

    def clean_email(self):
        email_ = self.cleaned_data["email"]
        return email_.lower()

    def clean_org_name(self):
        name_ = self.cleaned_data["org_name"]
        slug = slugify(name_)
        org_exists = FTLOrg.objects.filter(slug=slug).exists()
        if org_exists:
            raise forms.ValidationError(_("Organization already exists"))
        return name_

    def save(self, commit=True):
        """Set extra attributes to create an admin user"""
        user = super().save(commit=False)

        org_name_cleaned = self.cleaned_data["org_name"]

        ftl_org = FTLOrg()
        ftl_org.name = org_name_cleaned
        ftl_org.slug = slugify(org_name_cleaned)
        ftl_org.save()

        user.org = ftl_org
        user.is_superuser = True
        user.is_staff = True

        if commit:
            user.save()

        return user
