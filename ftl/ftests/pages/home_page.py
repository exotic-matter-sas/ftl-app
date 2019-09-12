import os

from ftests.pages.base_page import BasePage
from ftests.tools import test_values as tv
from ftl.settings import BASE_DIR


class HomePage(BasePage):
    url = '/app/'

    search_input = '#search-input'
    search_button = '#search-button'
    document_list_loader = '#document-list-loader'

    profile_name = '#username'

    document_upload_input = 'input[type="file"]'
    document_upload_label = '.custom-file-label'
    submit_document_upload_button = '#upload-button'
    document_upload_loader = '#document-upload-loader'

    refresh_documents_button = '#refresh-documents'

    create_folder_button = '#create-folder'
    folders_list_buttons = 'button.folder > span:not(.spinner-border):not(.d-none)'
    folders_list_loader = '#folder-list-loader'

    batch_toolbar = '#action-selected-documents'
    unselect_all_docs_batch_button = '#unselect-all-documents'
    move_docs_batch_button = '#move-documents'
    delete_docs_batch_button = '#delete-documents'

    documents_list_container = '#documents-list'
    documents_thumbnails = '.document-thumbnail'
    documents_checkboxes = '.document-thumbnail .custom-checkbox'
    documents_titles = '.document-thumbnail .card-title'
    first_document_title = '.document-thumbnail:first-child .card-title'
    last_document_title = '.document-thumbnail:last-child .card-title'

    more_documents_button = '#more-documents'
    more_documents_loader = '#more-documents .loader'

    def wait_document_list_loaded(self):
        self.wait_for_elem_to_disappear(self.document_list_loader)

    def wait_folder_list_loaded(self):
        self.wait_for_elem_to_disappear(self.folders_list_loader)

    def wait_more_documents_loaded(self):
        self.wait_for_elem_to_disappear(self.more_documents_loader)

    def search_document(self, search_text):
        self.get_elem(self.search_input).send_keys(search_text)
        self.get_elem(self.search_button).click()
        self.wait_document_list_loaded()

    def upload_documents(self, absolute_paths=None):
        if not absolute_paths:
            absolute_paths = os.path.join(BASE_DIR, 'ftests', 'tools', 'test_documents', 'test.pdf')
        else:
            if type(absolute_paths) is not list:
                absolute_paths = [absolute_paths]
            absolute_paths = "\n".join(absolute_paths)

        self.get_elem(self.document_upload_input, is_visible=False).send_keys(absolute_paths)
        self.get_elem(self.submit_document_upload_button).click()
        self.wait_for_elem_to_disappear(self.document_upload_loader)
        # Needed in case of several upload in a row as upload success trigger a notification that hide upload button
        self.close_all_notifications()

    def create_folder(self, folder_name=tv.FOLDER1_NAME, close_notification=True):
        self.get_elem(self.create_folder_button).click()
        self.wait_for_elem_to_show(self.modal_input)
        self.get_elem(self.modal_input).send_keys(folder_name)
        self.get_elem(self.modal_accept_button).click()
        if close_notification:
            self.close_all_notifications()

    def refresh_document_list(self):
        refresh_button = self.get_elem(self.refresh_documents_button)
        refresh_button.click()

    def open_first_document(self):
        first_document_title = self.get_elem(self.first_document_title)
        first_document_title.click()

    def select_documents(self, documents_names):
        documents_list = self.get_elems(self.documents_thumbnails)
        for document in documents_list:
            if document.find_element_by_css_selector(self.documents_titles).text in documents_names:
                document.find_element_by_css_selector(self.documents_checkboxes).click()
