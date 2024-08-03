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
                                                            mock_insert_new_note_into_database,
                                                            mock_commit_transaction
                                                            ):
            mock_get_notes_dir.return_value = "sqnotes"
            mock_get_all_note_paths.return_value = ['file1', 'file2', 'file3']
            mock_get_note_id_or_none.side_effect = [3, 2, 1]
            mock_insert_new_note_into_database.side_effect = []
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
                                                            mock_insert_new_note_into_database,
                                                            mock_delete_keywords_from_database_for_note,
                                                            mock_get_decrypted_content_in_memory,
                                                            mock_get_note_id_or_none,
                                                            sqnotes_obj
                                                            ):
            mock_get_notes_dir.return_value = "sqnotes"
            mock_insert_new_note_into_database.return_value = 3
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
                                                    mock_insert_new_note_into_database,
                                                    mock_delete_keywords_from_database_for_note,
                                                    mock_get_decrypted_content_in_memory,
                                                    mock_get_note_id_or_none,
                                                    sqnotes_obj
                                                ):
            mock_get_notes_dir.return_value = "sqnotes"
            mock_insert_new_note_into_database.side_effect = [6, 7]
            mock_get_all_note_paths.return_value = ['file1', 'file2', 'file3', 'file4', 'file5']
            mock_get_note_id_or_none.side_effect = [1, None, None, 4, 2]
            sqnotes_obj.rescan_for_database()
            call_args_list = mock_insert_new_note_into_database.call_args_list
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
                                                            mock_insert_new_note_into_database
                                                            ):
            mock_get_notes_dir.return_value = "sqnotes"
            mock_get_all_note_paths.return_value = ['file1', 'file2', 'file3']
            mock_get_note_id_or_none.side_effect = [3, None, 1]
            mock_insert_new_note_into_database.side_effect = [5]
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
                                                            mock_insert_new_note_into_database,
                                                            mock_commit_transaction
                                                            ):
            mock_get_notes_dir.return_value = "sqnotes"
            mock_get_all_note_paths.return_value = ['file1', 'file2', 'file3']
            mock_get_note_id_or_none.side_effect = [3, None, 1]
            mock_insert_new_note_into_database.side_effect = [5]
            sqnotes_obj.rescan_for_database()
            num_commit_transaction_calls = len(mock_commit_transaction.call_args_list)
            assert num_commit_transaction_calls == 3
        
        
        
        