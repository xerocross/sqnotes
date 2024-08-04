import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import os
import pytest
from sqnotes.sqnotes_module import SQNotes, NotesDirNotConfiguredException
from sqnotes.user_configuration_helper import UserConfigurationHelper
from sqnotes.database_service import DatabaseService
from test.test_helper import do_nothing, just_return
from sqnotes.sqnotes_config_module import SQNotesConfig
import sqnotes
import logging

logger = logging.getLogger("test_misc")


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
            
            
    def describe_get_default_database_path():

        @pytest.mark.usefixtures("mock_get_notes_dir_from_config")
        @patch.object(SQNotesConfig, 'get')
        def it_builds_path_from_configured_notes_dir (
                                            mock_config_get,
                                            sqnotes_obj : SQNotes,
                                            test_notes_directory
                                            ):
            db_filename = 'sqnotes_index.db'
            mock_config_get.return_value = "[notes_dir]/" + db_filename
            default_db_file_path = sqnotes_obj._get_default_db_file_path()
            
            expected_path = os.path.join(test_notes_directory, db_filename)
            assert default_db_file_path == expected_path
            
        
        @pytest.mark.usefixtures("mock_get_notes_dir_from_config")
        @patch('os.path.expanduser', lambda x : f"expanded:{x}")
        @patch.object(SQNotesConfig, 'get')
        def it_applies_user_expansion_to_configured_path (
                                            mock_config_get,
                                            sqnotes_obj : SQNotes,
                                            test_notes_directory
                                            ):
            db_filename = 'sqnotes_index.db'
            pre_expanded_path = f"~/{db_filename}"
            mock_config_get.return_value = pre_expanded_path
            default_db_file_path = sqnotes_obj._get_default_db_file_path()
            expanded_path = f"expanded:{pre_expanded_path}"
            assert default_db_file_path == expanded_path
            
            
    def describe_set_user_db_path():
        
        def describe_user_input_is_empty():
            @patch.object(SQNotes, '_get_default_db_file_path')
            @patch.object(UserConfigurationHelper, 'set_setting_to_user_config')
            def it_sets_the_default_to_user_config(
                                                mock_set_setting_to_user_config,
                                                mock_get_default_db_file_path,
                                                sqnotes_obj : SQNotes,
                                                mock_sqnotes_config_test_data
                                                ):
                
                db_file_name = 'sqnotes_index.db'
                mock_sqnotes_config_test_data[sqnotes_obj.DATABASE_FILE_NAME_KEY] = db_file_name
                default_path = "/path/to/db/file"
                mock_get_default_db_file_path.return_value = default_path
                expected_saved_path = default_path + os.sep + db_file_name
                sqnotes_obj._set_user_db_path()
                mock_set_setting_to_user_config.assert_called_once_with(key=sqnotes_obj.DB_FILE_PATH_KEY, value = expected_saved_path)
                
                
        def describe_user_specified_directory_set():
        
            @patch.object(UserConfigurationHelper, 'set_setting_to_user_config')
            def it_sets_the_user_specified_path_to_user_config(
                                                    mock_set_setting_to_user_config,
                                                    sqnotes_obj : SQNotes,
                                                    mock_sqnotes_config_test_data
                                                        ):
                db_file_name = 'sqnotes_index.db'
                mock_sqnotes_config_test_data[sqnotes_obj.DATABASE_FILE_NAME_KEY] = db_file_name
                user_specified_directory = "~/some_directory"
                expected_saved_path = user_specified_directory + os.sep + db_file_name
                sqnotes_obj._set_user_db_path(user_specified_directory=user_specified_directory)
                mock_set_setting_to_user_config.assert_called_once_with(
                            key=sqnotes_obj.DB_FILE_PATH_KEY, 
                            value = expected_saved_path
                        )
        

    def describe_get_db_file_path_from_user_config():
        
        @patch.object(UserConfigurationHelper, 'get_setting_from_user_config')
        def it_returns_db_file_path_from_config(
                                                mock_get_setting_from_user_config,
                                                sqnotes_obj : SQNotes,
                                            ):
            configured_path = "configured/path"
            mock_get_setting_from_user_config.return_value = configured_path
            found_db_path = sqnotes_obj._get_db_path_from_user_config()
            mock_get_setting_from_user_config.assert_called_once_with(key=sqnotes_obj.DB_FILE_PATH_KEY)
            assert found_db_path == configured_path
            
    
    def describe_setting_and_checking_database_is_set_up():
        
        def describe_get_is_database_set_up():
            
            def describe_user_config_globals_say_is_set_up():
            
                
                def it_returns_true(
                                                                sqnotes_obj,
                                                                user_config_data
                                                                    ):
                    
                    user_config_data['global'][sqnotes_obj.DATABASE_IS_SET_UP_KEY] = 'yes'
                    assert sqnotes_obj._get_is_database_set_up()
                    
            def describe_user_config_globals_say_is_not_set_up():
            
                
                def it_returns_false(
                                                                sqnotes_obj,
                                                                user_config_data
                                                                    ):
                    
                    user_config_data['global'][sqnotes_obj.DATABASE_IS_SET_UP_KEY] = 'no'
                    assert not sqnotes_obj._get_is_database_set_up()
                
        def describe_set_database_set_up():
            

            @patch.object(UserConfigurationHelper, 'set_global_to_user_config')
            def it_sets_global_on_user_config_helper(
                                                            mock_set_global,
                                                            sqnotes_obj
                                                                ):
                sqnotes_obj._set_database_is_set_up()
                mock_set_global.assert_called_once_with(key=sqnotes_obj.DATABASE_IS_SET_UP_KEY, value='yes')
                    

if __name__ == '__main__':
    unittest.main()
