import pytest
from injector import Injector, provider
from sqnotes.sqnotes_module import SQNotes
from sqnotes.database_service import DatabaseService
import tempfile
import os
import shutil
from unittest.mock import Mock, patch, MagicMock
from injector import Module, singleton
import yaml
import copy

from sqnotes.user_configuration_helper import UserConfigurationHelper
from sqnotes.encrypted_note_helper import EncryptedNoteHelper
from sqnotes.sqnotes_logger import SQNotesLogger
from sqnotes.choose_text_editor import ChooseTextEditor
from sqnotes.printer_helper import PrinterHelper
from sqnotes.path_input_helper import PathInputHelper
from sqnotes.sqnotes_config_module import SQNotesConfig
from sqnotes.injection_configuration_module import InjectionConfigurationModule
from test.test_helper import do_nothing

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = current_dir
test_root = os.path.abspath(os.path.join(current_dir, "test"))
test_resources_root = os.path.join(test_root, 'resources')
test_config_file = os.path.join(test_resources_root, 'test_config.yaml')
sqnotes_dir = os.path.join(root_dir, "src/sqnotes")
primary_config_file_path = os.path.join(sqnotes_dir, 'config.yaml')



@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    
@pytest.fixture
def mock_subprocess_call():
    with patch('subprocess.call') as mock:
        yield mock
    
    
@pytest.fixture
def mock_sqnotes_config_from_resource_file():
    
    class ConfigModule(Module):
        @provider
        def provide_config_file_path(self) -> str:
            return test_config_file
    
    injector = Injector([ConfigModule()])
    sqnotes_config : SQNotesConfig = injector.get(SQNotesConfig)
    yield sqnotes_config
    
@pytest.fixture(scope='session')
def mock_config_data():
    with open(test_config_file, 'r') as file:
        data = yaml.safe_load(file)
    yield copy.deepcopy(data)
    
@pytest.fixture
def mock_sqnotes_config_test_data(test_temp_config_dir, 
                                  test_temp_notes_dir, 
                                  mock_config_data):
    
    
    data = mock_config_data
    data['USER_CONFIG_DIR'] = str(test_temp_config_dir)
    data ['DEFAULT_NOTES_DIR'] = str(test_temp_notes_dir)
    yield data

    
@pytest.fixture
def mock_note_files(test_notes_directory):
    notes = ['test1.txt.gpg', 'test2.txt.gpg']
    note_paths = [test_notes_directory / n for n in notes]
    for p in note_paths:
        with open(p, 'w'):
            pass
        
    yield [str(p) for p in note_paths]
    for p in note_paths:
        if os.path.isfile(p):
            os.remove(p)
        
    
@pytest.fixture
def sqnotes_config_with_mocked_data(mock_sqnotes_config_test_data):
    with patch('yaml.safe_load') as mock_yaml_load:
        with patch('builtins.open'):
            mock_yaml_load.return_value = mock_sqnotes_config_test_data
            injector = Injector()
            sqnotes_config : SQNotesConfig = injector.get(SQNotesConfig)
    yield sqnotes_config
    
@pytest.fixture
def sqnotes_obj(
                database_service_open_in_memory, 
                user_configuration_helper,
                mock_path_input_helper,
                mock_encrypted_note_helper,
                sqnotes_config_with_mocked_data,
                mock_sqnotes_config_test_data):
    
    
    class SQNotesTestConfigurationModule(Module):
        
        def configure(self, binder):
            binder.bind(SQNotesLogger, to=SQNotesLogger(), scope=singleton)
            binder.bind(UserConfigurationHelper, to=user_configuration_helper, scope=singleton)
            binder.bind(PathInputHelper, to=mock_path_input_helper, scope=singleton)
            binder.bind(DatabaseService, to=database_service_open_in_memory, scope=singleton)
            binder.bind(EncryptedNoteHelper, to=mock_encrypted_note_helper, scope=singleton)
            binder.bind(SQNotesConfig, to=sqnotes_config_with_mocked_data, scope=singleton )
    
    injector = Injector([SQNotesTestConfigurationModule()])
    sqnotes_instance : SQNotes = injector.get(SQNotes)
    yield sqnotes_instance
    
@pytest.fixture
def mock_is_valid_path():
    with patch.object(PathInputHelper, 'get_path_interactive') as mock:
        yield mock

@pytest.fixture
def user_configuration_helper(test_temp_config_dir):
    injector = Injector()
    user_configuration_helper : UserConfigurationHelper = injector.get(UserConfigurationHelper)
    user_configuration_helper._set_config_dir(test_temp_config_dir)
    yield user_configuration_helper


@pytest.fixture
def database_service():
    injector = Injector()
    database_service : DatabaseService = injector.get(DatabaseService)
    yield database_service
    

@pytest.fixture
def choose_text_editor():
    choose_text_editor = ChooseTextEditor()
    yield choose_text_editor
    
@pytest.fixture
def mock_input():
    with patch('builtins.input') as mock:
        yield mock
    
    
    
@pytest.fixture
def mock_print():
    with patch('builtins.print') as mock:
        yield mock

@pytest.fixture
def mock_transaction(database_service_open_in_memory : DatabaseService):
    connection = database_service_open_in_memory._get_connection()
    yield connection
    connection.rollback()
    
@pytest.fixture
def mock_print_to_so():
    with patch.object(PrinterHelper, 'print_to_so') as mock:
        yield mock
        
        
@pytest.fixture
def mock_printer_helper_print():
    with patch.object(PrinterHelper, 'print_to_so') as mock:
        yield mock
        
        
@pytest.fixture
def mock_path_input_helper():
    injector = Injector()
    path_input_helper : PathInputHelper = injector.get(PathInputHelper)
    yield path_input_helper
        
@pytest.fixture
def mock_get_is_initialized():
    with patch.object(SQNotes, '_get_is_initialized') as mock:
        mock.return_value = True
        yield mock

@pytest.fixture
def database_service_connected_in_memory(database_service):
    database_service.connect(db_file_path = ':memory:')
    yield database_service
    database_service._get_connection().close()

@pytest.fixture
def mock_get_database_file_path(database_service):
    with patch.object(SQNotes, '_get_db_file_path') as mock:
        mock.return_value = ':memory:'
        yield mock

@pytest.fixture
def database_service_open_in_memory(database_service_connected_in_memory : DatabaseService):
    database_service_connected_in_memory.setup_database()
    yield database_service_connected_in_memory


@pytest.fixture
def mock_open_database():
    with patch.object(SQNotes, "open_database") as mock:
        yield mock
    

@pytest.fixture
def mock_get_all_note_paths():
    with patch.object(SQNotes, '_get_all_note_paths') as mock:
        mock.return_value = ['note1.txt', 'note2.txt', 'note3.txt']
        yield mock

            
@pytest.fixture
def test_notes_directory(tmp_path):
    temp_notes_path = tmp_path / "notes"
    temp_notes_path.mkdir()
    yield temp_notes_path
            
@pytest.fixture
def test_note_file(test_notes_directory):
    with tempfile.NamedTemporaryFile(mode='w', dir=test_notes_directory, delete=False) as temp_file:
        temp_filename = temp_file.name
    try:
        yield temp_filename
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
    
@pytest.fixture
def mock_get_notes_dir_from_config(test_notes_directory):
    with patch.object(SQNotes, 'get_notes_dir_from_config') as mock:
        mock.return_value = test_notes_directory
        yield mock
        
@pytest.fixture
def mock_get_user_config_dir():
    with patch.object(SQNotes, '_get_user_config_dir') as mock:
        mock.return_value = "/some/fake/dir"
        yield mock
        
@pytest.fixture
def mock_get_initial_globals_from_config():
    with patch.object(SQNotes, '_get_initial_globals_from_config') as mock:
        yield mock
        
@pytest.fixture
def mock_get_input_from_text_editor():
    with patch.object(SQNotes, '_get_input_from_text_editor') as mock:
        mock.return_value = "edited content"
        yield mock
        
@pytest.fixture
def mock_get_configured_text_editor():
    with patch.object(SQNotes, '_get_configured_text_editor') as mock:
        mock.return_value = 'vim'
        yield mock
    
@pytest.fixture
def mock_check_text_editor_is_configured():
    with patch.object(SQNotes, 'check_text_editor_is_configured') as mock:
        mock.return_value = True
        yield mock
    
@pytest.fixture
def mock_exists():
    with patch('os.path.exists') as mock:
        yield mock
    
@pytest.fixture
def mock_get_decrypted_content_in_memory():
    with patch.object(EncryptedNoteHelper, 'get_decrypted_content_in_memory') as mock:
        mock.side_effect = [f"content{x}" for x in range(1, 20)]
        yield mock
     
@pytest.fixture   
def mock_insert_new_note_into_database():
    # @patch.object(DatabaseService, 'insert_new_note_into_database')
    with patch.object(DatabaseService, 'insert_new_note_into_database') as mock:
        # mock.side_effect = [x for x in range(0, 20)]
        yield mock
   

@pytest.fixture
def test_note_filename(test_note_file):
    base_name = os.path.basename(test_note_file)
    yield base_name
    
@pytest.fixture
def mock_get_edited_note_content():
    with patch.object(SQNotes, '_get_edited_note_from_text_editor') as mock:
        yield mock

@pytest.fixture 
def mock_write_encrypted_note():
    with patch.object(EncryptedNoteHelper, 'write_encrypted_note') as mock:
        yield mock

@pytest.fixture 
def mock_get_note_id_or_raise():
    with patch.object(DatabaseService, 'get_note_id_from_database_or_raise') as mock:
        yield mock
        
@pytest.fixture 
def mock_get_note_id_or_none():
    with patch.object(DatabaseService, 'get_note_id_from_database_or_none') as mock:
        yield mock

@pytest.fixture
def mock_delete_keywords_from_database_for_note():
    with patch.object(DatabaseService, 'delete_keywords_from_database_for_note') as mock:
        yield mock
  
@pytest.fixture   
def mock_delete_temp_file():
    with patch.object(SQNotes, '_delete_temp_file') as mock:
        yield mock
     
@pytest.fixture   
def mock_get_gpg_key_email():
    with patch.object(SQNotes, 'get_gpg_key_email') as mock:
        mock.return_value = 'test@test.com'
        yield mock
        
@pytest.fixture   
def mock_is_use_ascii_armor():
    with patch.object(SQNotes,'_is_use_ascii_armor') as mock:
        mock.return_value = True
        yield mock
        
@pytest.fixture   
def mock_get_new_note_name():
    with patch.object(SQNotes,'_get_new_note_name') as mock:
        mock.side_effect = ['test1.txt.gpg', 'test2.txt.gpg']
        yield mock
        
@pytest.fixture
def mock_check_gpg_key_email():
    with patch.object(SQNotes, 'check_gpg_key_email') as mock:
        mock.return_value = True
        yield mock
     
     
@pytest.fixture
def mock_check_gpg_verified():
    with patch.object(SQNotes, '_check_gpg_verified') as mock:
        mock.return_value = True
        yield mock
     
@pytest.fixture   
def mock_extract_and_save_keywords():
    with patch.object(SQNotes, '_extract_and_save_keywords') as mock:
        yield mock

@pytest.fixture
def mock_commit_transaction():
    with patch.object(DatabaseService, 'commit_transaction') as mock:
        yield mock



@pytest.fixture
def test_note_temp_file(test_notes_directory):
    with tempfile.NamedTemporaryFile(mode='w', dir=test_notes_directory, delete=False) as temp_file:
        temp_filename = temp_file.name
    try:
        yield temp_filename
    finally:
        try:
            if os.path.exists(temp_filename):
                os.remove(temp_filename)
        except FileNotFoundError:
            pass
    
    
@pytest.fixture
def mock_builtin_open():
    with patch('builtins.open') as mock:
        yield mock
    
@pytest.fixture
def mock_subprocess_result():
    subprocess_return_mock = Mock()
    yield subprocess_return_mock

@pytest.fixture
def mock_subprocess_run(mock_subprocess_result):
    with patch('subprocess.run') as mock:
        mock.return_value = mock_subprocess_result
        yield mock
    
@pytest.fixture
def mock_decrypt_note_into_temp_file():
    with patch.object(EncryptedNoteHelper, 'decrypt_note_into_temp_file') as mock:
        yield mock
    
@pytest.fixture
def mock_temp_file():
    mock_temp_file = MagicMock(spec=tempfile.NamedTemporaryFile)
    mock_temp_file.name = "mock_temp_file_name"
    mock_temp_file.write = do_nothing
    yield mock_temp_file

@pytest.fixture
def temp_note_file(tmp_path):
    with tempfile.NamedTemporaryFile(dir=tmp_path, delete=False) as temp_file:
        yield temp_file


@pytest.fixture
def mock_NamedTemporaryFile_real(temp_note_file):
    with patch('tempfile.NamedTemporaryFile') as mock:
        mock.return_value.__enter__.return_value = temp_note_file
        yield mock


@pytest.fixture
def mock_NamedTemporaryFile(mock_temp_file):
    with patch('tempfile.NamedTemporaryFile') as mock:
        mock.return_value.__enter__.return_value = mock_temp_file
        yield mock

@pytest.fixture
def mock_encrypted_note_helper():
    injector = Injector()
    encrypted_note_helper = injector.get(EncryptedNoteHelper)
    yield encrypted_note_helper
    
    

@pytest.fixture
def test_temp_config_dir(tmp_path):
    temp_config = tmp_path / ".config"
    temp_config.mkdir()
    yield temp_config
    
@pytest.fixture
def test_temp_notes_dir(tmp_path):
    temp_notes = tmp_path / "sqnotes_notes"
    temp_notes.mkdir()
    yield temp_notes


@pytest.fixture
def sqnotes_config_data(test_temp_notes_dir, test_temp_config_dir):
    with open(primary_config_file_path, 'r') as file:
        data = yaml.safe_load(file)

    data['USER_CONFIG_DIR'] = str(test_temp_config_dir)
    data ['DEFAULT_NOTES_DIR'] = str(test_temp_notes_dir)
    yield data

@pytest.fixture
def sqnotes_config(sqnotes_config_data):
    class ConfigurationModule(InjectionConfigurationModule):
        @provider
        def provide_config_file_path(self) -> str:
            return test_config_file
        
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
def user_configuration_helper_for_integration(user_config_data, test_temp_config_dir):
    injector = Injector()
    user_config_helper : UserConfigurationHelper = injector.get(UserConfigurationHelper)
    user_config_helper._set_config_dir(config_dir = test_temp_config_dir)
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
def sqnotes_real(sqnotes_config, user_configuration_helper_for_integration):
    class TestInjectionConfigurationModule(InjectionConfigurationModule):
    
        @provider
        def provide_config_file_path(self) -> str:
            return test_config_file
        
        @provider
        def provide_sqnotes_config(self) -> SQNotesConfig:
            return sqnotes_config
        
        @provider
        def provide_user_configuration_helper(self) -> UserConfigurationHelper:
            return user_configuration_helper_for_integration
    
    injector = Injector([TestInjectionConfigurationModule()])
    sqnotes_instance : SQNotes = injector.get(SQNotes)
    yield sqnotes_instance

    