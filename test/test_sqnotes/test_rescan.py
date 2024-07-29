import unittest
from unittest.mock import patch, mock_open, MagicMock, call, Mock
import os
import pytest
from sqnotes.sqnotes_module import SQNotes
from sqnotes.encrypted_note_helper import EncryptedNoteHelper
from test.test_sqnotes_initializer import get_test_sqnotes


@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    
        
class TestSQNotesRescanNotes(unittest.TestCase):
    get_decrypted_content_in_memory_patcher = None

    @classmethod
    def setUpClass(cls):
        pass
        
    @classmethod
    def tearDownClass(cls):
        pass


    def setUp(self):
        self.sqnotes = get_test_sqnotes()
        get_decrypted_content = Mock()
        get_decrypted_content.side_effect = ['content1', 'content2']
        self.get_decrypted_content_in_memory_patcher = patch.object(EncryptedNoteHelper, 'get_decrypted_content_in_memory', get_decrypted_content)
        self.get_decrypted_content_in_memory_patcher.start()
        
        
        
        
    def tearDown(self):
        self.get_decrypted_content_in_memory_patcher.stop()

    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, '_commit_transaction')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_delete_keywords_from_database_for_note')
    @patch.object(SQNotes, '_get_note_id_from_database_or_none')
    @patch.object(SQNotes, '_get_all_note_paths')
    def test_rescan_calls_to_remove_existing_note_keywords_if_all_notes_found_in_database(self,
                                    mock_get_all_note_paths,
                                    mock_get_note_id,
                                    mock_delete_keywords_from_database_for_note,
                                    mock_extract_and_save_keywords,
                                    mock_commit,
                                    mock_get_notes_dir,
                                    mock_open_database):
        mock_get_notes_dir.return_value = "sqnotes"
        mock_get_all_note_paths.return_value = ['file1', 'file2']
        mock_get_note_id.side_effect = [1, 2]
        self.sqnotes.rescan_for_database()
        
        call_args_list = mock_delete_keywords_from_database_for_note.call_args_list
        
        self.assertEqual(call_args_list[0].kwargs, {'note_id': 1})
        self.assertEqual(call_args_list[1].kwargs, {'note_id': 2})
        
    @patch.object(SQNotes, '_insert_new_note_into_database')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, '_commit_transaction')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_delete_keywords_from_database_for_note')
    @patch.object(SQNotes, '_get_note_id_from_database_or_none')
    @patch.object(SQNotes, '_get_all_note_paths')
    def test_rescan_calls_to_remove_existing_note_keywords_if_some_notes_not_found_in_database(self,
                                    mock_get_all_note_paths,
                                    mock_get_note_id,
                                    mock_delete_keywords_from_database_for_note,
                                    mock_extract_and_save_keywords,
                                    mock_commit,
                                    mock_get_notes_dir,
                                    mock_open_database,
                                    mock_insert_note):
        mock_get_notes_dir.return_value = "sqnotes"
        mock_insert_note.return_value = 3
        mock_get_all_note_paths.return_value = ['file1', 'file2']
        mock_get_note_id.side_effect = [None, 2]
        self.sqnotes.rescan_for_database()
        
        call_args_list = mock_delete_keywords_from_database_for_note.call_args_list
        
        self.assertEqual(call_args_list[0].kwargs, {'note_id': 3})
        self.assertEqual(call_args_list[1].kwargs, {'note_id': 2})
        
        
        
    @patch.object(SQNotes, '_insert_new_note_into_database')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, '_commit_transaction')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_delete_keywords_from_database_for_note')
    @patch.object(SQNotes, '_get_note_id_from_database_or_none')
    @patch.object(SQNotes, '_get_all_note_paths')
    def test_rescan_inserts_note_in_database_if_not_found(self,
                                    mock_get_all_note_paths,
                                    mock_get_note_id,
                                    mock_delete_keywords_from_database_for_note,
                                    mock_extract_and_save_keywords,
                                    mock_commit,
                                    mock_get_notes_dir,
                                    mock_open_database,
                                    mock_insert_note_into_database):
        mock_get_notes_dir.return_value = "sqnotes"
        mock_get_all_note_paths.return_value = ['file1', 'file2']
        mock_get_note_id.side_effect = [1, None]
        self.sqnotes.rescan_for_database()
        mock_insert_note_into_database.assert_called_once_with(note_filename_base='file2')
        
        
    @patch.object(SQNotes, '_insert_new_note_into_database')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, '_commit_transaction')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_delete_keywords_from_database_for_note')
    @patch.object(SQNotes, '_get_note_id_from_database_or_none')
    @patch.object(SQNotes, '_get_all_note_paths')
    def test_rescan_calls_to_extract_and_save_keywords(self,
                                    mock_get_all_note_paths,
                                    mock_get_note_id,
                                    mock_delete_keywords_from_database_for_note,
                                    mock_extract_and_save_keywords,
                                    mock_commit,
                                    mock_get_notes_dir,
                                    mock_open_database,
                                    mock_insert_note):
        mock_get_notes_dir.return_value = "sqnotes"
        mock_insert_note.return_value = 3
        mock_get_all_note_paths.return_value = ['file1', 'file2']
        mock_get_note_id.side_effect = [None, 2]
        self.sqnotes.rescan_for_database()
        
        call_args_list = mock_extract_and_save_keywords.call_args_list
        
        self.assertEqual(call_args_list[0].kwargs, {'note_id': 3, 'note_content' : 'content1'})
        self.assertEqual(call_args_list[1].kwargs, {'note_id': 2, 'note_content' : 'content2'})
        
        
        
    @patch.object(SQNotes, '_insert_new_note_into_database')
    @patch.object(SQNotes, 'open_database')
    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, '_commit_transaction')
    @patch.object(SQNotes, '_extract_and_save_keywords')
    @patch.object(SQNotes, '_delete_keywords_from_database_for_note')
    @patch.object(SQNotes, '_get_note_id_from_database_or_none')
    @patch.object(SQNotes, '_get_all_note_paths')
    def test_rescan_commits_database_changes(self,
                                    mock_get_all_note_paths,
                                    mock_get_note_id,
                                    mock_delete_keywords_from_database_for_note,
                                    mock_extract_and_save_keywords,
                                    mock_commit,
                                    mock_get_notes_dir,
                                    mock_open_database,
                                    mock_insert_note):
        mock_get_notes_dir.return_value = "sqnotes"
        mock_insert_note.return_value = 3
        mock_get_all_note_paths.return_value = ['file1', 'file2']
        mock_get_note_id.side_effect = [None, 2]
        self.sqnotes.rescan_for_database()
        
        mock_commit.assert_called()
        
        
        
        
        
        
        