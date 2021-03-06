#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the Business Source License. See LICENSE at project root for more information.

from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import APIException


ERROR_CODES_DETAILS = {
    "folder_name_unique_for_org_level": _("A folder with this name already exist"),
    "folder_parent_invalid": _("A folder can't be move inside one of its children"),
    "ftl_folder_not_found": _("Specified ftl_folder doesn't exist"),
    "ftl_document_md5_mismatch": _(
        "Document has been corrupted during upload, please retry"
    ),
    "ftl_document_type_unsupported": _("Unsupported document format"),
    "ftl_missing_file_or_json_in_body": _(
        "Missing parameter `file` or/and `json` in POST body"
    ),
    "ftl_file_empty": _("The file is empty"),
    "ftl_thumbnail_generation_error": _("The thumbnail could not be decoded"),
    "ftl_too_many_reminders": _(
        "Too many reminders have been created for this document"
    ),
    "ftl_one_reminder_per_day": _("Only one reminder can be set per date and per user"),
}


class BadRequestError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _("Bad request")
    default_code = "bad_request"


class PluginUnsupportedStorage(Exception):
    pass
