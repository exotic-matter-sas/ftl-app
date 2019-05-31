import os
import platform
import time

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as Ec
from selenium.webdriver.support.wait import WebDriverWait

from ftl.settings import BASE_DIR, DEFAULT_TEST_BROWSER, TEST_BROWSER_HEADLESS

if 'CI' in os.environ:
    LIVE_SERVER = LiveServerTestCase
else:
    # Use StaticLiveServerTestCase when test running locally to not depend on collectstatic run
    LIVE_SERVER = StaticLiveServerTestCase


class BasePage(LIVE_SERVER):
    modal_input = '.modal-dialog input'
    modal_accept_button = '.modal-dialog .modal-footer .btn-primary'
    modal_reject_button = '.modal-dialog .modal-footer .btn-secondary'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.root_url = ''

    def setUp(self, browser=DEFAULT_TEST_BROWSER, browser_locale='en'):
        platform_system = platform.system()

        if browser == 'firefox':
            if platform_system.startswith('Linux'):
                executable_path = 'ftests/drivers/geckodriver/geckodriver64_linux'
            elif platform_system.startswith('Windows'):
                executable_path = 'ftests/drivers/geckodriver/geckodriver64.exe'
            elif platform_system.startswith('Darwin'):
                executable_path = 'ftests/drivers/geckodriver/geckodriver64_macosx'
            else:
                raise EnvironmentError(f'Platform "{platform_system}" not supported')

            profile = webdriver.FirefoxProfile()
            profile.set_preference('intl.accept_languages', browser_locale)

            options = FirefoxOptions()

            if TEST_BROWSER_HEADLESS:
                options.headless = True

            self.browser = webdriver.Firefox(executable_path=os.path.join(BASE_DIR, executable_path),
                                             firefox_profile=profile, firefox_options=options)
        elif browser == 'chrome':
            if platform_system.startswith('Linux'):
                chrome_driver_path = 'ftests/drivers/chromedriver/chromedriver_linux64'
            elif platform_system.startswith('Windows'):
                chrome_driver_path = 'ftests/drivers/chromedriver/chromedriver_win32.exe'
            elif platform_system.startswith('Darwin'):
                chrome_driver_path = 'ftests/drivers/chromedriver/chromedriver_mac64'
            else:
                raise EnvironmentError(f'Platform "{platform_system}" not supported')

            options = ChromeOptions()
            options.add_argument(f'--lang={browser_locale}')

            if TEST_BROWSER_HEADLESS:
                options.add_argument('--headless')
                if platform.system() == 'Windows':  # Needed due to Chrome bug
                    options.add_argument('--disable-gpu')

            self.browser = webdriver.Chrome(executable_path=os.path.join(BASE_DIR, chrome_driver_path),
                                            chrome_options=options)
        else:
            raise ValueError('Unsupported browser, allowed: firefox, chrome')

        # Set a default window size
        self.browser.set_window_size(1024, 768)
        # Set default timeout
        self.browser.implicitly_wait(5)

    def tearDown(self):
        self.browser.quit()

    @property
    def head_title(self):
        return self.browser.title.lower()

    def visit(self, url, absolute_url=False):
        if absolute_url:
            complete_url = url
        else:
            complete_url = self.live_server_url + url
        self.browser.get(complete_url)

    def get_elem(self, css_selector, is_visible=True):
        elem = self.browser.find_element_by_css_selector(css_selector)
        if elem.is_displayed() == is_visible:
            return elem
        else:
            raise NoSuchElementException()

    def get_elems(self, css_selector, is_visible=True):
        elems = self.browser.find_elements_by_css_selector(css_selector)
        if elems and elems[0].is_displayed() == is_visible:
            return elems
        else:
            raise NoSuchElementException()

    @staticmethod
    def _wait_for_method_to_return(method, timeout, *method_args, custom_return_validator=None,
                                   expected_exception_type=None, **method_kwargs):
        """
        Wait for the given method to return a truthy value and return it
        If custom_return_validator is provided return value will be tested against the validator
        If expected_exception is provided and an exception of the provided type occurred return None
        """
        end_time = time.time() + timeout
        polling_interval = 0.5

        while True:
            try:
                value = method(*method_args, **method_kwargs)
                if custom_return_validator and custom_return_validator(value) or value:
                    return value
            except expected_exception_type:
                return None

            time.sleep(polling_interval)
            if time.time() > end_time:
                raise TimeoutException()

    def _wait_for_method_to_raise_exception(self, method, timeout, exception_type, *method_args, **method_kwargs):
        # Use always False validator to only return if expected condition is raised
        self._wait_for_method_to_return(method, timeout, *method_args, **method_kwargs,
                                        custom_return_validator=lambda: False,
                                        expected_exception_type=exception_type)

    def wait_for_element_to_show(self, css_selector, timeout=5):
        WebDriverWait(self.browser, timeout).until(
            Ec.visibility_of_element_located((By.CSS_SELECTOR, css_selector))
        )

    def wait_for_element_to_disappear(self, css_selector, timeout=5):
        try:
            self._wait_for_method_to_raise_exception(self.get_elem, timeout, NoSuchElementException, css_selector)
        except TimeoutException:
            raise TimeoutException(f'The element "{css_selector}" doesn\'t disapear after {timeout}s')
