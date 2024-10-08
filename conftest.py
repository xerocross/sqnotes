import pytest
from injector import Injector, provider
from sqnotes.sqnotes_module import SQNotes
from sqnotes.database_service import DatabaseService
import tempfile
import os
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
from test.test_helper import do_nothing, just_return

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
def mock_note_files(test_temp_notes_dir):
    notes = ['test1.txt.gpg', 'test2.txt.gpg']
    note_paths = [test_temp_notes_dir / n for n in notes]
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
                database_service, 
                user_configuration_helper_for_integration,
                mock_path_input_helper,
                mock_encrypted_note_helper,
                sqnotes_config_with_mocked_data,
                mock_sqnotes_config_test_data):
    
    
    class SQNotesTestConfigurationModule(Module):
        
        def configure(self, binder):
            binder.bind(SQNotesLogger, to=SQNotesLogger(), scope=singleton)
            binder.bind(UserConfigurationHelper, to=user_configuration_helper_for_integration, scope=singleton)
            binder.bind(PathInputHelper, to=mock_path_input_helper, scope=singleton)
            binder.bind(DatabaseService, to=database_service, scope=singleton)
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
    with patch.object(SQNotes, '_get_db_path_from_user_config') as mock:
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

            
# @pytest.fixture
# def test_notes_directory(tmp_path):
#     temp_notes_path = tmp_path / "notes"
#     temp_notes_path.mkdir()
#     yield temp_notes_path
            
@pytest.fixture
def test_note_file(test_temp_notes_dir):
    with tempfile.NamedTemporaryFile(mode='w', dir=test_temp_notes_dir, delete=False) as temp_file:
        temp_filename = temp_file.name
    try:
        yield temp_filename
    finally:
        if os.path.exists(temp_filename):
            os.remove(temp_filename)
    
@pytest.fixture
def mock_get_notes_dir_from_config(test_temp_notes_dir):
    with patch.object(SQNotes, 'get_notes_dir_from_config') as mock:
        mock.return_value = str(test_temp_notes_dir)
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
def mock_user_input():
    mock_user_input = {
    'input' : 'test input'    
    }
    yield mock_user_input
        
def mock_get_input_from_text_editor_handler(_, text_editor, user_input):
    
    pass
        
@pytest.fixture
def mock_get_input_from_text_editor(mock_user_input):
    with patch.object(SQNotes, '_get_input_from_text_editor') as mock:
        mock.return_value = mock_user_input['input']
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
def mock_get_decrypted_content_in_memory_integration():
    
    def mock_get_decrypted_content_in_memory_handler(self, note_path):
        with open(note_path, 'r') as open_file:
            return open_file.read()
    
    with patch.object(EncryptedNoteHelper, 'get_decrypted_content_in_memory', mock_get_decrypted_content_in_memory_handler):
        yield
     
@pytest.fixture   
def mock_insert_new_note_into_database():
    # @patch.object(DatabaseService, 'insert_new_note_into_database')
    with patch.object(DatabaseService, 'insert_new_note_into_database') as mock:
        # mock.side_effect = [x for x in range(0, 20)]
        yield mock
        
@pytest.fixture
def plaintext_temp_file(tmp_path):
    with tempfile.NamedTemporaryFile(mode='w', dir=tmp_path, delete=False) as temp_file:
        yield temp_file
   
@pytest.fixture
def mock_write_plaintext_to_temp_file(plaintext_temp_file):
    plaintext_temp_file_path = plaintext_temp_file.name
    def handler (_, note_content, config=None):
        with open(plaintext_temp_file_path, 'w') as file:
            file.write(note_content)
        return plaintext_temp_file_path
    
    
    patcher = patch.object(EncryptedNoteHelper, '_write_plaintext_to_temp_file', handler)
    patcher.start()
    yield
    patcher.stop()

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
def test_note_temp_file(test_temp_notes_dir):
    with tempfile.NamedTemporaryFile(mode='w', dir=test_temp_notes_dir, delete=False) as temp_file:
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
def mock_get_temp_plaintext_file(plaintext_temp_file):
    with patch.object(EncryptedNoteHelper, '_get_temp_plaintext_file') as mock:
        mock.return_value = plaintext_temp_file.name
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
def user_config_data(test_temp_notes_dir):
    data = {
        'global' : {},
        'settings': {
            'DB_FILE_PATH':':memory:',
            "notes_path" : str(test_temp_notes_dir)
        },
        
    }
    yield data
    
    
@pytest.fixture
def user_configuration_helper_2(user_config_data, test_temp_config_dir):
    injector = Injector()
    user_config_helper : UserConfigurationHelper = injector.get(UserConfigurationHelper)
    user_config_helper._set_config_dir(config_dir = test_temp_config_dir)
    user_config_helper.data = user_config_data
    
    with patch.object(UserConfigurationHelper, 'get_setting_from_user_config', get_setting):
        with patch.object(UserConfigurationHelper, 'get_global_from_user_config', get_global):
            yield user_config_helper
    
@pytest.fixture
def user_configuration_helper_for_integration(user_config_data, test_temp_config_dir):
    injector = Injector()
    user_config_helper : UserConfigurationHelper = injector.get(UserConfigurationHelper)
    user_config_helper._set_config_dir(config_dir = test_temp_config_dir)
    def get_setting (_, key):
        return user_config_data['settings'][key]
    
    def get_global (_, key):
        return user_config_data['global'][key]
    
    def set_setting (_, key, value):
        user_config_data['settings'][key] = value
        
    def set_global (_, key, value):
        user_config_data['global'][key] = value
    
    get_setting_patcher = patch.object(UserConfigurationHelper, 'get_setting_from_user_config', get_setting)
    get_global_patcher = patch.object(UserConfigurationHelper, 'get_global_from_user_config', get_global)
    set_setting_patcher = patch.object(UserConfigurationHelper, 'set_setting_to_user_config', set_setting)
    set_global_patcher = patch.object(UserConfigurationHelper, 'set_global_to_user_config', set_global)
    get_setting_patcher.start()
    get_global_patcher.start()
    set_setting_patcher.start()
    set_global_patcher.start()
    yield user_config_helper
    set_setting_patcher.stop()
    get_global_patcher.stop()
    get_setting_patcher.stop()
    set_global_patcher.stop()


def mock_call_gpg_subprocess_write(_, in_commands):
    note_file_path = in_commands['output_path']
    infile = in_commands['infile']
    with open(infile, 'r') as in_file:
        infile_content = in_file.read()
    with open(note_file_path, 'w') as out_file:
        out_file.write(f"encrypted: {infile_content}")
    return 0

@pytest.fixture
def mock_call_gpg_subprocess_to_write_encrypted(plaintext_temp_file):
    with patch.object(EncryptedNoteHelper, '_call_gpg_subprocess_to_write_encrypted', mock_call_gpg_subprocess_write) as mock:
        yield mock
    
@pytest.fixture
def temp_database_file(tmp_path):
    temp_database_file = tmp_path / "sqnotes_index.db"
    patcher = patch.object(SQNotes, '_get_db_path_from_user_config', just_return(str(temp_database_file)))
    patcher.start()
    yield temp_database_file
    patcher.stop()
    
    
@pytest.fixture
def sqnotes_real(sqnotes_config, 
                 user_configuration_helper_for_integration,
                 database_service,
                 temp_database_file
                 ):
    class TestInjectionConfigurationModule(InjectionConfigurationModule):
    
        @provider
        def provide_config_file_path(self) -> str:
            return test_config_file
        
        @provider
        def provider_database_service(self) -> DatabaseService:
            return database_service
        
        @provider
        def provide_sqnotes_config(self) -> SQNotesConfig:
            return sqnotes_config
        
        @provider
        def provide_user_configuration_helper(self) -> UserConfigurationHelper:
            return user_configuration_helper_for_integration
    
    injector = Injector([TestInjectionConfigurationModule()])
    sqnotes_instance : SQNotes = injector.get(SQNotes)
    yield sqnotes_instance

@pytest.fixture
def mock_gpg_key_email():
    yield 'test@test.com'

@pytest.fixture
def sqnotes_with_initialized_user_data (
                                    sqnotes_real : SQNotes,
                                    user_config_data,
                                    test_temp_notes_dir,
                                    mock_gpg_key_email
                                ):
    user_config_data['global']['initialized'] = 'yes'
    user_config_data['global'][sqnotes_real.DATABASE_IS_SET_UP_KEY] = 'no'
    user_config_data['settings'].update({
                'armor' : 'yes',
                'gpg_key_email': mock_gpg_key_email,
                'text_editor' : 'vim',
                'notes_path' : test_temp_notes_dir
            })
    sqnotes_real.open_database()
        
    yield sqnotes_real
    
    
@pytest.fixture
def mock_decrypt_note_into_temp_file_for_integration(plaintext_temp_file):
    
    def mock_decrypt_into_temp(_, note_path):
        decrypted_note_path = str(plaintext_temp_file.name)
        with open(note_path, 'w') as file:
            file.write('decrypted note content')
        return decrypted_note_path
    
    with patch.object(EncryptedNoteHelper, 'decrypt_note_into_temp_file', mock_decrypt_into_temp) as mock:
        yield mock

    