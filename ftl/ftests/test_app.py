#  Copyright (c) 2020 Exotic Matter SAS. All rights reserved.
#  Licensed under the BSL License. See LICENSE in the project root for license information.

import os
import time
from string import ascii_lowercase
from unittest import skipIf
from unittest.mock import patch

from selenium.common.exceptions import NoSuchElementException

from core.processing.ftl_processing import FTLDocumentProcessing
from ftests.pages.base_page import NODE_SERVER_RUNNING
from ftests.pages.document_viewer_modal import DocumentViewerModal
from ftests.pages.home_page import HomePage
from ftests.pages.manage_folder_page import ManageFolderPage
from ftests.pages.move_documents_modal import MoveDocumentsModal
from ftests.pages.user_login_page import LoginPage
from ftests.tools import test_values as tv
from ftests.tools.setup_helpers import setup_org, setup_admin, setup_user, setup_document, setup_folder, \
    setup_temporary_file
from ftl.settings import DEV_MODE, BASE_DIR, DEFAULT_TEST_BROWSER, TEST_BROWSER_HEADLESS


class HomePageTests(LoginPage, HomePage, DocumentViewerModal):
    def setUp(self, **kwargs):
        # first org, admin, user are already created, user is already logged on home page
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        self.visit(LoginPage.url)
        self.log_user()

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    @patch.object(FTLDocumentProcessing, 'apply_processing')
    def test_upload_document_to_root(self, mock_apply_processing):
        # User upload a document
        self.upload_documents()

        # Document appears as the first document of the list
        self.assertEqual(tv.DOCUMENT1_TITLE, self.get_elem_text(self.first_document_title))

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    @patch.object(FTLDocumentProcessing, 'apply_processing')
    def test_upload_document_to_subfolder(self, mock_apply_processing):
        # User has already created a folder
        setup_folder(self.org)
        self.visit(HomePage.url)

        # User upload open its subfolder and upload a document
        self.get_elem(self.folders_list_buttons).click()
        self.upload_documents()

        # Document appears as the first document of the list
        self.assertEqual(tv.DOCUMENT1_TITLE, self.get_elem_text(self.first_document_title))
        # Document doesn't appears in root folder
        self.visit(HomePage.url)
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.first_document_title)

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    @patch.object(FTLDocumentProcessing, 'apply_processing')
    def test_upload_documents_to_root(self, mock_apply_processing):
        # User upload several documents
        documents_to_upload = [
            os.path.join(BASE_DIR, 'ftests', 'tools', 'test_documents', 'test.pdf'),
            os.path.join(BASE_DIR, 'ftests', 'tools', 'test_documents', 'test.pdf'),
            os.path.join(BASE_DIR, 'ftests', 'tools', 'test_documents', 'test.pdf')
        ]
        self.upload_documents(documents_to_upload)

        # Document appears as the first document of the list
        self.assertEqual(3, len(self.get_elems(self.documents_thumbnails)))

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_display_document(self):
        # User has already added a document
        setup_document(self.org, self.user)
        self.refresh_documents_list()

        # User click on the first listed document
        self.open_first_document()
        # User can see the pdf inside the pdf viewer
        pdf_viewer_iframe = self.get_elem(self.pdf_viewer_iframe)
        self.browser.switch_to_frame(pdf_viewer_iframe)
        pdf_viewer_iframe_title = self.get_elem('title', False).get_attribute("innerHTML")

        self.assertEqual(pdf_viewer_iframe_title, 'PDF.js viewer')

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_create_folder(self):
        # User create a folder
        self.create_folder()

        # The folder properly appears in the folder list
        self.assertEqual(tv.FOLDER1_NAME, self.get_elem_text(self.folders_list_buttons))

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_create_folder_with_name_already_used(self):
        # A folder already exist
        existing_folder = setup_folder(self.org)
        # Refresh page to display folder
        self.visit(HomePage.url)
        self.wait_folder_list_loaded()

        # User try to create a second folder at the same level using the existing folder name
        self.create_folder(folder_name=existing_folder.name, close_notification=False)

        # The second folder isn't created and an error message appears
        self.assertEqual(len(self.get_elems(self.folders_list_buttons)), 1,
                         'The second folder should not have been created because its name is already used')
        self.assertIn('name already exist', self.get_elem_text(self.error_notification),
                      'An error message should have been displayed to user to tell him folder creation failed because'
                      ' of duplicate name')

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_create_folder_tree(self):
        # User create a folder at root level
        self.create_folder(tv.FOLDER1_NAME)
        # User open previous folder and create a subfolder
        self.get_elem(self.folders_list_buttons).click()
        self.create_folder(tv.FOLDER2_NAME)
        # User open previous folder and create another subfolder
        self.get_elem(self.folders_list_buttons).click()
        self.create_folder(tv.FOLDER3_NAME)

        # Check if each folder have been created at proper level
        self.visit(HomePage.url)
        self.wait_for_elem_to_show(self.folders_list_buttons)
        self.assertEqual(tv.FOLDER1_NAME, self.get_elem_text(self.folders_list_buttons))
        self.get_elem(self.folders_list_buttons).click()
        self.wait_for_elem_to_show(self.folders_list_buttons)
        self.assertEqual(tv.FOLDER2_NAME, self.get_elem_text(self.folders_list_buttons))
        self.get_elem(self.folders_list_buttons).click()
        self.wait_for_elem_to_show(self.folders_list_buttons)
        self.assertEqual(tv.FOLDER3_NAME, self.get_elem_text(self.folders_list_buttons))
        self.get_elem(self.folders_list_buttons).click()

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_visit_url_with_search_query(self):
        # User have already added 2 documents
        setup_document(self.org, self.user)
        second_document_title = 'bingo!'
        setup_document(self.org, self.user, title=second_document_title)

        # User search last uploaded document
        self.visit(f'/app/#/home/search/{second_document_title}')
        self.wait_documents_list_loaded()

        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 1,
                         'Only second document should appears in the search result')
        self.assertEqual(second_document_title, self.get_elem_text(self.first_document_title),
                         'Second document title should appears in search result')

        self.assertEqual(second_document_title, self.get_elem_text(self.search_input),
                         'Search input should be prefilled with search query')

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_visit_url_with_folder_id(self):
        # User already created a 3 levels folder three (a > b > c) and have added a document inside c folder
        folder_a = setup_folder(self.org)
        folder_b = setup_folder(self.org, parent=folder_a)
        folder_c = setup_folder(self.org, parent=folder_b)
        document = setup_document(self.org, self.user, folder_c, title='bingo!')

        # User open folder c through url
        self.visit(f'/app/#/home/folderFakePath/{folder_c.id}')
        self.wait_documents_list_loaded()

        self.assertEqual(document.title, self.get_elem_text(self.first_document_title),
                         'Setup document title should appears in folder C')

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_folder_navigation_using_browser_previous_and_next(self):
        # User already created a 3 levels folder three (a > b > c) and have added a document inside each of them
        # plus one at root level
        document_root = setup_document(self.org, self.user, title='document_root')
        folder_a = setup_folder(self.org)
        document_a = setup_document(self.org, self.user, folder_a, title='document_a')
        folder_b = setup_folder(self.org, parent=folder_a)
        document_b = setup_document(self.org, self.user, folder_b, title='document_b')
        folder_c = setup_folder(self.org, parent=folder_b)
        document_c = setup_document(self.org, self.user, folder_c, title='document_c')
        self.visit(HomePage.url)

        # User browse to folder c
        self.wait_documents_list_loaded()
        self.get_elem(self.folders_list_buttons).click()
        self.wait_folder_list_loaded()
        self.get_elem(self.folders_list_buttons).click()
        self.wait_folder_list_loaded()
        self.get_elem(self.folders_list_buttons).click()
        self.wait_folder_list_loaded()

        # User use the browser previous button to come back to root
        self.previous_page()
        self.wait_documents_list_loaded()
        self.assertEqual(document_b.title, self.get_elem_text(self.first_document_title),
                         'Setup document title should appears in folder b')
        self.previous_page()
        self.wait_documents_list_loaded()
        self.assertEqual(document_a.title, self.get_elem_text(self.first_document_title),
                         'Setup document title should appears in folder a')
        self.previous_page()
        self.wait_documents_list_loaded()
        self.assertEqual(document_root.title, self.get_elem_text(self.first_document_title),
                         'Setup document title should appears in root folder')
        self.next_page()
        self.wait_documents_list_loaded()
        self.next_page()
        self.wait_documents_list_loaded()
        self.next_page()
        self.wait_documents_list_loaded()
        self.assertEqual(document_c.title, self.get_elem_text(self.first_document_title),
                         'Setup document title should appears in folder c')

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_documents_list_pagination(self):
        # User has already added 21 documents
        for i in range(21):
            setup_document(self.org, self.user, title=i + 1)
        self.refresh_documents_list()

        # Only 10 documents are shown by default
        self.wait_documents_list_loaded()

        self.assertEqual(self.get_elem_text(self.first_document_title), '21')
        self.assertEqual(self.get_elem_text(self.last_document_title), '12')
        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 10)

        # User display 10 more document
        self.get_elem(self.more_documents_button).click()
        self.wait_more_documents_loaded()

        self.assertEqual(self.get_elem_text(self.first_document_title), '21')
        self.assertEqual(self.get_elem_text(self.last_document_title), '2')
        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 20)

        # User display the last document
        self.get_elem(self.more_documents_button).click()
        self.wait_more_documents_loaded()

        self.assertEqual(self.get_elem_text(self.first_document_title), '21')
        self.assertEqual(self.get_elem_text(self.last_document_title), '1')
        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 21)

        # There are no more documents to show
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.more_documents_button)

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_sort_documents_list(self):
        # append 1 at the end to not have the same order for date and alphabetical
        document_title_to_create = list(ascii_lowercase) + ['1']
        # User has already added 21 documents
        for i, title in enumerate(document_title_to_create, 1):
            if i <= 5:  # for the first 5 docs we add a note to test search and relevance sort later
                note = 'bingo ' * i  # doc 5 will get max relevance on "bingo" search
            else:
                note = ''
            setup_document(self.org, self.user, title=title, note=note)
        self.refresh_documents_list()

        # Documents are sort by recent first by default
        recent_first_order = list(reversed(document_title_to_create))
        self.assertIn('recent', self.get_elem_text(self.sort_dropdown_button))
        self.assertEqual(self.get_elems_text(self.documents_titles), recent_first_order[:10])

        # User change sort to older
        self.sort_documents_list('older')

        self.assertIn('older', self.get_elem_text(self.sort_dropdown_button))
        self.assertEqual(self.get_elems_text(self.documents_titles), list(reversed(recent_first_order))[:10])

        # User change sort to a-z
        self.sort_documents_list('az')

        az_order = (['1'] + list(ascii_lowercase))
        self.assertIn('a-z', self.get_elem_text(self.sort_dropdown_button))
        self.assertEqual(self.get_elems_text(self.documents_titles), az_order[:10])

        # User change sort to z-a
        self.sort_documents_list('za')

        self.assertIn('z-a', self.get_elem_text(self.sort_dropdown_button))
        self.assertEqual(self.get_elems_text(self.documents_titles), list(reversed(az_order))[:10])

        # User make a search
        self.search_documents('bingo')

        # Default sort for search is always relevance
        relevance_order = list(reversed(document_title_to_create[:5]))
        self.assertIn('relevance', self.get_elem_text(self.sort_dropdown_button))
        self.assertEqual(self.get_elems_text(self.documents_titles), relevance_order)

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_sort_doc_cache_policy(self):
        # User has already added 21 docs to root and 21 docs to a sub_folder
        document_title_to_create = list(ascii_lowercase) \
                                   + ['1']  # append 1 at the end to not have the same order for date and alphabetical
        # add docs to root
        for title in document_title_to_create:
            setup_document(self.org, self.user, title=title)
        sub_folder = setup_folder(org=self.org)
        document_title_to_create = list(ascii_lowercase) + ['1']
        # add docs to sub_folder
        for i, title in enumerate(document_title_to_create, 1):
            setup_document(self.org, self.user, sub_folder, title)
        self.refresh_documents_list()

        # Default sort in root is recent
        self.assertIn('recent', self.get_elem_text(self.sort_dropdown_button))

        # User open subfolder
        self.get_elem(self.folders_list_buttons).click()

        # Default sort is also recent
        self.assertIn('recent', self.get_elem_text(self.sort_dropdown_button))

        # User update sort to a-z
        self.sort_documents_list('az')

        # Sort properly updated
        self.assertIn('a-z', self.get_elem_text(self.sort_dropdown_button))

        # User come back to root
        self.get_elem(self.home_page_link).click()

        # Default sort is now a-z
        self.assertIn('a-z', self.get_elem_text(self.sort_dropdown_button))

        # User make a search
        self.search_documents('note')

        # Default sort for search is always relevance
        self.assertIn('relevance', self.get_elem_text(self.sort_dropdown_button))

        # User update sort to z-a
        self.sort_documents_list('za')

        # Sort properly updated
        self.assertIn('z-a', self.get_elem_text(self.sort_dropdown_button))

        # User display the page to manage folder
        self.get_elem(self.manage_folder_page_link).click()

        # User come back to home
        self.get_elem(self.home_page_link).click()

        # Default sort is still a-z
        self.assertIn('a-z', self.get_elem_text(self.sort_dropdown_button),
                      'user custom sort should have been saved')

        # User make an F5
        self.visit(HomePage.url)

        # Default sort is back to recent first
        self.assertIn('recent', self.get_elem_text(self.sort_dropdown_button))

    @skipIf(DEFAULT_TEST_BROWSER == 'firefox',
            'Due to a Firefox bug, download can\'t be automated for file with Content-Disposition header set to '
            'attachment.'
            '\nRef: https://bugzilla.mozilla.org/show_bug.cgi?id=453455'
            '\nPossible workaround: https://bugzilla.mozilla.org/show_bug.cgi?id=453455#c150')
    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_download_document_from_list(self):
        # User has already added a document
        document_name = 'doc_name1'
        setup_document(self.org, self.user, title=document_name)
        self.refresh_documents_list()

        # User click on the download button
        file_name = self.download_file(self.documents_download_buttons)

        # Downloaded file name match document name
        self.assertEqual(file_name, document_name + '.pdf')

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_unselect_documents(self):
        # Ensure that documents selected are unselected when switching pages
        folder_a = setup_folder(self.org, "Folder A")
        folder_b = setup_folder(self.org, "Folder B")
        doc_in_folder_a = setup_document(self.org, self.user, title="doc ABBBAX", ftl_folder=folder_a)
        doc_in_folder_b = setup_document(self.org, self.user, title="doc ABXXAB", ftl_folder=folder_b)

        self.refresh_page()

        self.search_documents("ABXXAB")
        self.get_elem(self.documents_checkboxes).click()
        self.get_elem(self.home_page_link).click()

        with self.assertRaises(NoSuchElementException, msg='No batch toolbar should be shown'):
            self.get_elem(self.batch_toolbar)

        # Ensure it's reset between searches too
        self.search_documents("ABXXAB")
        self.get_elem(self.documents_checkboxes).click()
        self.wait_for_elem_to_show(self.batch_toolbar)
        self.assertTrue(self.get_elem(self.batch_toolbar))

        self.search_documents("ABBBAX")
        with self.assertRaises(NoSuchElementException, msg='No batch toolbar should be shown'):
            self.get_elem(self.batch_toolbar)


class SearchTests(LoginPage, HomePage, DocumentViewerModal):
    def setUp(self, **kwargs):
        # first org, admin, user are already created, user is already logged on home page
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        self.visit(LoginPage.url)
        self.log_user()

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_search_document_by_its_title(self):
        # User have already added 2 documents
        setup_document(self.org, self.user)
        second_document_title = 'bingo!'
        setup_document(self.org, self.user, title=second_document_title)

        # User search last uploaded document
        self.search_documents(second_document_title)

        # Only the second document appears in search results
        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 1)
        self.assertEqual(second_document_title, self.get_elem_text(self.first_document_title))

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_search_document_by_its_note(self):
        # User have already added 2 documents
        setup_document(self.org, self.user)
        second_document_note = 'bingo!'
        second_document_title = 'second document'
        setup_document(self.org, self.user, title=second_document_title, note=second_document_note)

        # User search last uploaded document
        self.search_documents(second_document_note)

        # Only the second document appears in search results
        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 1)
        self.assertEqual(second_document_title, self.get_elem_text(self.first_document_title))

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_search_apply_to_all_folders(self):
        # User have added 3 documents in 3 different folders
        folder_a = setup_folder(self.org)
        folder_a_1 = setup_folder(self.org, name=tv.FOLDER2_NAME, parent=folder_a)
        folder_b = setup_folder(self.org, name=tv.FOLDER3_NAME)

        setup_document(self.org, self.user, title='bingo!')
        setup_document(self.org, self.user, folder_a, title='bingo!')
        setup_document(self.org, self.user, folder_a_1, title='bingo!')
        setup_document(self.org, self.user, folder_b, title='bingo!')

        self.visit(HomePage.url)  # Refresh page for folder list to be displayed
        self.wait_folder_list_loaded()

        # User go in folder_a_1 and search for 'bingo!'
        self.get_elem(self.folders_list_buttons).click()  # open folder A
        self.wait_folder_list_loaded()
        self.get_elem(self.folders_list_buttons).click()  # open folder B
        self.wait_folder_list_loaded()
        self.search_documents('bingo!')
        self.wait_documents_list_loaded()

        # Search apply to all folders, thus the 4 documents are return
        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 4,
                         'Search should apply to all folders')

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_search_document_by_its_content(self):
        # User have already added 2 documents
        setup_document(self.org, self.user)
        second_document_title = 'bingo!'
        second_document_text_content = 'Yellow Blue'
        setup_document(self.org, self.user, title=second_document_title, text_content=second_document_text_content)

        # User search last uploaded document
        self.search_documents(second_document_text_content)

        # Only the second document appears in search results
        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 1)
        self.assertEqual(second_document_title, self.get_elem_text(self.first_document_title))

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_search_not_found(self):
        # User have already added 1 document
        setup_document(self.org, self.user)

        # User search something that isn't present in his document
        self.search_documents('this text doesn\'t exist')

        with self.assertRaises(NoSuchElementException, msg='No document should be found by this search query'):
            self.get_elems(self.documents_thumbnails)

        self.assertIn('No document', self.get_elem_text(self.documents_list_container),
                      'A message should indicate no documents were found')

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_search_not_found_from_a_folder(self):
        # User have already added 1 document and 1 folder
        setup_document(self.org, self.user)
        setup_folder(self.org)
        self.visit(HomePage.url)  # Refresh page for folder list to be displayed
        self.wait_folder_list_loaded()

        # User open the folder and then search something that isn't present in its document
        self.get_elem(self.folders_list_buttons).click()
        self.wait_folder_list_loaded()
        self.search_documents('this text doesn\'t exist')

        with self.assertRaises(NoSuchElementException, msg='No document should be found by this search query'):
            self.get_elems(self.documents_thumbnails)

        self.assertIn('No document', self.get_elem_text(self.documents_list_container),
                      'A message should indicate no documents were found')

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_search_open_close_document(self):
        # User have already added 2 documents inside sub folder
        sub_folder = setup_folder(self.org)
        doc_first_result = setup_document(self.org, self.user, ftl_folder=sub_folder, title='pop pop')
        doc_second_result = setup_document(self.org, self.user, ftl_folder=sub_folder, title='pop')
        self.refresh_documents_list()

        # User search for document
        self.search_documents('pop')

        # User open first document of search result and close it
        self.open_first_document()
        self.close_document()

        # The search result is still displayed after closing the first document
        self.assertEqual(self.get_elems_text(self.documents_titles), [doc_first_result.title, doc_second_result.title])

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_search_advanced_syntax(self):
        # See https://www.postgresql.org/docs/11/textsearch-controls.html#id-1.5.11.6.4.11 for advanced search syntax
        # User have already added 2 documents inside sub folder
        red_doc = setup_document(self.org, self.user, title='red')
        purple_doc = setup_document(self.org, self.user, title='purple 1', note='red blue')
        purple_doc_2 = setup_document(self.org, self.user, title='purple 2', note='blue red')
        orange_doc = setup_document(self.org, self.user, title='orange', note='red yellow')
        self.refresh_documents_list()

        # User search for documents containing red and yellow key word
        self.search_documents('red yellow')

        # 1 document is found: orange
        self.assertEqual(len(self.get_elems(self.documents_thumbnails)), 1)
        self.assertIn(orange_doc.title, self.get_elems_text(self.documents_titles))

        # User search for documents containing blue or yellow key word
        self.search_documents('blue OR yellow')

        # 3 documents are found: purple, purple 2 and orange
        self.assertEqual(len(self.get_elems(self.documents_titles)), 3)
        self.assertIn(purple_doc.title, self.get_elems_text(self.documents_titles))
        self.assertIn(purple_doc_2.title, self.get_elems_text(self.documents_titles))
        self.assertIn(orange_doc.title, self.get_elems_text(self.documents_titles))

        # User search for documents containing red but not yellow and blue
        self.search_documents('red -yellow -blue')

        # 1 documents is found: red
        self.assertEqual(len(self.get_elems(self.documents_titles)), 1)
        self.assertIn(red_doc.title, self.get_elems_text(self.documents_titles))

        # User search for documents containing the phrase "blue red"
        self.search_documents('"blue red"')

        # 1 documents is found: purple2
        self.assertEqual(len(self.get_elems(self.documents_titles)), 1)
        self.assertIn(purple_doc_2.title, self.get_elems_text(self.documents_titles))


class DocumentsBatchActionsTests(LoginPage, HomePage, MoveDocumentsModal):
    def setUp(self, **kwargs):
        # first org, admin, user are already created, user is already logged on home page
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        self.visit(LoginPage.url)
        self.log_user()
        # 3 documents, 1 folder already added/created
        self.doc1 = setup_document(self.org, self.user, binary=setup_temporary_file().name, title='doc1')
        self.doc2 = setup_document(self.org, self.user, binary=setup_temporary_file().name, title='doc2')
        self.doc3 = setup_document(self.org, self.user, binary=setup_temporary_file().name, title='doc3')
        self.folder = setup_folder(self.org)
        # refresh page to see documents
        self.visit(HomePage.url)

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_select_documents(self):
        # User select doc1 and doc2
        docs_to_select = ['doc1', 'doc2']
        self.select_documents(docs_to_select)

        # User see in the batch actions toolbar that 2 documents are selected
        self.assertIn('2 documents', self.get_elem_text(self.batch_toolbar))

        # User unselect documents and the toolbar disappear
        self.get_elem(self.unselect_all_docs_batch_button).click()
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.batch_toolbar)

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_move_documents(self):
        # User select doc1 and doc2
        docs_to_move = ['doc1', 'doc2']
        self.select_documents(docs_to_move)

        # User click on move button and select the target folder
        self.get_elem(self.move_docs_batch_button).click()
        self.move_documents(self.folder.name)

        # User see the documents to move have disappear from the current folder
        self.assertCountEqual([self.doc3.title], self.get_elems_text(self.documents_titles))

        # User see the documents in the proper folder
        self.get_elem(self.folders_list_buttons).click()
        self.wait_documents_list_loaded()
        self.assertCountEqual(docs_to_move, self.get_elems_text(self.documents_titles))

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_delete_documents(self):
        # User select doc1 and doc2
        docs_to_delete = ['doc1', 'doc2']
        self.select_documents(docs_to_delete)

        # User click on delete button
        self.get_elem(self.delete_docs_batch_button).click()
        self.accept_modal()

        # User see the documents to delete have disappear from the current folder
        self.assertCountEqual([self.doc3.title], self.get_elems_text(self.documents_titles))

        # User refresh the page and observe that documents are really gone
        self.visit(HomePage.url)
        self.assertCountEqual([self.doc3.title], self.get_elems_text(self.documents_titles))


class DocumentViewerModalTests(LoginPage, HomePage, DocumentViewerModal):
    def setUp(self, **kwargs):
        # first org, admin, user are already created, user is already logged on home page
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        self.visit(LoginPage.url)
        self.log_user()

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_visit_url_with_document_pid(self):
        # User have already added 2 documents
        setup_document(self.org, self.user)
        second_document_title = 'bingo!'
        second_document = setup_document(self.org, self.user, title=second_document_title)

        # User open second document through url
        self.visit(DocumentViewerModal.url.format(second_document.pid))
        self.wait_for_elem_to_show(self.document_title)

        self.assertIn(second_document_title,
                      self.get_elem_text(self.document_title),
                      'Setup document title should match opened document')

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_visit_url_with_folder_id_and_document_pid(self):
        # User already created a 3 levels folder three (a > b > c) and have added a document inside c folder
        folder_a = setup_folder(self.org)
        folder_b = setup_folder(self.org, parent=folder_a)
        folder_c = setup_folder(self.org, parent=folder_b)
        document_title = 'bingo!'
        document = setup_document(self.org, self.user, folder_c, title=document_title)

        # User open folder and document through url
        self.visit(f'{HomePage.url}#/home/folderFakePath/{folder_c.id}?doc={document.pid}')
        self.wait_for_elem_to_show(self.document_title)

        self.assertIn(document_title,
                      self.get_elem_text(self.document_title),
                      'Setup document title should match opened document')

        # User close document
        self.close_document()
        self.assertEqual(document.title, self.get_elem_text(self.first_document_title),
                         'Setup document title should appears in folder C')

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    @patch.object(FTLDocumentProcessing, 'apply_processing')
    def test_rename_document(self, mock_apply_processing):
        # User has already added and opened a document
        setup_document(self.org, self.user)
        self.refresh_documents_list()
        self.open_first_document()

        # User rename the document
        new_doc_title = 'Renamed doc'
        self.rename_document(new_doc_title)

        # Document title is properly updated in pdf viewer and list
        self.assertEqual(self.get_elem_text(self.document_title), new_doc_title)
        self.close_document()
        self.assertEqual(self.get_elem_text(self.first_document_title), new_doc_title)

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    @patch.object(FTLDocumentProcessing, 'apply_processing')
    def test_annotate_document(self, mock_apply_processing):
        # User has already added and opened a document
        setup_document(self.org, self.user)
        self.refresh_documents_list()
        self.open_first_document()

        # User annotate the document
        new_doc_note = 'New note'
        self.annotate_document(new_doc_note)

        # Document note is properly updated in pdf viewer
        self.assertEqual(self.get_elem_text(self.note_text), new_doc_note)

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    @patch.object(FTLDocumentProcessing, 'apply_processing')
    def test_delete_document(self, mock_apply_processing):
        # User has already added and opened a document
        setup_document(self.org, self.user, binary=setup_temporary_file().name)
        self.refresh_documents_list()
        self.open_first_document()

        # User delete the document
        self.delete_document()

        # User see there is no more document in the list
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.first_document_title)

        # User refresh the page and observe document is really gone
        self.visit(HomePage.url)
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.first_document_title)

    @skipIf(DEFAULT_TEST_BROWSER == 'chrome' and TEST_BROWSER_HEADLESS,
            "Headless chrome doesn't support extensions and it seem it doesn't support PDF preview too (browser freeze"
            " after switching to tab with PDF preview).\n"
            "Refs:\n"
            " - https://bugs.chromium.org/p/chromedriver/issues/detail?id=1961\n"
            " - https://bugs.chromium.org/p/chromium/issues/detail?id=706008")
    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_open_document(self):
        # User has already added and opened a document
        document_name = 'doc_name1'
        document = setup_document(self.org, self.user, title=document_name)
        self.refresh_documents_list()
        self.open_first_document()

        # User click on open pdf button
        initial_tabs = self.browser.window_handles
        self.get_elem(self.open_pdf_button).click()
        time.sleep(0.5)  # wait for browser to open new tab
        current_tabs = self.browser.window_handles

        # A new tab has opened
        self.assertGreater(len(current_tabs), len(initial_tabs), 'no new tab opened')

        # document is opened in new tab
        new_window = (set(current_tabs) - set(initial_tabs)).pop()
        self.browser.switch_to.window(new_window)
        time.sleep(0.5)  # wait for browser to load viewer
        self.assertIn(f'{document.pid}/doc.pdf', self.browser.current_url)


class ManageFoldersPageTests(LoginPage, ManageFolderPage):
    def setUp(self, **kwargs):
        # first org, admin, user are already created, user is already logged on manage folder page
        super().setUp()
        self.org = setup_org()
        setup_admin(self.org)
        self.user = setup_user(self.org)
        self.visit(ManageFolderPage.url)
        self.log_user()

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_create_folder(self):
        # User create 3 folders at root
        folders_to_create = ['folder 1', 'folder 2', 'folder 3']
        for folder in folders_to_create:
            self.create_folder(folder)

        # Folder appears in the list with the proper order
        self.assertEqual(folders_to_create, self.get_elems_text(self.folders_title))

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_create_folder_tree(self):
        # User create a folder tree of 3 levels :
        # folder 1
        #   folder 2
        #       folder 3
        folders_to_create = ['folder 1', 'folder 2', 'folder 3']
        for folder in folders_to_create:
            self.create_folder(folder)
            self.navigate_to_folder(folder)

        # Folders appears as a tree
        self.visit(ManageFolderPage.url)
        self.assertEqual([folders_to_create[0]], self.get_elems_text(self.folders_title),
                         'First level should only show first folder')

        self.navigate_to_folder(folders_to_create[0])
        self.assertEqual([folders_to_create[1]], self.get_elems_text(self.folders_title),
                         'Second level should only show second folder')

        self.navigate_to_folder(folders_to_create[1])
        self.assertEqual([folders_to_create[2]], self.get_elems_text(self.folders_title),
                         'Third level should only show third folder')

        self.navigate_to_folder(folders_to_create[2])
        self.assertEqual('Root\n' + '\n'.join(folders_to_create), self.get_elem_text(self.breadcrumb),
                         'Breadcrumb should show all folders created on the deepest level')

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_select_folder(self):
        # User have already created 2 folders
        folder_to_select_name = 'folder 1'
        self.create_folder(folder_to_select_name)
        self.create_folder('folder 2')

        # No folder select message appears in the right panel
        self.assertEqual('No folder selected', self.get_elem_text(self.right_panel))

        # User select the folder to select
        self.select_folder(folder_to_select_name)

        # The selected folder name appears in the right panel
        self.assertEqual(folder_to_select_name, self.get_elem_text(self.selected_folder_name))

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_rename_selected_folder(self):
        # User have already created 2 folders
        folder_to_rename_name = 'rename me plz'
        self.create_folder(folder_to_rename_name)
        folder_not_to_rename_name = 'do not rename me :C!'
        self.create_folder(folder_not_to_rename_name)

        # User select the folder to rename and rename it
        self.select_folder(folder_to_rename_name)
        folder_renamed_name = 'fresh new name'
        self.rename_selected_folder(folder_renamed_name)

        # The desired folder have been renamed the other folder keep its name
        folder_title_list = self.get_elems_text(self.folders_title)
        self.assertNotIn(folder_to_rename_name, folder_title_list,
                         'Old folder name should not be present anymore')
        self.assertIn(folder_not_to_rename_name, folder_title_list,
                      'The not renamed folder should have kept its name')
        self.assertIn(folder_renamed_name, folder_title_list,
                      'New folder name should be present')
        # Side panel remain opened
        self.assertEqual(folder_renamed_name, self.get_elem_text(self.selected_folder_name),
                         'The selected folder name should be still visible and updated')

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_move_selected_folder(self):
        # User have already created 2 folders
        folder_to_move_name = 'move me plz'
        self.create_folder(folder_to_move_name)
        folder_not_to_move_name = 'do not move me :C!'
        self.create_folder(folder_not_to_move_name)

        # User select the folder to move and move it
        self.select_folder(folder_to_move_name)
        self.move_selected_folder(target_folder_name=folder_not_to_move_name)

        # The desired folder have been moved
        folder_title_list = self.get_elems_text(self.folders_title)
        self.assertNotIn(folder_to_move_name, folder_title_list,
                         'Moved folder should not appears at root anymore')
        self.assertIn(folder_not_to_move_name, folder_title_list,
                      'Unmoved folder appears at root')
        # Side panel has been closed
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.selected_folder_name)

        self.navigate_to_folder(folder_not_to_move_name)
        folder_title_list = self.get_elems_text(self.folders_title)
        self.assertIn(folder_to_move_name, folder_title_list,
                      'Moved folder should appears in target folder')

    @skipIf(DEV_MODE and not NODE_SERVER_RUNNING, "Node not running, this test can't be run")
    def test_delete_selected_folder(self):
        # User have already created 2 folders
        folder_to_delete_name = 'delete me plz'
        self.create_folder(folder_to_delete_name)
        folder_not_to_delete_name = 'do not delete me :C!'
        self.create_folder(folder_not_to_delete_name)

        # User select the folder to move and move it
        self.select_folder(folder_to_delete_name)
        self.delete_selected_folder()

        # The desired folder have been deleted
        folder_title_list = self.get_elems_text(self.folders_title)
        self.assertNotIn(folder_to_delete_name, folder_title_list,
                         'Delete folder should not appears anymore')
        self.assertIn(folder_not_to_delete_name, folder_title_list,
                      'Undeleted folder should appears')

        # Side panel has been closed
        with self.assertRaises(NoSuchElementException):
            self.get_elem(self.selected_folder_name)
