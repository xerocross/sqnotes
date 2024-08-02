
from unittest.mock import patch
import pytest
from sqnotes.encrypted_note_helper import EncryptedNoteHelper
from sqnotes.user_configuration_helper import UserConfigurationHelper, ConfigFileReadingException,\
    ConfigModuleNotInitializedException
import configparser
from test.test_helper import do_nothing, touch

def describe_user_configuration_helper():


    def describe_the_open_or_create_and_open_user_config_method():
        """the open_or_create_and_open_user_config_file method"""
    
    
        def it_does_not_raise_on_first_call(
                                    user_configuration_helper : UserConfigurationHelper
                                    ):
            try:
                user_configuration_helper.open_or_create_and_open_user_config_file()
            except Exception as e:
                pytest.fail(f"Unexpected exception raised: {e}")
    
        @patch.object(configparser.ConfigParser, 'read')
        @patch.object(UserConfigurationHelper, 'is_config_file_exists')
        @patch.object(UserConfigurationHelper, '_is_config_dir_exists')
        def it_raises_read_exception_if_encounters_exception_reading_existing_config_file(
                                                mock_is_config_dir_exists,
                                                mock_is_config_file_exists,
                                                mock_config_parser_read,
                                                user_configuration_helper : UserConfigurationHelper,
                                                    ):
            
            """raises read exception if encounters exception reading existing config file """
            mock_is_config_dir_exists.return_value = True
            mock_is_config_file_exists.return_value = True
            config_file = user_configuration_helper._get_config_file()
            touch(config_file) # create empty config file
            mock_config_parser_read.side_effect = Exception
            
            with pytest.raises(ConfigFileReadingException):
                user_configuration_helper.open_or_create_and_open_user_config_file()
            
        
        def it_raises_not_initialized_exception_if_get_setting_method_called_before_init(user_configuration_helper):
            """raises not initialized exception if get setting method called before initialized"""
            test_setting_key = 'key'
            with pytest.raises(ConfigModuleNotInitializedException):
                user_configuration_helper.get_setting_from_user_config(key=test_setting_key)
                
        def it_raises_not_initialized_exception_if_get_global_method_called_before_init(user_configuration_helper):
            """raises not initialized exception if get global method called before initialized"""
            test_global_key = 'key'
            with pytest.raises(ConfigModuleNotInitializedException):
                user_configuration_helper.get_global_from_user_config(key=test_global_key)
                
                
        def it_raises_not_initialized_exception_if_set_setting_method_called_before_init(user_configuration_helper):
            """raises not initialized exception if set setting method called before initialized"""
            test_setting_key = 'key'
            test_value = 'value'
            with pytest.raises(ConfigModuleNotInitializedException):
                user_configuration_helper.set_setting_to_user_config(key=test_setting_key, value=test_value)
                
        def it_raises_not_initialized_exception_if_set_global_method_called_before_init(user_configuration_helper):
            """raises not initialized exception if get setting method called before initialized"""
            test_global_key = 'key'
            test_value = 'value'
            with pytest.raises(ConfigModuleNotInitializedException):
                user_configuration_helper.set_global_to_user_config(key=test_global_key, value=test_value)
                
        def describe_config_file_does_not_exist_and_config_dir_does_exist():
            """the config file does not exist and config dir does exist"""
            
            @patch.object(UserConfigurationHelper, '_save_config')
            @patch.object(UserConfigurationHelper, '_create_configuration_groups')
            @patch.object(configparser.ConfigParser, 'read')
            @patch.object(UserConfigurationHelper, 'is_config_file_exists')
            @patch.object(UserConfigurationHelper, '_is_config_dir_exists')
            def it_creates_config_groups_and_saves__config_dir_exists(
                                                                                mock_is_config_dir_exists,
                                                                                mock_is_config_file_exists,
                                                                                mock_config_parser_read,
                                                                                mock_create_configuration_groups,
                                                                                mock_save_config,
                                                                                user_configuration_helper):
                """creates config groups and saves"""
                mock_is_config_dir_exists.return_value = True
                mock_is_config_file_exists.return_value = False
                user_configuration_helper.open_or_create_and_open_user_config_file()
                mock_create_configuration_groups.assert_called_once()
                mock_save_config.assert_called_once()
                    
                
         
            @patch.object(UserConfigurationHelper, '_save_config', lambda x : None)
            @patch.object(UserConfigurationHelper, '_create_configuration_groups', lambda x : None)
            @patch.object(configparser.ConfigParser, 'read', lambda x : None)       
            @patch.object(UserConfigurationHelper, '_set_is_initialized')
            @patch.object(UserConfigurationHelper, 'is_config_file_exists')
            @patch.object(UserConfigurationHelper, '_is_config_dir_exists')
            def it_marks_initialized_on_creating_config_file__config_dir_exists(
                                                                                mock_is_config_dir_exists,
                                                                                mock_is_config_file_exists,
                                                                                mock_set_initialized,
                                                                                user_configuration_helper):
                """marks initialized"""
                mock_is_config_dir_exists.return_value = True
                mock_is_config_file_exists.return_value = False
                user_configuration_helper.open_or_create_and_open_user_config_file()
                mock_set_initialized.assert_called_once()
                
                
            @patch.object(UserConfigurationHelper, '_set_all_globals', do_nothing)
            @patch.object(UserConfigurationHelper, '_set_all_settings')
            @patch.object(UserConfigurationHelper, '_save_config')
            @patch.object(UserConfigurationHelper, '_create_configuration_groups')
            @patch.object(configparser.ConfigParser, 'read')
            @patch.object(UserConfigurationHelper, 'is_config_file_exists')
            @patch.object(UserConfigurationHelper, '_is_config_dir_exists')
            def it_accepts_and_sets_the_initial_data_from_initial_settings_dictionary(
                                                                                mock_is_config_dir_exists,
                                                                                mock_is_config_file_exists,
                                                                                mock_config_parser_read,
                                                                                mock_create_configuration_groups,
                                                                                mock_save_config,
                                                                                mock_set_all_settings,
                                                                                user_configuration_helper):
                """creates config groups and saves"""
                mock_is_config_dir_exists.return_value = True
                mock_is_config_file_exists.return_value = False
                test_init_settings = {
                    'fruit' : 'apple'
                }
                user_configuration_helper.open_or_create_and_open_user_config_file(initial_settings = test_init_settings)
                mock_set_all_settings.assert_called_once_with(initial_settings = test_init_settings)
                
            @patch.object(UserConfigurationHelper, '_set_all_settings', do_nothing)
            @patch.object(UserConfigurationHelper, '_set_all_globals')
            @patch.object(UserConfigurationHelper, '_save_config')
            @patch.object(UserConfigurationHelper, '_create_configuration_groups')
            @patch.object(configparser.ConfigParser, 'read')
            @patch.object(UserConfigurationHelper, 'is_config_file_exists')
            @patch.object(UserConfigurationHelper, '_is_config_dir_exists')
            def it_accepts_and_sets_the_initial_data_from_initial_global_dictionary(
                                                                                mock_is_config_dir_exists,
                                                                                mock_is_config_file_exists,
                                                                                mock_config_parser_read,
                                                                                mock_create_configuration_groups,
                                                                                mock_save_config,
                                                                                mock_set_all_globals,
                                                                                user_configuration_helper):
                """creates config groups and saves"""
                mock_is_config_dir_exists.return_value = True
                mock_is_config_file_exists.return_value = False
                test_init_globals = {
                    'fruit' : 'apple'
                }
                user_configuration_helper.open_or_create_and_open_user_config_file(initial_globals = test_init_globals)
                mock_set_all_globals.assert_called_once_with(initial_globals = test_init_globals)
            
            
        def describe_config_directory_does_not_exist():
            
            @patch.object(UserConfigurationHelper, '_save_config', lambda x : None)
            @patch.object(UserConfigurationHelper, '_create_configuration_groups', lambda x : None)
            @patch.object(configparser.ConfigParser, 'read', lambda x : None)
            @patch.object(UserConfigurationHelper, '_set_is_initialized', lambda x: None)
            @patch('os.makedirs')       
            @patch.object(UserConfigurationHelper, 'is_config_file_exists')
            @patch.object(UserConfigurationHelper, '_is_config_dir_exists')
            def it_creates_config_directory(
                                                mock_is_config_dir_exists,
                                                mock_is_config_file_exists,
                                                mock_makedir,
                                                user_configuration_helper
                                            ):
                mock_is_config_dir_exists.return_value = False
                mock_is_config_file_exists.return_value = False
                CONFIG_DIR = user_configuration_helper.CONFIG_DIR
                user_configuration_helper.open_or_create_and_open_user_config_file()
                mock_makedir.assert_called_once_with(CONFIG_DIR)
                
            @patch.object(UserConfigurationHelper, '_save_config', lambda x : None)
            @patch.object(UserConfigurationHelper, '_create_configuration_groups', lambda x : None)
            @patch.object(configparser.ConfigParser, 'read', lambda x : None)
            @patch('os.makedirs', do_nothing)       
            @patch.object(UserConfigurationHelper, '_set_is_initialized')
            @patch.object(UserConfigurationHelper, 'is_config_file_exists')
            @patch.object(UserConfigurationHelper, '_is_config_dir_exists')
            def it_sets_initialized(
                                                mock_is_config_dir_exists,
                                                mock_is_config_file_exists,
                                                mock_set_initialized,
                                                user_configuration_helper
                                            ):
                mock_is_config_dir_exists.return_value = False
                mock_is_config_file_exists.return_value = False
                CONFIG_DIR = user_configuration_helper.CONFIG_DIR
                user_configuration_helper.open_or_create_and_open_user_config_file()
                mock_set_initialized.assert_called()
        
        
    def describe_set_all_settings():
        
        def it_accepts_dictionary_and_puts_all_settings_on_config_settings(
                                                                        user_configuration_helper : UserConfigurationHelper
                                                                        ): 
            test_feature_key = 'use-feature'
            test_value = 'no'
            test_init_settings = {
                'fruit' : 'apple',
                test_feature_key : test_value
            }
            user_configuration_helper._create_and_set_user_config()
            user_configuration_helper._create_configuration_groups()
            user_configuration_helper.is_initialized = True
            user_configuration_helper._set_all_settings(initial_settings = test_init_settings)
            saved_value = user_configuration_helper.get_setting_from_user_config(key = test_feature_key)
            assert saved_value == test_value
            
            
    def describe_set_all_globals():
        

        def it_accepts_dictionary_and_puts_all_globals_on_config_globals(
                                                                        user_configuration_helper : UserConfigurationHelper
                                                                        ): 
            test_feature_key = 'use-feature'
            test_value = 'no'
            test_init_globals = {
                'fruit' : 'apple',
                test_feature_key : test_value
            }
            user_configuration_helper._create_and_set_user_config()
            user_configuration_helper._create_configuration_groups()
            user_configuration_helper.is_initialized = True
            user_configuration_helper._set_all_globals(initial_globals = test_init_globals)
            saved_value = user_configuration_helper.get_global_from_user_config(key = test_feature_key)
            assert saved_value == test_value



    