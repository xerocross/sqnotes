
import argparse
import os
import glob
import subprocess
import tempfile
from datetime import datetime
import sqlite3
import re
import configparser
from dotenv import load_dotenv
from sqnotes import interface_copy
import sys
from sqnotes.manual import Manual
from sqnotes.command_validator import CommandValidator
from sqnotes.encrypted_note_helper import EncryptedNoteHelper, GPGSubprocessException, CouldNotReadNoteException
from injector import inject, Injector
from sqnotes.injection_configuration_module import InjectionConfigurationModule
from sqnotes.sqnotes_logger import SQNotesLogger
from sqnotes.configuration_module import ConfigurationModule
from sqnotes.database_service import DatabaseService


VERSION = '0.2'
DEBUGGING = '--debug' in sys.argv
ASCII_ARMOR_CONFIG_KEY = "armor"
GPG_VERIFIED_KEY = "gpg_verified"
SET_TEXT_EDITOR_INTERACTIVE_FLAG = False
VIM = 'vim'
NANO = 'nano'
GPG = 'gpg'
INITIALIZED = 'initialized'
DATABASE_IS_SET_UP_KEY = 'database_is_set_up'
NO = 'no'
NOTES_PATH_KEY = 'notes_path'


SUPPORTED_TEXT_EDITORS = [
    VIM, 
    NANO
]

INIT_GLOBALS = {
    INITIALIZED : NO,
    DATABASE_IS_SET_UP_KEY : NO
}

INIT_SETTINGS = {
    
}

class EnvironmentConfigurationNotFound(Exception):
    """Raise if the environment configuration file is not found."""

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '../'))
env_file_path = os.path.join(project_root, '.production.env')
if os.getenv('TESTING') == 'true':
    env_file_path = os.path.join(project_root, '.test.env')
else:
    env_file_path = os.path.join(project_root, '.env.production')
if not os.path.exists(env_file_path):
    raise EnvironmentConfigurationNotFound()
else:
    load_dotenv(env_file_path)


USE_DIRECT_NOTE_INSERTION = os.getenv('DIRECT_NOTE_INSERTION') == "yes"

class NotesDirNotConfiguredException(Exception):
    """Exception raised if the user notes directory is not configured."""
    pass

class NotesDirNotSelectedException(Exception):
    """Exception raised if user notes directory not specified."""

class NoteNotFoundException(Exception):
    """Exception raised if attempt to open a note that is not found."""
    
class TextEditorNotConfiguredException(Exception):
    """Raise if attempted to use text editor but not configured."""
    
class DatabaseException(Exception):
    """Raise if an error occurs while interacting with the database."""

class DecryptionFailedException(Exception):
    """Raise if the GPG decryption process is not successfull."""

class NoteNotFoundInDatabaseException(Exception):
    """Raise when could not find a note reference in the database."""

class TextEditorSubprocessException(Exception):
    """Raise when an exception occurs in calling the text editor in a subprocess."""
    
  
class CouldNotRunGPG(Exception):
    """Raise when a command is called that requires GPG and GPG is not available."""




class FileInfo:
        
    def __init__(self, path, base_name):
        self.path = path
        self.base_name = base_name

class SQNotes:
    
    @inject
    def __init__(self, 
                 encrypted_note_helper: EncryptedNoteHelper,
                 sqnotes_logger : SQNotesLogger,
                 config_module : ConfigurationModule,
                 database_service : DatabaseService):
        
        self.encrypted_note_helper = encrypted_note_helper
        self.sqnotes_logger = sqnotes_logger
        sqnotes_logger.configure(debug=DEBUGGING)
        self.logger = sqnotes_logger.get_logger('SQNotes')
        self.config_module = config_module
        self.CONFIG_DIR_OVERRIDE = None
        self._INITIAL_GLOBALS = INIT_GLOBALS
        self._INITIAL_SETTINGS = INIT_SETTINGS
        self.database_service = database_service
        
    def _get_input_from_text_editor(self, TEXT_EDITOR):
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_filename = temp_file.name
        try:
            response = subprocess.call([TEXT_EDITOR, temp_filename])
            if response != 0:
                raise TextEditorSubprocessException()
        except Exception as e:
            self.logger.error("an exception occurred while attempting the text editor subprocess")
            self.logger.error(e)
            raise TextEditorSubprocessException()
        try:
            with open(temp_filename, 'r') as file:
                note_content = file.read().strip()
        finally:
            self._delete_temp_file(temp_file=temp_filename)
        return note_content
        
        
    def _get_new_note_name(self):
        is_use_armor = self._is_use_ascii_armor()
        extension = 'txt' if is_use_armor else "txt.gpg"
        datetime_string = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"{datetime_string}.{extension}"
         
         
         
    def _insert_new_note(self, note_content, notes_dir):
        
        base_filename = self._get_new_note_name()
        note_file_path = os.path.join(notes_dir, base_filename)
        try:
            enh_config = {
                'GPG_KEY_EMAIL' : self.GPG_KEY_EMAIL,
                'USE_ASCII_ARMOR' : self._is_use_ascii_armor()
            }
            
            self.encrypted_note_helper.write_encrypted_note(note_file_path=note_file_path, note_content=note_content, config=enh_config)
        
        except GPGSubprocessException as e:
            self.logger.error(e)
            message = interface_copy.GPG_SUBPROCESS_ERROR_MESSAGE() + '\n' + interface_copy.EXITING()
            self.logger.error(message)
            print(message)
            exit(1)
            
        
        note_added_message = interface_copy.NOTE_ADDED().format(base_filename)
        print(note_added_message)
    
        try:
            note_id = self._insert_new_note_into_database(note_filename_base=base_filename)
            self._extract_and_save_keywords(note_id=note_id, note_content=note_content)
            self._commit_transaction()
        except Exception as e:
            is_database_exception = self._check_for_database_exception(e)
            if is_database_exception:
                message = interface_copy.DATABASE_EXCEPTION_MESSAGE() + '\n' + interface_copy.DATA_NOT_SAVED()
                self.logger.error(message)
                self.logger.error(e)
                print(message)
            else:
                message = interface_copy.UNKNOWN_ERROR() + '\n' + interface_copy.DATA_NOT_SAVED()
                self.logger.error(message)
                self.logger.error(e)
                print(interface_copy.UNKNOWN_ERROR() + '\n' + interface_copy.DATA_NOT_SAVED())
                

    def directly_insert_note(self, text):
        self._check_gpg_verified()
        self.GPG_KEY_EMAIL = self.get_gpg_key_email()
        self.check_gpg_key_email()
        NOTES_DIR = self.get_notes_dir_from_config()
        try:
            self.open_database()
        except Exception as e:
            message = interface_copy.COULD_NOT_OPEN_DATABASE() + ' ' + interface_copy.EXITING()
            print(message)
            exit(1)
            
        self._insert_new_note(note_content=text, notes_dir=NOTES_DIR)

    def new_note(self):
        self._check_gpg_verified()
        self.GPG_KEY_EMAIL = self.get_gpg_key_email()
        self.check_gpg_key_email()
        NOTES_DIR = self.get_notes_dir_from_config()
        self.check_text_editor_is_configured()
        TEXT_EDITOR = self._get_configured_text_editor()
        
        try:
            self.open_database()
        except Exception as e:
            message = interface_copy.COULD_NOT_OPEN_DATABASE() + ' ' + interface_copy.EXITING()
            print(message)
            exit(1)

        try:        
            note_content = self._get_input_from_text_editor(TEXT_EDITOR=TEXT_EDITOR)
        except TextEditorSubprocessException:
            message = interface_copy.TEXT_EDITOR_SUBPROCESS_ERROR().format(self._get_configured_text_editor())
            self.logger.error(message)
            print(message)
            exit(1)
        
        self._insert_new_note(note_content=note_content, notes_dir=NOTES_DIR)
        
        

    def _extract_and_save_keywords(self, note_id, note_content):
        keywords = self._extract_keywords(note_content)
        keyword_ids = []
        for keyword in keywords:
            keyword_id = self._insert_keyword_into_database(keyword)
            keyword_ids.append(keyword_id)
    
        for keyword_id in keyword_ids:
            self.insert_note_keyword_into_database(note_id, keyword_id)
        
    
    def _check_initialized(self):
        value = self.config_module.get_global_from_user_config(INITIALIZED)
        self.logger.debug(f"checking initialized: {value}")
        return (self.config_module.get_global_from_user_config(INITIALIZED) == 'yes')
    
    def _get_all_keywords_from_database(self):
        self.cursor.execute('SELECT keyword FROM keywords')
        rows = self.cursor.fetchall()
        keywords = [row[0] for row in rows]
        return keywords
    
    
    def print_all_keywords(self):
        self.open_database()
        keywords = self._get_all_keywords_from_database()
        for kw in keywords:
            print(kw)
    

    
    def _delete_keywords_from_database_for_note(self, note_id):
        self.cursor.execute('DELETE FROM note_keywords WHERE note_id = ?', (note_id,))
    
    def _delete_temp_file(self, temp_file):
        if os.path.exists(temp_file):
                os.remove(temp_file)
                
    
    def _get_edited_note_from_text_editor(self, temp_filename):
        TEXT_EDITOR = self._get_configured_text_editor()
        edit_process = subprocess.run([TEXT_EDITOR, temp_filename], check=True)
    
        # Ensure Vim exited properly before proceeding
        if edit_process.returncode != 0:
            raise Exception("Editing failed")
        with open(temp_filename, 'r') as file:
            edited_content = file.read().strip()
        return edited_content
    
    
    def _get_available_text_editors(self):
        available_editors = []
        for editor in SUPPORTED_TEXT_EDITORS:
            validator_function = CommandValidator.get_validator_by_command(command_string=editor)
            if validator_function is None:
                continue
            editor_is_supported = validator_function()
            if editor_is_supported:
                available_editors.append(editor)
        return available_editors
    
    def check_available_text_editors(self):
        available_editors = self._get_available_text_editors()
        if len(available_editors) > 0:
            print("supported text editors installed:")
            print(available_editors)
        else:
            print("No supported text editors installed.")
            print(f"Supported text editors include these: {', '.join(SUPPORTED_TEXT_EDITORS)}.")
    
    
    def edit_note(self, filename):
        self.GPG_KEY_EMAIL = self.get_gpg_key_email()
        self.check_gpg_key_email()
        NOTES_DIR = self.get_notes_dir_from_config()
        self.check_text_editor_is_configured
        self.TEXT_EDITOR = self._get_configured_text_editor()
        self.open_database()
        
        note_path = os.path.join(NOTES_DIR, filename)
        if not os.path.exists(note_path):
            raise NoteNotFoundException()
    
        temp_dec_filename = ''
        try:
            temp_dec_filename = self.encrypted_note_helper.decrypt_note_into_temp_file(note_path=note_path)
            edited_content = self._get_edited_note_from_text_editor(temp_filename=temp_dec_filename)
            
            print("edited_content:")
            print(edited_content)
            self.encrypted_note_helper.write_encrypted_note(note_file_path=note_path, note_content=edited_content)
        except GPGSubprocessException as e:
            self.logger.error(e)
            message = interface_copy.GPG_SUBPROCESS_ERROR_MESSAGE() + '\n' + interface_copy.EXITING()
            print(message)
            self.logger.error(message)
            self._delete_temp_file(temp_file=temp_dec_filename)
            exit(1)
        finally:
            self._delete_temp_file(temp_file=temp_dec_filename)
    
        try:
            note_id = self._get_note_id_from_database_or_raise(filename = filename)
            self._delete_keywords_from_database_for_note(note_id)
            self._extract_and_save_keywords(note_id=note_id, note_content=edited_content)
            self._commit_transaction()
                
        except Exception:
            raise DatabaseException()
            
        print(f"Note edited: {filename}")
    
    def _get_note_id_from_database_or_raise(self, filename):
        self.cursor.execute('SELECT id FROM notes WHERE filename = ?', (filename,))
        result = self.cursor.fetchone()
        if result:
            note_id = result[0]
            return note_id
        else:
            raise NoteNotFoundInDatabaseException()
        
    def _get_note_id_from_database_or_none(self, filename):
        self.cursor.execute('SELECT id FROM notes WHERE filename = ?', (filename,))
        result = self.cursor.fetchone()
        if result:
            note_id = result[0]
            return note_id
        else:
            return None
        
        
    def _check_for_database_exception(self, e):
        return (isinstance(e, sqlite3.IntegrityError) 
            or isinstance(e, sqlite3.OperationalError)
            or isinstance(e, sqlite3.ProgrammingError)
            or isinstance(e, sqlite3.DataError)
            or isinstance(e, sqlite3.InternalError)
            or isinstance(e, sqlite3.InterfaceError)
            or isinstance(e, sqlite3.DatabaseError)
            or isinstance(e, sqlite3.NotSupportedError)
            )
        
    def _handle_database_exception(self, e):
        self.logger.error("encountered a database exception")
        self.logger.error(e)
        print(interface_copy.DATABASE_EXCEPTION_MESSAGE())

    
    def _extract_keywords(self, content):
        # Extract hashtags using regular expression
        tags = [match[1:] for match in re.findall(r'\B#\w+\b', content)]
        unique_tags = set(tags)
        return list(unique_tags)
    
    def rescan_for_database(self):
        NOTES_DIR = self.get_notes_dir_from_config()
        self.open_database()
        files = self._get_all_note_paths(notes_dir = NOTES_DIR)
        files_info = [FileInfo(path = file, base_name = os.path.basename(file)) for file in files]
        
        for file_info in files_info:
            content = self.encrypted_note_helper.get_decrypted_content_in_memory(note_path=file_info.path)
            try:
                note_id = self.database_service.get_note_id_from_database_or_none(filename=file_info)
                
                if note_id is None:
                    note_id = self.database_service.insert_new_note_into_database(note_filename_base=file_info.base_name)
                
                self.database_service.delete_keywords_from_database_for_note(note_id=note_id)
                self._extract_and_save_keywords(note_id=note_id, note_content=content)
                self.database_service.commit_transaction()
                    
            except Exception:
                raise DatabaseException()
        print("rescan complete")
    
    def get_db_file_path(self, notes_dir):

        if os.getenv('TESTING') == 'true':
            return os.getenv('DATABASE_URL')
        else:    
            return os.path.join(notes_dir, os.getenv('DEFAULT_DATABASE_NAME'))
        
    
    def get_notes_dir_from_config(self):
        self.logger.debug(f"about to call to get notes dir from config")
        notes_dir_path = self.config_module.get_setting_from_user_config(key=NOTES_PATH_KEY)
        if notes_dir_path is None:
            raise NotesDirNotConfiguredException()
        else:
            return notes_dir_path
        
    def _get_configured_text_editor(self):
        text_editor = self.config_module.get_setting_from_user_config('text_editor')
        
        if text_editor is None:
            raise TextEditorNotConfiguredException()
        return text_editor
    
    def _is_text_editor_configured(self):
        text_editor = self.config_module.get_setting_from_user_config('text_editor')
        return text_editor is not None and text_editor != ''
    
    def get_setting_from_user_config(self, key):
        if 'settings' in self.user_config and key in self.user_config['settings']:
            return self.user_config['settings'][key]
        else:
            return None
        
    def insert_note_keyword_into_database(self, note_id, keyword_id):
        self.database_service.insert_note_keyword_into_database(note_id=note_id, keyword_id=keyword_id)

    def _get_all_note_paths(self, notes_dir):
        extensions = ['txt.gpg', 'txt']
        all_notes = []
        for ex in extensions:
            pattern = os.path.join(notes_dir, f"*.{ex}")
            files = glob.glob(pattern)
            all_notes.extend(files)
        return all_notes
        
    def notes_list(self):
        self.logger.debug("printing notes list")
        notes_dir = self.get_notes_dir_from_config()
        files = self._get_all_note_paths(notes_dir=notes_dir)
        filenames = [os.path.basename(file) for file in files]
        for file in filenames:
            self.logger.debug(f"note found: {file}")
            print(file)
        
    def set_config_dir_override(self, config_dir_override):
        self.CONFIG_DIR_OVERRIDE = config_dir_override
    
    def _load_setup_configuration(self):
        # Configurable directory for storing notes and database location
        self.DEFAULT_NOTE_DIR = os.path.expanduser(os.getenv('DEFAULT_NOTES_PATH'))
        
        if self.CONFIG_DIR_OVERRIDE is not None:
            self.CONFIG_DIR = self.CONFIG_DIR_OVERRIDE
            self.logger.debug(f"config dir override set;setting sqnotes CONFIG_DIR = {self.CONFIG_DIR}")
        else:
            self.CONFIG_DIR = os.path.expanduser(os.getenv('DEFAULT_CONFIG_DIR_PATH'))
            self.logger.debug(f" setting sqnotes CONFIG_DIR = {self.CONFIG_DIR}")
        self.CONFIG_FILE = os.path.join(self.CONFIG_DIR, "config.ini")
        
        
    def _setup_user_configuration(self):
        self.logger.debug(f"setting config module config dir value to {self.CONFIG_DIR}")
        self.config_module._set_config_dir(config_dir=self.CONFIG_DIR)
        self.config_module.open_or_create_and_open_user_config_file(
                                                        initial_globals = self._INITIAL_GLOBALS,
                                                        initial_settings = self._INITIAL_SETTINGS
                                                )
        
    def _generate_initial_user_config_information(self):
        self.config_module.set_global_to_user_config(key=INITIALIZED, value='no')
        self.config_module.set_global_to_user_config(key='database_is_setup', value='no')
        
        
    def _get_database_cursor(self):
        return self.cursor
    
    def _get_database_connection(self):
        return self.conn
    
    def open_database(self):
        notes_dir = self.get_notes_dir_from_config()
        if notes_dir is None:
            raise NotesDirNotSelectedException()
        self.DB_PATH = self.get_db_file_path(notes_dir)
        self.database_service.connect(db_file_path = self.get_db_file_path(notes_dir))
        
        
        self.logger.debug(f"opening database at {self.DB_PATH}")
        try:
            self.conn = sqlite3.connect(self.DB_PATH)
            self.cursor = self.conn.cursor()
        except Exception as e:
            self.logger.error(f"could not open database at {self.DB_PATH}")
            self.logger.error(e)
            raise e
        
        is_database_set_up = self._check_is_database_set_up()
        if not is_database_set_up:
            self.logger.debug("found database not set up")
            self.setup_database()
    
    
    def prompt_for_user_notes_path(self):
        user_input_notes_path = None
        attempt_num = 0
        max_attempts = 2
        while user_input_notes_path is None:
            prompt = "Please enter a path for saving your notes \nin the format '[full_path_to_parent]/[note_directory]'. \nPress enter to use default '{}'.".format(self.DEFAULT_NOTE_DIR)
            user_input_notes_path = input(prompt + '>')
        
            if user_input_notes_path == '':
                selected_path = self.DEFAULT_NOTE_DIR
                return selected_path
            else:
                selected_path = user_input_notes_path
                success = self._try_to_make_path(selected_path)
                
                if success is False:
                    if attempt_num < max_attempts:
                        attempt_num+=1
                        print("Please try again.")
                        user_input_notes_path = None
                    else:
                        print("Failed multiple times; you can try running this command again.")
                        exit(1)
                else:
                    return selected_path
        
    
    def prompt_to_initialize(self):
        print("sqnotes not initialized; please run initialization")
        
        
    def run_git_command(self, args):
        subprocess.call(['git'] + args, cwd=self.NOTES_DIR)
    
    def _save_config(self):
        with open(self.CONFIG_FILE, 'w') as configfile:
            self.user_config.write(configfile)
    
    
    def _print_note(self, note_path, decrypted_content):
        print(f"{note_path}:\n{decrypted_content}")
    
    
    def _query_notes_by_keywords(self, notes_dir, keywords):
        self.cursor.execute('''
                SELECT n.filename
                FROM notes n
                JOIN note_keywords nk ON n.id = nk.note_id
                JOIN keywords k ON nk.keyword_id = k.id
                WHERE k.keyword IN ({})
                GROUP BY n.filename
                HAVING COUNT(*) = {}
            '''.format(  ', '.join('?' for _ in keywords) , len(keywords)), keywords)
        results = self.cursor.fetchall()
        return results
    
    def search_keywords(self, keywords):
        NOTES_DIR = self.get_notes_dir_from_config()
        self.open_database()
        results = self._query_notes_by_keywords(notes_dir=NOTES_DIR, keywords=keywords)
        if results:
            print('') # blank line
            for result in results:
                note_path = os.path.join(NOTES_DIR, result[0])
                try:
                    decrypted_content = self.encrypted_note_helper.get_decrypted_content_in_memory(note_path=note_path)
                except GPGSubprocessException:
                    message = interface_copy.GPG_SUBPROCESS_ERROR_MESSAGE() + '\n' + interface_copy.EXITING()
                    print(message)
                    self.logger.error(message)
                    exit(1)
                    
                self._print_note(note_path=note_path, decrypted_content=decrypted_content)
                print('') # blank line
                
        else:
            print(f"No notes found with keywords: {keywords}")

    def search_notes(self, search_queries):
        print(interface_copy.SOME_DELAY_FOR_DECRYPTION())
        is_found_any_matches = False
        notes_dir = self.get_notes_dir_from_config()
        
        note_paths = self._get_all_note_paths(notes_dir=notes_dir)
        queries_in_lower_case = [query.lower() for query in search_queries]
        for note_path in note_paths:
            try:
                decrypted_content = self.encrypted_note_helper.get_decrypted_content_in_memory(note_path=note_path)
            except GPGSubprocessException as e:
                self.logger.error(e)
                message = interface_copy.GPG_SUBPROCESS_ERROR_MESSAGE() + '\n' + interface_copy.EXITING()
                self.logger.error(message)
                print(message)
                exit(1)
            
            content_in_lower_case = decrypted_content.lower()
            if all(lowercase_query in content_in_lower_case for lowercase_query in queries_in_lower_case):
                print(f"\n{note_path}:\n{decrypted_content}")
                is_found_any_matches = True

        if not is_found_any_matches:
            print("no notes match search query")    
        


    def _try_to_make_path(self, selected_path):
        
        if os.path.exists(selected_path):
            # path exists
            return True
        else:
            directory = os.path.dirname(selected_path)
            user_expanded_directory = os.path.expanduser(directory)
            
            directory_exists = os.path.exists(user_expanded_directory)
            if directory_exists:
                try:
                    os.mkdir(selected_path)
                    return True
                except FileExistsError:
                    # logically this shouldn't happen
                    print(f"directory '{selected_path}' already exists")
                    return False
                except Exception as e:
                    self.logger.error(e)
                    print("encountered an error attempting to make this directory")
                    return False
            else:
                print(f"parent directory {directory} does not exist")
                return False
                
    
    def _check_gpg_verified(self):
        is_gpg_verified = self._get_gpg_verified()
        if not is_gpg_verified:
            is_gpg_available = CommandValidator.verify_command(command_string = GPG)
            if is_gpg_available:
                self._set_gpg_verified()
            else:
                raise CouldNotRunGPG()
        
    
    def _set_gpg_verified(self):
        self.config_module.set_setting_to_user_config(key=GPG_VERIFIED_KEY, value='yes')
    
    def _get_gpg_verified(self):
        return (self.config_module.get_setting_from_user_config(key=GPG_VERIFIED_KEY) =='yes')
    
    def initialize(self):
        selected_path = self.prompt_for_user_notes_path()

        self.config_module.set_global_to_user_config(key=INITIALIZED, value='yes')
        self.config_module.set_setting_to_user_config(key=NOTES_PATH_KEY, value=selected_path)
        self.config_module.set_setting_to_user_config(key=ASCII_ARMOR_CONFIG_KEY, value='yes')

        
        gpg_verified = CommandValidator.verify_command(command_string=GPG)
        if not gpg_verified:
            print(interface_copy.NEED_TO_INSTALL_GPG)
        else:
            self._set_gpg_verified()
            
    #
    # def _set_setting_in_user_config(self, key, value):
    #     if 'settings' not in self.user_config:
    #         self.user_config['settings'] = {}
    #     self.user_config['settings'][key]= value
    #     self._save_config()

    def _check_is_database_set_up(self):
        is_set_up = (self.config_module.get_setting_from_user_config('database_is_setup') == 'yes')
        return is_set_up
    
    def _set_database_is_set_up(self):
        self.config_module.set_setting_to_user_config('database_is_setup', 'yes')
        
        
    def setup_database(self):
        print(interface_copy.SETTING_UP_DATABASE_MESSAGE())
        self.logger.debug("setting up the database tables")
        self.database_service.setup_database()
        self._set_database_is_set_up()
        

    def _is_use_ascii_armor(self):
        return (self.config_module.get_setting_from_user_config(key=ASCII_ARMOR_CONFIG_KEY) == "yes")

    def _set_use_ascii_armor(self, isUseArmor):
        value = 'yes' if isUseArmor else 'no'
        self.config_module.set_setting_to_user_config(key=ASCII_ARMOR_CONFIG_KEY, value=value)
        self.logger.debug(f"set {ASCII_ARMOR_CONFIG_KEY}=yes")


    def check_gpg_key_email(self):
        if self.GPG_KEY_EMAIL is None:
            print("Error: GPG key not set.")
            print("Please set the GPG key. (Refer to help menu `-h`.)")
            exit(1)
            
    def get_gpg_key_email(self):
        if 'settings' in self.user_config and 'gpg_key_email' in self.user_config['settings']:
            self.GPG_KEY_EMAIL = self.user_config['settings']['gpg_key_email']
            return self.GPG_KEY_EMAIL
        else:
            return None
    
    def set_gpg_key_email(self, new_gpg_key_email):
        self.GPG_KEY_EMAIL = new_gpg_key_email
        key = "gpg_key_email"
        self.config_module.set_setting_to_user_config(key=key, value=new_gpg_key_email)
        print(f"GPG Key set to: {self.GPG_KEY_EMAIL}")


            
            
    def check_gpg_installed(self):
        is_can_run_gpg_version = CommandValidator.verify_command(command_string=GPG)
        message = interface_copy.GPG_VERIFIED() if is_can_run_gpg_version else interface_copy.GPG_NOT_RUN()
        print(message)
    
    def startup(self):
        self._load_setup_configuration()
        self._setup_user_configuration()

    def _configure_text_editor(self, editor):
        raise Exception('add some validation')
        self.config_module.set_setting_to_user_config('text_editor', editor)
        
        
    def _get_input_until_condition_satisfied(self, prompt, condition):
        response = None
        while response == None:
            user_input = input(prompt)
            if condition(user_input):
                return user_input
            else:
                continue
        


    def choose_text_editor_interactive(self):
        available_editors = self._get_available_text_editors()
        if len(available_editors) == 0:
            print("No supported text editors were installed.")
            supported_editors_message = interface_copy.SUPPORTED_TEXT_EDITORS.format(", ".join(SUPPORTED_TEXT_EDITORS))
            print(supported_editors_message)
            print("Please install a supported text editor and try again.")
        elif len(available_editors) > 1:
            print("Please choose a text editor:")
            for index, editor in enumerate(available_editors):
                print(f"{index} : {editor}")
            text_editor_index_choice = None
            while text_editor_index_choice == None:
                text_editor_choice = input("Enter the number of your choice here.> ")
                try:
                    input_as_number = int(text_editor_choice)
                except ValueError as e:
                    self.logger.error(e)
                    print("input wasn't an integer")
                    continue
                except TypeError as e:
                    self.logger.error(e)
                    print("input wasn't an integer")
                    continue
                if input_as_number >= 0 and input_as_number < len(available_editors):
                    text_editor_index_choice = input_as_number
                    selected_editor = available_editors[text_editor_index_choice]
                    self.logger.debug(f"user selected editor {text_editor_choice}->{input_as_number} : {selected_editor}")
                    print(f"selected {selected_editor}")
                    self._configure_text_editor(editor=available_editors[text_editor_index_choice])
                else:
                    print("input wasn't an index")
                    self.logger.debug("input wasn't an index")
                    continue
        else:
            #set only available editor
            pass
                    
                    

    def check_text_editor_is_configured(self):
        # Check if a text editor is configured, prompt to select one if not
        is_configured = self._is_text_editor_configured()
        if not is_configured:
            TEXT_EDITOR = input("No text editor configured. Please enter the path to your preferred terminal text editor (e.g. 'vim', 'nano')> ")
            self.config_module.set_setting_to_user_config('text_editor', TEXT_EDITOR)
            


def __get_sqnotes():
    injector = Injector([InjectionConfigurationModule()])
    
    sqnotes = injector.get(SQNotes)
    return sqnotes

def main():
    parser = argparse.ArgumentParser(
        description='SQNote: Secure note-taking command-line utility.',
        )
    
    
    parser.add_argument('--debug', 
                    action='store_true', 
                    help='Enable debugging mode with detailed log messages')
    
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-k', '--keywords', nargs='+', help='Keywords for keyword search')
    group.add_argument('-s', '--search', nargs='+', help='Search term for full text search.')
    if USE_DIRECT_NOTE_INSERTION:
        group.add_argument('-n', '--new', help='Text for new note.', type=str)
    
    subparsers = parser.add_subparsers(dest='command', help='Subcommands')

    
    subparsers.add_parser('new', help='Add a new note.')
    subparsers.add_parser('init', help='Initialize app.')
    
    subparsers.add_parser('text-editors', help='Show supported text editors available on your system.')
    
    if SET_TEXT_EDITOR_INTERACTIVE_FLAG:
        subparsers.add_parser('config-text-editor', help='Choose your text editor (interactive).')
    
    man_command = subparsers.add_parser('man', help='Show manual.')
    manual_subcommands = man_command.add_subparsers(dest='man_subcommand', help='Manual subcommands.')
    manual_subcommands.add_parser('encryption', help='Show manual page for encryption.')
    manual_subcommands.add_parser('main', help='Show main manual page.')
    
    
    
    search_subparser = subparsers.add_parser('search', help='Find notes by full text search. (Slow because requires full decryption.)')
    search_subparser.add_argument('-t', '--text', nargs='+', help='Search strings.')
    
    set_gpg_key_subparser = subparsers.add_parser('set-gpg-key', help='Set the GPG key.')
    set_gpg_key_subparser.add_argument('-i', '--id', help='GPG key email/identifier.', type=str)
    
    use_armor_subparser = subparsers.add_parser('use-ascii-armor', help='Configure use of ASCII armor for encryption')
    group = use_armor_subparser.add_mutually_exclusive_group(required=True)
    group.add_argument('-y',
        '--yes', 
        action='store_true', 
        help='Set to use ASCII armor for encryption'
    )
    group.add_argument('-n',
        '--no', 
        action='store_true', 
        help='Set not to use ASCII armor for encryption'
    )
    
    keyword_search_subparser = subparsers.add_parser('keywords', help='Find notes keyword. (Fast because searches plaintext database.)')
    keyword_search_subparser.add_argument('-k', '--keywords', nargs='+', help='Search notes by keywords')
    
    subparsers.add_parser('rescan', help='Rescan notes to populate database (useful for troubleshooting certain errors)')
    subparsers.add_parser('notes-list', help='Show a list of all notes (scans notes directory)')
    subparsers.add_parser('print-keywords', help='Print all keywords from database.')
    
    subparsers.add_parser('verify-gpg', help='Verify that SQNotes can run GPG for encryption/decryption')
    
    git_parser = subparsers.add_parser('git', help='Passthrough git commands.')
    git_parser.add_argument('git_args', nargs=argparse.REMAINDER, help='Arguments for git command')
    
    edit_parser = subparsers.add_parser('edit', help='Edit a note.')
    edit_parser.add_argument('-n', '--note', help='Note base filename.', type=str)
    
    args = parser.parse_args()
    
    sqnotes = __get_sqnotes()
    sqnotes.startup()


    if args.command == 'init':
        sqnotes.initialize()
    elif args.command == 'man':
        manual = Manual()
        if args.man_subcommand == 'encryption':
            manual.print_encryption_page()
        else:
            manual.print_main_page()
    else:
        initialized = sqnotes._check_initialized()
        if not initialized:
            print(interface_copy.SQNOTES_NOT_INITIALIZED_MESSAGE)
            return
        else:
            if args.command == 'new':
                sqnotes.new_note()
            elif args.new:
                sqnotes.directly_insert_note(text=args.new)
            elif args.search:
                sqnotes.search_notes(search_queries = args.search)
            elif args.keywords:
                sqnotes.search_keywords(keywords=args.keywords)
            elif args.command == 'notes-list':
                sqnotes.notes_list()
            elif args.command == 'verify-gpg':
                sqnotes.check_gpg_installed()
            elif args.command == 'config-text-editor':
                sqnotes.choose_text_editor_interactive()
            elif args.command == 'text-editors':
                sqnotes.check_available_text_editors()
            elif args.command == 'set-gpg-key':
                sqnotes.set_gpg_key_email(args.id)
            elif args.command == 'use-ascii-armor':
                if args.yes:
                    sqnotes._set_use_ascii_armor(isUseArmor=True)
                elif args.no:
                    sqnotes._set_use_ascii_armor(isUseArmor=False)
            elif args.command == 'search':
                sqnotes.search_notes(args.text)
            elif args.command == 'keywords':
                sqnotes.search_keywords(args.keywords)
            elif args.command == 'edit':
                sqnotes.edit_note(args.note)
            elif args.command == 'git':
                sqnotes.run_git_command(args.git_args)
            elif args.command == 'print-keywords':
                sqnotes.print_all_keywords()
            elif args.command == 'rescan':
                sqnotes.rescan_for_database()
                
            else:
                parser.print_help()

if __name__ == '__main__':
    main()