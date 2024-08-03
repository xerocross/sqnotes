

from sqnotes.injection_configuration_module import InjectionConfigurationModule
from sqnotes.sqnotes_module import SQNotes
from injector import Injector, provider
import pytest
import os
import yaml
from unittest.mock import patch
from sqnotes.sqnotes_config_module import SQNotesConfig


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
def sqnotes_real(sqnotes_config):
    class TestInjectionConfigurationModule(InjectionConfigurationModule):
    
        @provider
        def provide_config_file_path(self) -> str:
            return test_config_path
        
        @provider
        def provide_sqnotes_config(self) -> SQNotesConfig:
            return sqnotes_config
    
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
            

        
    