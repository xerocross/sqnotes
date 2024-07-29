import unittest
from unittest.mock import patch, mock_open, MagicMock, call, Mock
import os
import pytest
from sqnotes.sqnotes_module import SQNotes
from sqnotes.encrypted_note_helper import EncryptedNoteHelper
from test.test_sqnotes_initializer import get_test_sqnotes

from sqnotes.database_service import DatabaseService


@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    
@pytest.fixture
def mock_get_decrypted_content_in_memory():
    with patch.object(EncryptedNoteHelper, 'get_decrypted_content_in_memory') as mock:
        mock.side_effect = [f"content{x}" for x in range(1, 20)]
        yield mock
     
@pytest.fixture   
def mock_insert_new_note():
    # @patch.object(DatabaseService, 'insert_new_note_into_database')
    with patch.object(DatabaseService, 'insert_new_note_into_database') as mock:
        # mock.side_effect = [x for x in range(0, 20)]
        yield mock
   
    
def describe_rescan_notes():
    
    
    
    
    
    
    def describe_all_notes_found_in_database():
    
        @pytest.mark.usefixtures("mock_commit_transaction",
                                 "mock_extract_and_save_keywords",
                                 "mock_open_database")
        @patch.object(SQNotes, 'get_notes_dir_from_config')
        @patch.object(SQNotes, '_get_all_note_paths')
        def it_calls_to_remove_existing_note_keywords(
                                                            mock_get_all_note_paths,
                                                            mock_get_notes_dir,
                                                            mock_delete_keywords_from_database_for_note,
                                                            mock_get_decrypted_content_in_memory,
                                                            mock_get_note_id_or_none,
                                                            sqnotes_obj
                                                            ):
            mock_get_notes_dir.return_value = "sqnotes"
            mock_get_all_note_paths.return_value = ['file1', 'file2']
            mock_get_note_id_or_none.side_effect = [1, 2]
            sqnotes_obj.rescan_for_database()
            
            call_args_list = mock_delete_keywords_from_database_for_note.call_args_list
            
            assert call_args_list[0].kwargs == {'note_id': 1}
            assert call_args_list[1].kwargs == {'note_id': 2}
    
    
        @pytest.mark.usefixtures("mock_commit_transaction",
                                 "mock_open_database",
                                 "mock_delete_keywords_from_database_for_note")
        @patch.object(SQNotes, 'get_notes_dir_from_config')
        @patch.object(SQNotes, '_get_all_note_paths')
        def it_extracts_and_saves_keywords_for_all_notes(
                                                            mock_get_all_note_paths,
                                                            mock_get_notes_dir,
                                                            mock_get_decrypted_content_in_memory,
                                                            mock_get_note_id_or_none,
                                                            sqnotes_obj,
                                                            mock_extract_and_save_keywords
                                                            ):
            mock_get_notes_dir.return_value = "sqnotes"
            mock_get_all_note_paths.return_value = ['file1', 'file2']
            mock_get_note_id_or_none.side_effect = [3, 2]
            sqnotes_obj.rescan_for_database()
            
            call_args_list = mock_extract_and_save_keywords.call_args_list
            assert call_args_list[0].kwargs == {'note_id': 3, 'note_content' : 'content1'}
            assert call_args_list[1].kwargs == {'note_id': 2, 'note_content' : 'content2'}
    
    
        @pytest.mark.usefixtures("mock_open_database",
                                 "mock_delete_keywords_from_database_for_note")
        @patch.object(SQNotes, 'get_notes_dir_from_config')
        @patch.object(SQNotes, '_get_all_note_paths')
        def it_commits_the_transaction_for_each_note (
                                                            mock_get_all_note_paths,
                                                            mock_get_notes_dir,
                                                            mock_get_decrypted_content_in_memory,
                                                            mock_get_note_id_or_none,
                                                            sqnotes_obj,
                                                            mock_extract_and_save_keywords,
                                                            mock_insert_new_note,
                                                            mock_commit_transaction
                                                            ):
            mock_get_notes_dir.return_value = "sqnotes"
            mock_get_all_note_paths.return_value = ['file1', 'file2', 'file3']
            mock_get_note_id_or_none.side_effect = [3, 2, 1]
            mock_insert_new_note.side_effect = []
            sqnotes_obj.rescan_for_database()
            num_commit_transaction_calls = len(mock_commit_transaction.call_args_list)
            assert num_commit_transaction_calls == 3
    
    
    def describe_some_notes_not_found_in_database():
        """some notes from the notes directory not found in database"""
        
        @pytest.mark.usefixtures("mock_commit_transaction",
                                 "mock_extract_and_save_keywords",
                                 "mock_open_database")
        @patch.object(DatabaseService, 'insert_new_note_into_database')
        @patch.object(SQNotes, 'get_notes_dir_from_config')
        @patch.object(SQNotes, '_get_all_note_paths')
        def it_calls_to_remove_existing_note_keywords(
                                                            mock_get_all_note_paths,
                                                            mock_get_notes_dir,
                                                            mock_insert_new_note,
                                                            mock_delete_keywords_from_database_for_note,
                                                            mock_get_decrypted_content_in_memory,
                                                            mock_get_note_id_or_none,
                                                            sqnotes_obj
                                                            ):
            mock_get_notes_dir.return_value = "sqnotes"
            mock_insert_new_note.return_value = 3
            mock_get_all_note_paths.return_value = ['file1', 'file2']
            mock_get_note_id_or_none.side_effect = [None, 2]
            sqnotes_obj.rescan_for_database()
            
            call_args_list = mock_delete_keywords_from_database_for_note.call_args_list
            
            assert call_args_list[0].kwargs == {'note_id': 3}
            assert call_args_list[1].kwargs == {'note_id': 2}
    
    
        @pytest.mark.usefixtures("mock_commit_transaction",
                                 "mock_extract_and_save_keywords",
                                 "mock_open_database")
        @patch.object(DatabaseService, 'insert_new_note_into_database')
        @patch.object(SQNotes, 'get_notes_dir_from_config')
        @patch.object(SQNotes, '_get_all_note_paths')
        def it_inserts_unfound_notes_in_database(
                                                    mock_get_all_note_paths,
                                                    mock_get_notes_dir,
                                                    mock_insert_new_note,
                                                    mock_delete_keywords_from_database_for_note,
                                                    mock_get_decrypted_content_in_memory,
                                                    mock_get_note_id_or_none,
                                                    sqnotes_obj
                                                ):
            mock_get_notes_dir.return_value = "sqnotes"
            mock_insert_new_note.side_effect = [6, 7]
            mock_get_all_note_paths.return_value = ['file1', 'file2', 'file3', 'file4', 'file5']
            mock_get_note_id_or_none.side_effect = [1, None, None, 4, 2]
            sqnotes_obj.rescan_for_database()
            call_args_list = mock_insert_new_note.call_args_list
            first_call = call_args_list[0]
            _, first_call_kwargs = first_call
            assert first_call_kwargs['note_filename_base'] == 'file2'
            _, second_call_kwargs = call_args_list[1]
            assert second_call_kwargs['note_filename_base'] == 'file3'
            

        @pytest.mark.usefixtures("mock_commit_transaction",
                                 "mock_open_database",
                                 "mock_delete_keywords_from_database_for_note")
        @patch.object(SQNotes, 'get_notes_dir_from_config')
        @patch.object(SQNotes, '_get_all_note_paths')
        def it_extracts_and_saves_keywords_for_all_notes(
                                                            mock_get_all_note_paths,
                                                            mock_get_notes_dir,
                                                            mock_get_decrypted_content_in_memory,
                                                            mock_get_note_id_or_none,
                                                            sqnotes_obj,
                                                            mock_extract_and_save_keywords,
                                                            mock_insert_new_note
                                                            ):
            mock_get_notes_dir.return_value = "sqnotes"
            mock_get_all_note_paths.return_value = ['file1', 'file2', 'file3']
            mock_get_note_id_or_none.side_effect = [3, None, 1]
            mock_insert_new_note.side_effect = [5]
            sqnotes_obj.rescan_for_database()
            call_args_list = mock_extract_and_save_keywords.call_args_list
            assert call_args_list[0].kwargs == {'note_id': 3, 'note_content' : 'content1'}
            assert call_args_list[1].kwargs == {'note_id': 5, 'note_content' : 'content2'}
            assert call_args_list[2].kwargs == {'note_id': 1, 'note_content' : 'content3'}
        
        
        @pytest.mark.usefixtures("mock_open_database",
                                 "mock_delete_keywords_from_database_for_note")
        @patch.object(SQNotes, 'get_notes_dir_from_config')
        @patch.object(SQNotes, '_get_all_note_paths')
        def it_commits_the_transaction_for_each_note (
                                                            mock_get_all_note_paths,
                                                            mock_get_notes_dir,
                                                            mock_get_decrypted_content_in_memory,
                                                            mock_get_note_id_or_none,
                                                            sqnotes_obj,
                                                            mock_extract_and_save_keywords,
                                                            mock_insert_new_note,
                                                            mock_commit_transaction
                                                            ):
            mock_get_notes_dir.return_value = "sqnotes"
            mock_get_all_note_paths.return_value = ['file1', 'file2', 'file3']
            mock_get_note_id_or_none.side_effect = [3, None, 1]
            mock_insert_new_note.side_effect = [5]
            sqnotes_obj.rescan_for_database()
            num_commit_transaction_calls = len(mock_commit_transaction.call_args_list)
            assert num_commit_transaction_calls == 3
        
        
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

    
    #
    # @patch.object(SQNotes, '_insert_new_note_into_database')
    # @patch.object(SQNotes, 'open_database')
    # @patch.object(SQNotes, 'get_notes_dir_from_config')
    # @patch.object(SQNotes, '_extract_and_save_keywords')
    # @patch.object(SQNotes, '_delete_keywords_from_database_for_note')
    # @patch.object(SQNotes, '_get_all_note_paths')
    # def test_rescan_commits_database_changes(self,
    #                                 mock_get_all_note_paths,
    #                                 mock_get_note_id,
    #                                 mock_delete_keywords_from_database_for_note,
    #                                 mock_extract_and_save_keywords,
    #                                 mock_get_notes_dir,
    #                                 mock_open_database,
    #                                 mock_insert_note,
    #                                 mock_get_note_id_or_none,
    #                                 mock_commit_transaction):
    #     mock_get_notes_dir.return_value = "sqnotes"
    #     mock_get_note_id_or_none.return_value = 3
    #     mock_get_all_note_paths.return_value = ['file1', 'file2']
    #     mock_get_note_id.side_effect = [None, 2]
    #     self.sqnotes.rescan_for_database()
    #
    #     mock_commit_transaction.assert_called()
    #
    #
    #

        
        
        
        