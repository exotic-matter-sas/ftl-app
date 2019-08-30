from ftests.pages.base_page import BasePage


class DocumentViewPage(BasePage):
    url = '/app/#/home?doc={}'

    page_body = '#document-viewer'
    document_title = '#document-viewer .modal-title > span'

    rename_document_button = '#rename-document'
    close_document_button = '#document-viewer .close'
    move_document_button = '#move-document'

    pdf_viewer = '#document-viewer iframe'

    # Move document modal
    move_document_modal = '#modal-move-document'
    move_document_target_list = '.target-folder-name'

    def rename_document(self, document_name):
        self.get_elem(self.rename_document_button).click()
        self.wait_for_elem_to_show(self.modal_input)
        self.get_elem(self.modal_input).send_keys(document_name)
        self.get_elem(self.modal_accept_button).click()

    def close_document(self):
        self.get_elem(self.close_document_button).click()
        self.wait_for_elem_to_disappear(self.page_body)

    def move_document(self, target_folder_name):
        self.get_elem(self.move_document_button).click()
        self.wait_for_elem_to_show(self.move_document_modal)

        target_list = self.get_elems(self.move_document_target_list)
        for target in target_list:
            if target.text.strip() == target_folder_name:
                target.click()
                break

        self.get_elem(self.modal_accept_button).click()
