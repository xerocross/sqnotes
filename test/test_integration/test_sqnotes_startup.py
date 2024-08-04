

from sqnotes.injection_configuration_module import InjectionConfigurationModule
from sqnotes.sqnotes_module import SQNotes
from injector import Injector, provider
import pytest
import os
import yaml
from unittest.mock import patch
from sqnotes.sqnotes_config_module import SQNotesConfig
from sqnotes.user_configuration_helper import UserConfigurationHelper
from sqnotes.encrypted_note_helper import EncryptedNoteHelper


current_dir = os.path.dirname(os.path.abspath(__file__))
test_package_dir = os.path.abspath(os.path.join(current_dir, "../"))
root_dir = os.path.join(test_package_dir, "../")
sqnotes_dir = os.path.join(root_dir, "src/sqnotes")
primary_config_file_path = os.path.join(sqnotes_dir, 'config.yaml')
test_config_path = os.path.join(test_package_dir, 'resources/test_config.yaml')


@pytest.fixture
def sqnotes_config_data(tmp_path):
    with open(primary_config_file_path, 'r') as file:
        data = yaml.safe_load(file)

    
    temp_config = tmp_path / ".config"
    temp_config.mkdir()
    
    temp_notes = tmp_path / "sqnotes_notes"
    temp_notes.mkdir()
    data['USER_CONFIG_DIR'] = str(temp_config)
    data ['DEFAULT_NOTES_DIR'] = str(temp_notes)
    yield data

@pytest.fixture
def sqnotes_config(sqnotes_config_data):
    class ConfigurationModule(InjectionConfigurationModule):
        @provider
        def provide_config_file_path(self) -> str:
            return test_config_path
        
    with patch("builtins.open"):
        with patch("yaml.safe_load") as safe_load:
            safe_load.return_value = sqnotes_config_data
            
            injector = Injector([ConfigurationModule()])
            sqnotes_config = injector.get(SQNotesConfig)
    yield sqnotes_config


@pytest.fixture
def user_config_data():
    data = {}
    yield data
    
    

    
@pytest.fixture
def user_configuration_helper(user_config_data):
    injector = Injector()
    user_config_helper = injector.get(UserConfigurationHelper)
    
    def get_setting (_, key):
        return user_config_data['settings'][key]
    
    def get_global (_, key):
        return user_config_data['global'][key]
    
    with patch.object(UserConfigurationHelper, 'get_setting_from_user_config', get_setting):
        with patch.object(UserConfigurationHelper, 'get_global_from_user_config', get_global):
            yield user_config_helper
    
@pytest.fixture
def gpg_subprocess_call():
    with patch.object(EncryptedNoteHelper, '_call_gpg_subprocess') as mock:
        mock.return_value = 0
        yield mock
    
@pytest.fixture
def sqnotes_real(sqnotes_config, user_configuration_helper):
    class TestInjectionConfigurationModule(InjectionConfigurationModule):
    
        @provider
        def provide_config_file_path(self) -> str:
            return test_config_path
        
        @provider
        def provide_sqnotes_config(self) -> SQNotesConfig:
            return sqnotes_config
        
        @provider
        def provide_user_configuration_helper(self) -> UserConfigurationHelper:
            return user_configuration_helper
    
    injector = Injector([TestInjectionConfigurationModule()])
    sqnotes_instance : SQNotes = injector.get(SQNotes)
    yield sqnotes_instance

def describe_sqnotes():
    
    def describe_get_init_globals_from_config():
        
        
        def it_gets_initialized_no(
                        sqnotes_real : SQNotes
                        ):
            initial_globals = sqnotes_real._get_initial_globals_from_config()
            assert initial_globals['initialized'] == 'no'
        
        
        def it_gets_database_is_set_up_no(
                        sqnotes_real : SQNotes
                        ):
            initial_globals = sqnotes_real._get_initial_globals_from_config()
            assert initial_globals['database_is_set_up'] == 'no'
            

    def describe_new_note_method():
        
        
        @pytest.mark.usefixtures(
            "mock_check_gpg_verified",
            "mock_open_database",
            "mock_extract_and_save_keywords",
            "mock_insert_new_note_into_database",
            "mock_commit_transaction",
        )
        def it_creates_a_new_note_in_notes_dir(
                            sqnotes_real : SQNotes,
                            mock_get_input_from_text_editor,
                            sqnotes_config_data,
                            user_config_data,
                            mock_get_new_note_name,
                            gpg_subprocess_call
                            ):
            test_note_content = "test note content"
            mock_get_input_from_text_editor.return_value = test_note_content
            notes_dir = sqnotes_config_data['DEFAULT_NOTES_DIR']
            user_config_data['global'] = {
                'initialized' : 'yes',
                'database_is_set_up' : 'yes'
            }
            user_config_data['settings'] = {
                'armor' : 'yes',
                'gpg_key_email': 'test@test.com',
                'text_editor' : 'vim',
                'notes_path' : notes_dir
            }
            new_note_name = "test.txt.gpg"
            mock_get_new_note_name.side_effect = [new_note_name]
            sqnotes_real.new_note()
            expected_new_note_path = os.path.join(notes_dir, new_note_name)
            print(f"path: {expected_new_note_path}")
            gpg_subprocess_call.assert_called()
            _, kwargs = gpg_subprocess_call.call_args
            in_commands = kwargs['in_commands']
            assert in_commands == None
            
            
    