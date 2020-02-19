#  Copyright (c) 2019 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

from ftests.pages.base_page import BasePage


class AccountPages(BasePage):
    index_url = '/accounts/'
    update_email_url = '/accounts/email'
    update_password_url = '/accounts/password'
    two_factors_authentication_url = '/accounts/2fa/'

    success_notification = '.alert.alert-success'
    error_notification = '.alert.alert-error'

    page_title = 'h3'

    # Change email page
    new_email_input = '#email-update-form #id_email'
    submit_new_email_input = '#email-update-form [type="submit"]'

    # Change password page
    old_password_input = '#password-update-form #id_old_password'
    new_password_input = '#password-update-form #id_new_password1'
    new_password_confirmation_input = '#password-update-form #id_new_password2'
    submit_new_password_input = '#password-update-form [type="submit"]'

    # 2fa pages
    # static device
    emergency_codes_divs = '.static-device-item'
    add_emergency_codes_button = '#add-emergency-codes'
    rename_emergency_codes_buttons = '.rename-emergency-codes'
    delete_emergency_codes_buttons = '.delete-emergency-codes'
    created_codes_list = '#emergency-code-to-print li'
    print_button = 'a[onclick="print()"]'
    # totp device
    auth_app_divs = '.totp-device-item'
    add_auth_app_button = '#add-auth-app'
    unconfirmed_badges = '.totp-device-item a.badge-danger'
    totp_code_setup_input = '#id_otp_token'
    rename_auth_app_buttons = '.rename-auth-app'
    delete_auth_app_buttons = '.delete-auth-app'
    qr_code_image = 'img[src*="qrcode"]'
    # fido2 device
    security_key_divs = '.fido2-device-item'
    add_security_key_button = '#add-security-key'
    rename_security_key_buttons = '.rename-security-key'
    delete_security_key_buttons = '.delete-security-key'
    # 2fa form
    device_name_input = '#id_name'
    cancel_button = '.btn-secondary'
    confirm_button = '.btn-primary, .btn-danger'
    # 2fa check pages
    check_pages_title = 'h1'
    check_pages_device_label = 'form#user-form label'
    check_pages_device_input = '#id_otp_device'
    check_pages_code_input = '#id_otp_token'
    check_pages_alternatives_list = '#alternatives-list li'

    def update_email(self, new_email):
        self.get_elem(self.new_email_input).send_keys(new_email)
        self.get_elem(self.submit_new_email_input).click()

    def update_password(self, old_password, new_password):
        self.get_elem(self.old_password_input).send_keys(old_password)
        self.get_elem(self.new_password_input).send_keys(new_password)
        self.get_elem(self.new_password_confirmation_input).send_keys(new_password)
        self.get_elem(self.submit_new_password_input).click()

    def add_emergency_codes_set(self, codes_set_name):
        self.get_elem(self.add_emergency_codes_button).click()
        self.get_elem(self.device_name_input).send_keys(codes_set_name)
        self.get_elem(self.confirm_button).click()

    def rename_emergency_codes_set(self, new_name, set_index=0):
        self.get_elems(self.rename_emergency_codes_buttons)[set_index].click()
        self.get_elem(self.device_name_input).send_keys(new_name)
        self.get_elem(self.confirm_button).click()

    def delete_emergency_codes_set(self, set_index=0):
        self.get_elems(self.delete_emergency_codes_buttons)[set_index].click()
        self.get_elem(self.confirm_button).click()

    def add_auth_app(self, device_name):
        self.get_elem(self.add_auth_app_button).click()
        self.get_elem(self.device_name_input).send_keys(device_name)
        self.get_elem(self.confirm_button).click()

    def rename_auth_app(self, new_name, set_index=0):
        self.get_elems(self.rename_auth_app_buttons)[set_index].click()
        self.get_elem(self.device_name_input).send_keys(new_name)
        self.get_elem(self.confirm_button).click()

    def delete_auth_app(self, set_index=0):
        self.get_elems(self.delete_auth_app_buttons)[set_index].click()
        self.get_elem(self.confirm_button).click()
