
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
import logging
import interface_copy
import sys


VERSION = '0.2'
DEBUGGING = '--debug' in sys.argv
ASCII_ARMOR_CONFIG_KEY = "armor"
GPG_VERIFIED_KEY = "gpg_verified"

class EnvironmentConfigurationNotFound(Exception):
    """Raise if the environment configuration file is not found."""

project_root = os.path.dirname(os.path.abspath(__file__))
env_file_path = os.path.join(project_root, '.production.env')
if os.getenv('TESTING') == 'true':
    env_file_path = os.path.join(project_root, '.test.env')
else:
    env_file_path = os.path.join(project_root, '.env.production')
if not os.path.exists(env_file_path):
    raise EnvironmentConfigurationNotFound()
else:
    load_dotenv(env_file_path)



def setup_logger():
    logger = logging.getLogger('SQNotes')
    logger.setLevel(logging.DEBUG)
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    if DEBUGGING:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)  # Log all levels to console
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    return logger


logger = setup_logger()


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
    
class GPGSubprocessException(Exception):
    """Raise when an exception or error occurs in calling gpg in a subprocess."""
    
class CouldNotRunGPG(Exception):
    """Raise when a command is called that requires GPG and GPG is not available."""

class FileInfo:
        
    def __init__(self, path, base_name):
        self.path = path
        self.base_name = base_name

class SQNotes:
    
    def _insert_keyword_into_database(self, keyword):
        self.cursor.execute('SELECT id FROM keywords WHERE keyword = ?', (keyword,))
        result = self.cursor.fetchone()
        if result is None:
            # this keyword does not exist in the database
            self.cursor.execute('''
                INSERT OR IGNORE INTO keywords (keyword)
                VALUES (?)
            ''', (keyword,))
            keyword_id = self.cursor.lastrowid
        else:
            keyword_id = result[0]
        return keyword_id

    def _get_input_from_text_editor(self):
        TEXT_EDITOR = self._get_configured_text_editor()
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_filename = temp_file.name
        try:
            response = subprocess.call([TEXT_EDITOR, temp_filename])
            if response != 0:
                raise TextEditorSubprocessException()
        except Exception as e:
            logger.error("an exception occurred while attempting the text editor subprocess")
            logger.error(e)
            raise TextEditorSubprocessException()
        
        with open(temp_filename, 'r') as file:
            note_content = file.read().strip()
        os.remove(temp_filename)
        return note_content
        

    def _write_encrypted_note(self, note_file_path, note_content):
        
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_enc_file:
            temp_enc_filename = temp_enc_file.name
            temp_enc_file.write(note_content.encode('utf-8'))
            
        subprocess_command = ['gpg', '--yes','--quiet', '--batch', '--output', note_file_path, '--encrypt', '--recipient', self.GPG_KEY_EMAIL, temp_enc_filename]
        if self._is_use_ascii_armor():
            subprocess_command.insert(1, '--armor')
            
        try:
            response = subprocess.call(subprocess_command)
            if os.path.exists(temp_enc_filename):
                os.remove(temp_enc_filename)
            if response != 0:
                raise GPGSubprocessException()
        except Exception as e:
            logger.error("encountered an error while calling gpg as a subprocess")
            logger.error(e)
            # make sure we remove the temp file
            if os.path.exists(temp_enc_filename):
                os.remove(temp_enc_filename)
            
            raise GPGSubprocessException()

        
    def _get_new_note_name(self):
        is_use_armor = self._is_use_ascii_armor()
        extension = 'txt' if is_use_armor else "txt.gpg"
        datetime_string = datetime.now().strftime('%Y%m%d%H%M%S')
        return f"{datetime_string}.{extension}"
         

    def new_note(self):
        self._check_gpg_verified()
        self.GPG_KEY_EMAIL = self.get_gpg_key_email()
        self.check_gpg_key_email()
        NOTES_DIR = self.get_notes_dir_from_config()
        self.check_text_editor_is_configured()
        
        
        try:
            self.open_database()
        except Exception as e:
            message = interface_copy.COULD_NOT_OPEN_DATABASE() + ' ' + interface_copy.EXITING()
            print(message)
            exit(1)

        try:        
            note_content = self._get_input_from_text_editor()
        except TextEditorSubprocessException:
            message = interface_copy.TEXT_EDITOR_SUBPROCESS_ERROR().format(self._get_configured_text_editor())
            logger.error(message)
            print(message)
            exit(1)
        
        base_filename = self._get_new_note_name()
        note_file_path = os.path.join(NOTES_DIR, base_filename)
        try:
            self._write_encrypted_note(note_file_path=note_file_path, note_content=note_content)
        except GPGSubprocessException as e:
            logger.error(e)
            message = interface_copy.GPG_SUBPROCESS_MESSAGE() + '\n' + interface_copy.EXITING()
            logger.error(message)
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
                logger.error(message)
                logger.error(e)
                print(message)
            else:
                message = interface_copy.UNKNOWN_ERROR() + '\n' + interface_copy.DATA_NOT_SAVED()
                logger.error(message)
                logger.error(e)
                print(interface_copy.UNKNOWN_ERROR() + '\n' + interface_copy.DATA_NOT_SAVED())

            

    def _extract_and_save_keywords(self, note_id, note_content):
        keywords = self._extract_keywords(note_content)
        keyword_ids = []
        for keyword in keywords:
            keyword_id = self._insert_keyword_into_database(keyword)
            keyword_ids.append(keyword_id)
    
        for keyword_id in keyword_ids:
            self.insert_note_keyword_into_database(note_id, keyword_id)
        
    
    def check_initialized(self):
        if 'global' in self.user_config and 'initialized' in self.user_config['global']:
            return (self.user_config['global']['initialized'] == 'yes')
        else:
            return False
    
    
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
    
    def create_initial_user_config(self, user_config):
        if 'global' not in self.user_config:
            self.user_config['global'] = {}
        user_config['global']['initialized'] = 'no'
        user_config['global']['VERSION'] = VERSION
        
        with open(self.CONFIG_FILE, 'w') as configfile:
            user_config.write(configfile)
        self.user_config = user_config
    
    def _delete_keywords_from_database_for_note(self, note_id):
        self.cursor.execute('DELETE FROM note_keywords WHERE note_id = ?', (note_id,))
    
    def _delete_temp_file(self, temp_file):
        if os.path.exists(temp_file):
                os.remove(temp_file)
    
    def _decrypt_note_into_temp_file(self, note_path):
        with tempfile.NamedTemporaryFile(delete=False) as temp_dec_file:
            temp_dec_filename = temp_dec_file.name
        try:
            decrypt_process = subprocess.run(['gpg', '--yes','--quiet', '--batch', '--output', temp_dec_filename, '--decrypt', note_path], check=True)
        except Exception as e:
            logger.error(e)
            
            self._delete_temp_file(temp_file=temp_dec_filename)
            
            raise GPGSubprocessException()
        
        if decrypt_process != 0:
            logger.error(f"decrypt process returned code {decrypt_process}")
            self._delete_temp_file(temp_file=temp_dec_filename)
            raise GPGSubprocessException()
        
        return temp_dec_filename
    
    def _get_edited_note_from_text_editor(self, temp_filename):
        TEXT_EDITOR = self._get_configured_text_editor()
        edit_process = subprocess.run([TEXT_EDITOR, temp_filename], check=True)
    
        # Ensure Vim exited properly before proceeding
        if edit_process.returncode != 0:
            raise Exception("Editing failed")
        with open(temp_filename, 'r') as file:
            edited_content = file.read().strip()
        return edited_content
    
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
            temp_dec_filename = self._decrypt_note_into_temp_file(note_path=note_path)
            edited_content = self._get_edited_note_from_text_editor(temp_filename=temp_dec_filename)
            print("edited_content:")
            print(edited_content)
            self._write_encrypted_note(note_file_path=note_path, note_content=edited_content)
        except GPGSubprocessException as e:
            logger.error(e)
            message = interface_copy.GPG_SUBPROCESS_MESSAGE() + '\n' + interface_copy.EXITING()
            print(message)
            logger.error(message)
            exit(1)
        finally:
            if os.path.exists(temp_dec_filename):
                os.remove(temp_dec_filename)
    
    
    
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
        logger.error("encountered a database exception")
        logger.error(e)
        print(interface_copy.DATABASE_EXCEPTION_MESSAGE())

    
    def _extract_keywords(self, content):
        # Extract hashtags using regular expression
        tags = [match[1:] for match in re.findall(r'\B#\w+\b', content)]
        unique_tags = set(tags)
        return list(unique_tags)
    
    
    def _get_decrypted_content(self, file_path):
        with tempfile.NamedTemporaryFile(delete=False) as temp_dec_file:
            temp_dec_filename = temp_dec_file.name
            
            subprocess.call(['gpg', '--yes', '--batch', '--quiet', '--output', temp_dec_filename, '--decrypt', file_path])
            
            with open(temp_dec_filename, 'r') as file:
                content = file.read()
            if os.path.exists(temp_dec_filename):
                os.remove(temp_dec_filename)
        return content
                
    
    def rescan_for_database(self):
        NOTES_DIR = self.get_notes_dir_from_config()
        self.open_database()
        files = self._get_notes(notes_dir = NOTES_DIR)
        files_info = [FileInfo(path = file, base_name = os.path.basename(file)) for file in files]
        
        for file_info in files_info:
            content = self._get_decrypted_content(file_path=file_info.path)
            try:
                note_id = self._get_note_id_from_database_or_none(filename = file_info.base_name)
                
                if note_id is None:
                    note_id = self._insert_new_note_into_database(note_filename_base=file_info.base_name)
                
                self._delete_keywords_from_database_for_note(note_id=note_id)
                self._extract_and_save_keywords(note_id=note_id, note_content=content)
                self._commit_transaction()
                    
            except Exception:
                raise DatabaseException()
        print("rescan complete")
    
    def get_db_file_path(self, notes_dir):

        if os.getenv('TESTING') == 'true':
            return os.getenv('DATABASE_URL')
        else:    
            return os.path.join(notes_dir, os.getenv('DEFAULT_DATABASE_NAME'))
        
    
    def get_notes_dir_from_config(self):
        if 'settings' in self.user_config and 'notes_path' in self.user_config['settings']:
            self.NOTES_DIR = self.user_config['settings']['notes_path']
            return self.NOTES_DIR
        else:
            raise NotesDirNotConfiguredException()
        
    def _get_configured_text_editor(self):
        text_editor = self.get_setting_from_user_config('text_editor')
        if text_editor is None:
            raise TextEditorNotConfiguredException()
        return text_editor
    
    def _is_text_editor_configured(self):
        text_editor = self.get_setting_from_user_config('text_editor')
        return text_editor is not None and text_editor != ''
    
    def get_setting_from_user_config(self, key):
        if 'settings' in self.user_config and key in self.user_config['settings']:
            return self.user_config['settings'][key]
        else:
            return None
        
    def _commit_transaction(self):
        self.conn.commit()
        
    def _insert_new_note_into_database(self, note_filename_base):
        self.cursor.execute('''
                INSERT INTO notes (filename)
                VALUES (?)
            ''', (note_filename_base,))
        note_id = self.cursor.lastrowid
        logger.debug(f"insert new note filename : {note_filename_base}, id : {note_id}")
        return note_id
        
    def insert_note_keyword_into_database(self, note_id, keyword_id):
        self.cursor.execute('''
                    INSERT INTO note_keywords (note_id, keyword_id)
                    VALUES (?, ?)
                ''', (note_id, keyword_id))
        

    # not top-level
    def _get_notes(self, notes_dir):
        extensions = ['txt.gpg', 'txt']
        all_notes = []
        for ex in extensions:
            pattern = os.path.join(notes_dir, f"*.{ex}")
            files = glob.glob(pattern)
            all_notes.extend(files)
        return all_notes
        
    def notes_list(self):
        logger.debug("printing notes list")
        notes_dir = self.get_notes_dir_from_config()
        files = self._get_notes(notes_dir=notes_dir)
        filenames = [os.path.basename(file) for file in files]
        for file in filenames:
            logger.debug(f"note found: {file}")
            print(file)
        
    
    def load_setup_configuration(self):
        # Configurable directory for storing notes and database location
        self.DEFAULT_NOTE_DIR = os.path.expanduser(os.getenv('DEFAULT_NOTES_PATH'))
        self.CONFIG_DIR = os.path.expanduser(os.getenv('DEFAULT_CONFIG_DIR_PATH'))
        self.CONFIG_FILE = os.path.join(self.CONFIG_DIR, "config.ini")
        
    def _get_database_cursor(self):
        return self.cursor
    
    def _get_database_connection(self):
        return self.conn
    
    def open_database(self):
        notes_dir = self.get_notes_dir_from_config()
        if notes_dir is None:
            raise NotesDirNotSelectedException()
        self.DB_PATH = self.get_db_file_path(notes_dir)
        logger.debug(f"opening database at {self.DB_PATH}")
        try:
            self.conn = sqlite3.connect(self.DB_PATH)
            self.cursor = self.conn.cursor()
        except Exception as e:
            logger.error(f"could not open database at {self.DB_PATH}")
            logger.error(e)
            raise e
        
        is_database_set_up = self._check_is_database_set_up()
        if not is_database_set_up:
            logger.debug("found database not set up")
            self.setup_database()
    
    def open_or_create_and_open_user_config_file(self):
        # Ensure the configuration directory exists
        
        if not os.path.exists(self.CONFIG_DIR):
            print(f"creating new user_config directory {self.CONFIG_DIR}")
            os.makedirs(self.CONFIG_DIR)
            
        user_config = configparser.ConfigParser()
        self.user_config = user_config
        if os.path.exists(self.CONFIG_FILE):
            user_config.read(self.CONFIG_FILE)
        else:
            self.create_initial_user_config(user_config=user_config)
    
    
    def prompt_for_user_notes_path(self):
        user_notes_path = None
        attempt_num = 0
        max_attempts = 2
        while user_notes_path is None:
            prompt = "Please enter a path for saving your notes \nin the format '[full_path_to_parent]/[note_directory]'. \nPress enter to use default '{}'.".format(self.DEFAULT_NOTE_DIR)
            user_notes_path = input(prompt + '>')
        
            if user_notes_path == '':
                selected_path = self.DEFAULT_NOTE_DIR
            else:
                selected_path = user_notes_path
                
            success = self.try_to_make_path(selected_path)
            if success is False:
                if attempt_num < max_attempts:
                    attempt_num+=1
                    print("Please try again.")
                else:
                    print("Failed multiple times; you can try running this command again.")
                    return None
            else:
                return selected_path
        
    
    def prompt_to_initialize(self):
        print("sqnotes not initialized; please run initialization")
        
        
    def run_git_command(self, args):
        subprocess.call(['git'] + args, cwd=self.NOTES_DIR)
    
    def save_config(self):
        with open(self.CONFIG_FILE, 'w') as configfile:
            self.user_config.write(configfile)
    
    
    def search_keywords(self, keywords):
        self.open_database()
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
        if results:
            for result in results:
                note_filename = os.path.join(self.NOTES_DIR, result[0])
                self.decrypt_and_print(note_filename)
        else:
            print(f"No notes found with keywords: {keywords}")

    def search_notes(self, search_queries):
        print(interface_copy.SOME_DELAY_FOR_DECRYPTION())
        
        # Search for the queries in all notes
        any_matches = False
        notes_dir = self.get_notes_dir_from_config()
        notes = self._get_notes(notes_dir=notes_dir)
        
        for filename in notes:
            was_match = self.decrypt_and_print(filename, search_queries)
            if was_match:
                any_matches = True
        if not any_matches:
            print("no notes match search query")    
        


    def try_to_make_path(self, selected_path):
        
        if os.path.exists(selected_path):
            # path exists
            return True
        else:
            directory = os.path.dirname(selected_path)
            directory_exists = os.path.exists(directory)
            if directory_exists:
                try:
                    os.mkdir(selected_path)
                    return True
                except FileExistsError:
                    # logically this shouldn't happen
                    print(f"directory '{selected_path}' already exists")
                    return False
                except Exception as e:
                    print(f"an error occurred: {e}")
                    return False
            else:
                print(f"parent directory {directory} does not exist")
                return False
                
    
    def _check_gpg_verified(self):
        is_gpg_verified = self._get_gpg_verified()
        if not is_gpg_verified:
            is_gpg_available = self._verify_gpg()
            if is_gpg_available:
                self._set_gpg_verified()
            else:
                raise CouldNotRunGPG()
        
    
    def _set_gpg_verified(self):
        self._set_setting_in_user_config(key=GPG_VERIFIED_KEY, value='yes')
    
    def _get_gpg_verified(self):
        return (self.get_setting_from_user_config(key=GPG_VERIFIED_KEY) =='yes')
    
    def initialize(self):
        selected_path = self.prompt_for_user_notes_path()
        
        
        if 'global' not in self.user_config:
            self.user_config['global'] = {}
        self.user_config['global']['initialized'] = 'yes'
        
        if 'settings' not in self.user_config:
            self.user_config['settings'] = {}
        self.user_config['settings']['notes_path'] = selected_path
        self.user_config['settings'][ASCII_ARMOR_CONFIG_KEY] = "yes"
        self.save_config()
        
        
        gpg_verified = self._verify_gpg()
        if not gpg_verified:
            print(interface_copy.NEED_TO_INSTALL_GPG)
        else:
            self._set_gpg_verified()
            

    def _set_setting_in_user_config(self, key, value):
        if 'settings' not in self.user_config:
            self.user_config['settings'] = {}
        self.user_config['settings'][key]= value
        self.save_config()

    def _check_is_database_set_up(self):
        is_set_up = (self.get_setting_from_user_config('database_is_setup') == 'yes')
        return is_set_up
    
    def _set_database_is_set_up(self):
        self._set_setting_in_user_config('database_is_setup', 'yes')
        
        
    def setup_database(self):
        print(interface_copy.SETTING_UP_DATABASE_MESSAGE())
        logger.debug("setting up the database tables")
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS note_keywords (
                note_id INTEGER,
                keyword_id INTEGER,
                FOREIGN KEY (note_id) REFERENCES notes(id),
                FOREIGN KEY (keyword_id) REFERENCES keywords(id),
                PRIMARY KEY (note_id, keyword_id)
            )
        ''')
        self._commit_transaction()

        self._set_database_is_set_up()
        
    

    
        
        
    def decrypt_and_print(self, filename, search_queries = None):
        with tempfile.NamedTemporaryFile(delete=False) as temp_dec_file:
            temp_dec_filename = temp_dec_file.name
            subprocess.call(['gpg', '--yes', '--batch', '--quiet', '--output', temp_dec_filename, '--decrypt', filename])
            with open(temp_dec_filename, 'r') as file:
                content = file.read()
                if search_queries is not None:
                    content_lower = content.lower()
                    lower_queries = [query.lower() for query in search_queries]
                    if all(query in content_lower for query in lower_queries):
                        print(f"\n{filename}:\n{content}")
                        return True
                    else:
                        return False
                else:
                    print(f"\n{filename}:\n{content}")
                    return True


    def _is_use_ascii_armor(self):
        return (self.get_setting_from_user_config(key=ASCII_ARMOR_CONFIG_KEY) == "yes")

    def _set_use_ascii_armor(self, isUseArmor):
        value = 'yes' if isUseArmor else 'no'
        self._set_setting_in_user_config(key=ASCII_ARMOR_CONFIG_KEY, value=value)
        logger.debug(f"set {ASCII_ARMOR_CONFIG_KEY}=yes")


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
        self._set_setting_in_user_config(key=key, value=new_gpg_key_email)
        print(f"GPG Key set to: {self.GPG_KEY_EMAIL}")

    
    def _verify_gpg(self):
        print(interface_copy.CALLING_GPG_VERSION())
        command = ['gpg', '--version', '--quiet']
        try:
            subprocess.call(command)
        except Exception as e:
            logger.error(e)
            return False
        return True
            
            
    def check_gpg_installed(self):
        is_can_run_gpg_version = self._verify_gpg()
        message = interface_copy.GPG_VERIFIED() if is_can_run_gpg_version else interface_copy.GPG_NOT_RUN()
        print(message)
    
    def startup(self):
        self.load_setup_configuration()
        self.open_or_create_and_open_user_config_file()

    def check_text_editor_is_configured(self):
        # Check if a text editor is configured, prompt to select one if not
        is_configured = self._is_text_editor_configured()
        if not is_configured:
            TEXT_EDITOR = input("No text editor configured. Please enter the path to your preferred terminal text editor (e.g. 'vim', 'nano')> ")
            self._set_setting_in_user_config('text_editor', TEXT_EDITOR)
            self.save_config()


def main():
    parser = argparse.ArgumentParser(
        description='SQNote: Secure note-taking command-line utility.',
        )
    
    
    parser.add_argument('--debug', 
                    action='store_true', 
                    help='Enable debugging mode with detailed log messages')
    
    
    
    subparsers = parser.add_subparsers(dest='command', help='Subcommands')

    
    subparsers.add_parser('new', help='Add a new note.')
    
    subparsers.add_parser('init', help='Initialize app.')
    
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

    sqnotes = SQNotes()
    sqnotes.startup()


    if args.command == 'init':
        sqnotes.initialize()
    else:
        initialized = sqnotes.check_initialized()
        if not initialized:
            print(interface_copy.SQNOTES_NOT_INITIALIZED_MESSAGE)
            return
        else:
            if args.command == 'new':
                sqnotes.new_note()
            elif args.command == 'notes-list':
                sqnotes.notes_list()
            elif args.command == 'verify-gpg':
                sqnotes.check_gpg_installed()
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
