#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django_otp.decorators import otp_required
from oauth2_provider import views


@method_decorator(login_required, name="dispatch")
@method_decorator(otp_required(if_configured=True), name="dispatch")
class FTLAuthorizationView(views.AuthorizationView):
    pass
