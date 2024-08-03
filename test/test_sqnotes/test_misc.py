import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import os
import pytest
from sqnotes.sqnotes_module import SQNotes, NotesDirNotConfiguredException
from sqnotes.user_configuration_helper import UserConfigurationHelper
from sqnotes.database_service import DatabaseService
from test.test_helper import do_nothing


def describe_sqnotes():
    
    
    def describe_database_setup():
    
        @patch.object(UserConfigurationHelper, 'set_setting_to_user_config', do_nothing)
        @patch.object(DatabaseService, 'setup_database')
        def it_calls_setup_on_database_service(
                                                mock_set_up_database,
                                                sqnotes_obj : SQNotes
                                                ):
            """calls setup on the database service"""
            
            sqnotes_obj.setup_database()
            mock_set_up_database.assert_called_once()
    
    
    def describe_get_notes_dir_from_config():
        
        def it_calls_config_module_to_get_notes_dir(
                                                        sqnotes_obj : SQNotes
                                                    ):
            with patch.object(sqnotes_obj.user_configuration_helper, 'get_setting_from_user_config') as mock_get_config_setting:
                sqnotes_obj.get_notes_dir_from_config()
                mock_get_config_setting.assert_called_once_with(key = 'notes_path')
            
        @patch.object(UserConfigurationHelper, 'get_setting_from_user_config')
        def it_returns_the_value_from_the_config_module(
                                                        mock_get_config_setting,
                                                        sqnotes_obj : SQNotes
                                                    ):
            test_notes_path = 'test/notes/path'
            mock_get_config_setting.return_value = test_notes_path
            return_value = sqnotes_obj.get_notes_dir_from_config()
            assert return_value == test_notes_path
        
        
        @patch.object(UserConfigurationHelper, 'get_setting_from_user_config')
        def it_raises_if_notes_path_not_configured(
                                                        mock_get_config_setting,
                                                        sqnotes_obj : SQNotes
                                                    ):
            mock_get_config_setting.return_value = None
            with pytest.raises(NotesDirNotConfiguredException):
                sqnotes_obj.get_notes_dir_from_config()
        


    def describe_list_files():
        
        @pytest.mark.usefixtures('mock_get_notes_dir_from_config')
        @patch.object(SQNotes, '_get_all_note_paths')
        def it_prints_all_files(
                                    mock_get_notes,
                                    sqnotes_obj,
                                    mock_print
                                ):
            mock_get_notes.return_value = ['test1.txt.gpg', 'test2.txt.gpg']
            
            sqnotes_obj.notes_list()
            calls = [
                call('test1.txt.gpg'),
                call('test2.txt.gpg'),
            ]
            mock_print.assert_has_calls(calls, any_order=False)
            

    def describe_get_notes():
            
        def it_returns_list_of_notes_in_notes_dir(
                    sqnotes_obj,
                    mock_note_files,
                    test_notes_directory
                ):
            
            expected_value = mock_note_files
            all_notes = sqnotes_obj._get_all_note_paths(notes_dir=test_notes_directory)
            assert all_notes == expected_value
            
    def describe_get_user_config_dir():
        
        @patch('os.path.expanduser')
        def it_applies_expanduser_to_get_the_configured_path(
                                                 mock_path_expanduser,
                                                 sqnotes_obj : SQNotes,
                                                 mock_config_data
                                                ):
            expanded_path = 'expanded path'
            mock_path_expanduser.return_value = expanded_path
            mock_config_data[sqnotes_obj.USER_CONFIG_DIR_KEY] = 'configured path'
            response = sqnotes_obj._get_user_config_dir()
            assert response == expanded_path

if __name__ == '__main__':
    unittest.main()
