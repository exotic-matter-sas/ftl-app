import platform
import os

from selenium import webdriver
from django.test import LiveServerTestCase
from unittest import skip

from ftl.settings import BASE_DIR
from ftests import _test_values as tv


class LandingPageTests(LiveServerTestCase):

    def setUp(self):
        if platform.system().startswith('Linux'):
            executable_path = 'ftests/geckodriver/geckodriver64_linux'
        elif platform.system().startswith('Windows'):
            executable_path = 'ftests/geckodriver/geckodriver64.exe'
        elif platform.system().startswith('Darwin'):
            executable_path = 'ftests/geckodriver/geckodriver64_linux'
        else:
            raise EnvironmentError(f'Platform "{platform.system()}" not supported')

        self.browser = webdriver.Firefox(executable_path=os.path.join(BASE_DIR, executable_path))

    def tearDown(self):
        self.browser.quit()

    def create_user(self, user_type):
        admin_form = self.browser.find_element_by_id(f'{user_type}-form')
        username_input = admin_form.find_element_by_id('id_username')
        email_address_input = admin_form.find_element_by_id('id_email')
        password_input = admin_form.find_element_by_id('id_password1')
        password_confirmation_input = admin_form.find_element_by_id('id_password2')
        submit_input = admin_form.find_element_by_css_selector('[type="submit"]')

        username_input.send_keys(getattr(tv, f'{user_type.upper()}_USERNAME'))
        email_address_input.send_keys(getattr(tv, f'{user_type.upper()}_EMAIL'))
        password_input.send_keys(getattr(tv, f'{user_type.upper()}_PASS'))
        password_confirmation_input.send_keys(getattr(tv, f'{user_type.upper()}_PASS'))
        submit_input.click()

    def create_first_organization(self):
        organization_form = self.browser.find_element_by_id('organization-form')
        name_input = organization_form.find_element_by_id('id_name')
        submit_input = organization_form.find_element_by_css_selector('[type="submit"]')

        name_input.send_keys(tv.ORG_NAME)
        submit_input.click()

    def test_landing_page_display_properly_on_first_visit(self):
        """Landing page display properly on first visit"""
        # Admin user have just install ftl-app and display it for the first time
        self.browser.get(self.live_server_url)

        # The landing page welcome the user and ask him to complete 1st step : admin creation
        self.assertIn('Ftl-app', self.browser.title)
        self.assertIn('Admin creation', self.browser.find_elements_by_css_selector('h2')[0].text)

    def test_landing_page_display_properly_after_admin_creation(self):
        """Landing page display properly after admin creation"""
        # Admin user have just install ftl-app and display it for the first time
        self.browser.get(self.live_server_url)

        # He fulfill the admin creation form and close his browser
        self.create_user('admin')
        self.browser.quit()

        # He come back later and display ftl-app again
        self.setUp()
        self.browser.get(self.live_server_url)

        # The landing page welcome the user and ask him to complete 2nd step : organization creation
        self.assertIn('Ftl-app', self.browser.title)
        self.assertIn('First organization creation', self.browser.find_elements_by_css_selector('h2')[0].text)

    def test_landing_page_redirect_to_user_login_when_setup_complete(self):
        """Landing page redirect to user login page when setup complete"""
        # Admin user have just install ftl-app and display it for the first time
        self.browser.get(self.live_server_url)

        # He fulfill the admin creation form
        self.create_user('admin')
        # And then the first organisation form
        self.create_first_organization()

        # A success page appears mentioning the urls for admin and user signup page
        self.assertIn('Setup completed', self.browser.title)
        admin_login_link = self.browser.find_element_by_id('admin-login')
        self.assertIn('/admin', admin_login_link.get_attribute('href'))

        user_signup_link = self.browser.find_element_by_id('user-signup')
        self.assertIn('/signup', user_signup_link.get_attribute('href'))

        # Display ftl-app again now redirect to user login page
        self.browser.get(self.live_server_url)
        self.assertIn('Login', self.browser.title)

    def test_admin_user_can_login_in_django_admin(self):
        """Admin user can login in Django admin"""
        # Admin user have just install ftl-app and display it for the first time
        self.browser.get(self.live_server_url)
        # He fulfill the admin creation form
        self.create_user('admin')
        # And then the first organisation form
        self.create_first_organization()

        # He click on link to login to admin portal
        admin_login_link = self.browser.find_element_by_id('admin-login')
        admin_login_link.click()

        admin_login_form = self.browser.find_element_by_id('login-form')
        username_input = admin_login_form.find_element_by_id('id_username')
        password_input = admin_login_form.find_element_by_id('id_password')
        submit_input = admin_login_form.find_element_by_css_selector('[type="submit"]')

        username_input.send_keys(tv.ADMIN_USERNAME)
        password_input.send_keys(tv.ADMIN_PASS)
        submit_input.click()

        # Django admin display properly
        self.assertIn(f'welcome, {tv.ADMIN_USERNAME}', self.browser.find_element_by_id('user-tools').text.lower())

    def test_user_can_signup_to_first_organization(self):
        """User can signup to first organization"""
        # Admin user have just install ftl-app and display it for the first time
        self.browser.get(self.live_server_url)
        # He fulfill the admin creation form
        self.create_user('admin')
        # And then the first organisation form
        self.create_first_organization()
        # He copy the link for signup to user and send it to the first user
        user_signup_link = self.browser.find_element_by_id('user-signup')

        # First user click on the link to signup to first organization
        user_signup_link.click()

        # The name of the first organization is displayed and user can create his account
        self.assertIn(tv.ORG_NAME, self.browser.find_element_by_css_selector('h1').text)
        self.create_user('user')

        # Success message appears when account creation is complete
        self.assertIn('Congratulations', self.browser.find_element_by_css_selector('h1').text)

    @skip('Need to be fixed')
    def test_user_can_access_login_page_of_first_organization(self):
        """User access login page of first organization"""
        # Admin user create admin user and first org and send link to first user
        self.browser.get(self.live_server_url)
        self.create_user('admin')
        self.create_first_organization()
        user_signup_link = self.browser.find_element_by_id('user-signup')

        # First user click on the link and signup to first organization
        user_signup_link.click()
        self.create_user('user')

        # He click on link to login
        user_login_link = self.browser.find_element_by_id('user-login')
        user_login_link.click()

        # The name of the first organization is displayed on login page
        login_header = self.browser.find_element_by_css_selector('h1').text
        self.assertIn('login', login_header.lower())
        self.assertIn(tv.ORG_NAME, login_header)  # TODO check for slug instead of organization name
