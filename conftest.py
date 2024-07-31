import pytest
from injector import Injector
from sqnotes.sqnotes_module import SQNotes
from sqnotes.database_service import DatabaseService
import tempfile
import os
import shutil
from unittest.mock import Mock, patch
from injector import Module, singleton

from sqnotes.configuration_module import ConfigurationModule
from sqnotes.encrypted_note_helper import EncryptedNoteHelper
from sqnotes.sqnotes_logger import SQNotesLogger

@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    
    

    
@pytest.fixture
def sqnotes_obj(test_configuration_dir, database_service_open_in_memory):
    
    
    class SQNotesTestConfigurationModule(Module):
        def configure(self, binder):
            binder.bind(SQNotesLogger, to=SQNotesLogger(), scope=singleton)
            binder.bind(ConfigurationModule, to=ConfigurationModule(), scope=singleton)
            binder.bind(DatabaseService, to=database_service_open_in_memory, scope=singleton)
    
    injector = Injector([SQNotesTestConfigurationModule()])
    sqnotes_instance : SQNotes = injector.get(SQNotes)
    sqnotes_instance.set_config_dir_override(config_dir_override = test_configuration_dir)
    yield sqnotes_instance
    
@pytest.fixture
def configuration_module(test_configuration_dir):
    injector = Injector()
    config_module : ConfigurationModule = injector.get(ConfigurationModule)
    config_module._set_config_dir(test_configuration_dir)
    yield config_module
    

@pytest.fixture
def database_service():
    injector = Injector()
    database_service : DatabaseService = injector.get(DatabaseService)
    yield database_service
    
    
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
    with patch('sqnotes.sqnotes_module.print_to_so') as mock:
        yield mock
        
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
def test_configuration_dir():
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
            
            
@pytest.fixture
def test_notes_directory():
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)
            
            
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
def mock_insert_new_note():
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
def mock_decrypt_note_into_temp_file():
    with patch.object(EncryptedNoteHelper, 'decrypt_note_into_temp_file') as mock:
        yield mock
    
            