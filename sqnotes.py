
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



VERSION = 2
DEBUGGING = True

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


class NotesDirNotConfiguredException(Exception):
    """Exception raised if the user notes directory is not configured."""
    pass

class DatabaseTableSetupException(Exception):
    """Exception raised during database table setup."""
    pass

class NotesDirNotSelectedException(Exception):
    """Exception raised if user notes directory not specified."""

class NoteNotFoundException(Exception):
    """Exception raised if attempt to open a note that is not found."""
    
class TextEditorNotConfiguredException(Exception):
    """Raise if attempted to use text editor but not configured."""
    
class DatabaseException(Exception):
    """Raise if an error occurs while interacting with the database."""



class SQNotes:
    
    def insert_keyword_into_database(self, keyword):
        self.cursor.execute('SELECT id FROM keywords WHERE keyword = ?', (keyword,))
        result = self.cursor.fetchone()
        if result is None:
            # this keyword does not exist in the database
            self.cursor.execute('''
                INSERT OR IGNORE INTO keywords (keyword)
                VALUES (?)
            ''', (keyword,))
            self.conn.commit()
            keyword_id = self.cursor.lastrowid
        else:
            keyword_id = result[0]
        return keyword_id

    def add_note(self):
        self.GPG_KEY_EMAIL = self.get_gpg_key_email()
        self.check_gpg_key_email()
        self.NOTES_DIR = self.get_notes_dir_from_config()
        self.open_database()
        self.TEXT_EDITOR = self.get_configured_text_editor()
        
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_filename = temp_file.name
    
        # Open the text editor to edit the note
        subprocess.call([self.TEXT_EDITOR, temp_filename])
    
        # Read the content from the temporary file
        with open(temp_filename, 'r') as file:
            note_content = file.read().strip()
    
        # Delete the temporary file
        os.remove(temp_filename)
    
        datetime_string = datetime.now().strftime('%Y%m%d%H%M%S')
        note_filename_slug = f"{datetime_string}.txt.gpg"
        note_filename = os.path.join(self.NOTES_DIR, note_filename_slug)
        with tempfile.NamedTemporaryFile(delete=False) as temp_enc_file:
            temp_enc_filename = temp_enc_file.name
            temp_enc_file.write(note_content.encode('utf-8'))
    
        # Encrypt the note using the gpg_key_email's public key
        subprocess.call(['gpg', '--yes', '--batch', '--output', note_filename, '--encrypt', '--recipient', self.GPG_KEY_EMAIL, temp_enc_filename])
        os.remove(temp_enc_filename)
        print(f"Note added: {note_filename}")
    
        note_id = self.insert_new_note_into_database(note_filename_base=note_filename_slug)
        keywords = self.extract_keywords(note_content)
        keyword_ids = []
        for keyword in keywords:
            keyword_id = self.insert_keyword_into_database(keyword)
            keyword_ids.append(keyword_id)
    
        for keyword_id in keyword_ids:
            self.insert_note_keyword_into_database(note_id, keyword_id)

    
    def check_initialized(self):
        if 'global' in self.user_config and 'initialized' in self.user_config['global']:
            return (self.user_config['global']['initialized'] == 'yes')
        else:
            return False
    
    
    def create_initial_user_config(self, user_config):
        if 'global' not in self.user_config:
            self.user_config['global'] = {}
        user_config['global']['initialized'] = 'no'
        user_config['global']['VERSION'] = VERSION
        
        with open(self.CONFIG_FILE, 'w') as configfile:
            user_config.write(configfile)
        self.user_config = user_config
    
    def delete_keywords_from_database_for_note(self, note_id):
        self.cursor.execute('DELETE FROM note_keywords WHERE note_id = ?', (note_id,))
        self.conn.commit()
    
    
    def edit_note(self, filename):
        self.GPG_KEY_EMAIL = self.get_gpg_key_email()
        self.check_gpg_key_email()
        self.NOTES_DIR = self.get_notes_dir_from_config()
        self.TEXT_EDITOR = self.get_configured_text_editor()
        self.open_database()
        
        note_path = os.path.join(self.NOTES_DIR, filename)
        if not os.path.exists(note_path):
            raise NoteNotFoundException()
    
        # Decrypt the note to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_dec_file:
            temp_dec_filename = temp_dec_file.name
    
        try:
            decrypt_process = subprocess.run(['gpg', '--yes','--quiet', '--batch', '--output', temp_dec_filename, '--decrypt', note_path], check=True)
    
            if decrypt_process.returncode != 0:
                raise Exception("Decryption failed")
    
            # Open the note with the configured text editor
    
            edit_process = subprocess.run([self.TEXT_EDITOR, temp_dec_filename], check=True)
    
            # Ensure Vim exited properly before proceeding
            if edit_process.returncode != 0:
                raise Exception("Editing failed")
    
            # Read the edited content from the temporary file
            with open(temp_dec_filename, 'r') as file:
                edited_content = file.read().strip()
    
            # Encrypt the edited note back to the original file
            with tempfile.NamedTemporaryFile(delete=False) as temp_enc_file:
                temp_enc_filename = temp_enc_file.name
                temp_enc_file.write(edited_content.encode('utf-8'))

            subprocess.call(['gpg', '--yes', '--batch','--quiet', '--output', note_path, '--encrypt', '--recipient', self.GPG_KEY_EMAIL, temp_enc_filename])
            
        finally:
            # Ensure temporary files are deleted
            if os.path.exists(temp_dec_filename):
                os.remove(temp_dec_filename)
            if os.path.exists(temp_enc_filename):
                os.remove(temp_enc_filename)
    
    
    
        try:
            self.cursor.execute('SELECT id FROM notes WHERE filename = ?', (filename,))
            result = self.cursor.fetchone()
            if result:
                note_id = result[0]
            else:
                self.cursor.execute('''
                    INSERT INTO notes (filename)
                    VALUES (?)
                ''', (filename,))
                note_id = self.cursor.lastrowid
        
            # Update keywords in the database
            keywords = self.extract_keywords(edited_content)
            keyword_ids = []
            for keyword in keywords:
                keyword_id = self.insert_keyword_into_database(keyword)
                keyword_ids.append(keyword_id)
        
            self.delete_keywords_from_database_for_note(note_id)
            
            for keyword_id in keyword_ids:
                self.insert_note_keyword_into_database(note_id, keyword_id)
                
        except Exception:
            raise DatabaseException()
            
        print(f"Note edited: {filename}")
    
    
    def extract_keywords(self, content):
        # Extract hashtags using regular expression
        tags = [match[1:] for match in re.findall(r'\B#\w+\b', content)]
        unique_tags = set(tags)
        return list(unique_tags)
    
    
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
        
    def get_configured_text_editor(self):
        text_editor = self.get_setting_from_user_config('text_editor')
        if text_editor is None:
            raise TextEditorNotConfiguredException()
        return text_editor
    
    def get_setting_from_user_config(self, key):
        if 'settings' in self.user_config and key in self.user_config['settings']:
            return self.user_config['settings'][key]
        else:
            return None
        
        
    def insert_new_note_into_database(self, note_filename_base):
        self.cursor.execute('''
                INSERT INTO notes (filename)
                VALUES (?)
            ''', (note_filename_base,))
        self.conn.commit()
        note_id = self.cursor.lastrowid
        return note_id
        
    def insert_note_keyword_into_database(self, note_id, keyword_id):
        self.cursor.execute('''
                    INSERT INTO note_keywords (note_id, keyword_id)
                    VALUES (?, ?)
                ''', (note_id, keyword_id))
        self.conn.commit()
        
    def list_notes(self):
        self.NOTES_DIR = self.get_notes_dir_from_config()
        extension = 'txt.gpg'
        pattern = os.path.join(self.NOTES_DIR, f"*.{extension}")
        files = glob.glob(pattern)
        filenames = [os.path.basename(file) for file in files]
        for file in filenames:
            print(file)
        
    
    def load_setup_configuration(self):
        # Configurable directory for storing notes and database location
        self.DEFAULT_NOTE_DIR = os.path.expanduser(os.getenv('DEFAULT_NOTES_PATH'))
        self.CONFIG_DIR = os.path.expanduser(os.getenv('DEFAULT_CONFIG_DIR_PATH'))
        self.CONFIG_FILE = os.path.join(self.CONFIG_DIR, "config.ini")
        
        
    
    def open_database(self):
        notes_dir = self.get_notes_dir_from_config()
        if notes_dir is None:
            raise NotesDirNotSelectedException()
        self.DB_PATH = self.get_db_file_path(notes_dir)
        self.conn = sqlite3.connect(self.DB_PATH)
        self.cursor = self.conn.cursor()
        
        is_database_set_up = self.check_is_database_set_up()
        if not is_database_set_up:
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
        print("there may be some delay here as this requires decrypting all your notes")
        self.GPG_KEY_EMAIL = self.get_gpg_key_email()
        self.check_gpg_key_email()
        
        # Search for the queries in all notes
        any_matches = False
        notes_dir = self.NOTES_DIR
        for filename in glob.glob(f"{notes_dir}/*.gpg"):
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
                
    
    
    
    
    def initialize(self):
        selected_path = self.prompt_for_user_notes_path()
        
        
        if 'global' not in self.user_config:
            self.user_config['global'] = {}
        self.user_config['global']['initialized'] = 'yes'
        
        if 'settings' not in self.user_config:
            self.user_config['settings'] = {}
        self.user_config['settings']['notes_path'] = selected_path
        
        self.save_config()
        
    
        


    

    def set_setting_in_user_config(self, key, value):
        if 'settings' not in self.user_config:
            self.user_config['settings'] = {}
        self.user_config['settings'][key]= value
        self.save_config()

    def check_is_database_set_up(self):
        is_set_up = (self.get_setting_from_user_config('database_is_setup') == 'yes')
        return is_set_up
    
    def set_database_is_set_up(self):
        self.set_setting_in_user_config('database_is_setup', 'yes')
        
    
    
        
        
    def setup_database(self):
        try:
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
            self.conn.commit()
        except Exception as e:
            raise DatabaseTableSetupException()
        self.set_database_is_set_up()
        
    

    
        
        
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


    def check_gpg_key_email(self):
        if self.GPG_KEY_EMAIL is None:
            print("Error: GPG key not set.")
            print("Please set the GPG key using the following command:")
            print("  sqnotes --set-gpg-key your_email@example.com")
            exit(1)
            
    def get_gpg_key_email(self):
        if 'settings' in self.user_config and 'gpg_key_email' in self.user_config['settings']:
            self.GPG_KEY_EMAIL = self.user_config['settings']['gpg_key_email']
            return self.GPG_KEY_EMAIL
        else:
            return None
    
    def set_gpg_key_email(self, new_gpg_key_email):
        self.GPG_KEY_EMAIL = new_gpg_key_email
        if 'settings' not in self.user_config:
            self.user_config['settings'] = {}
        self.user_config['settings']['gpg_key_email'] = new_gpg_key_email
        self.save_config()
        print(f"GPG Key Email set to: {self.GPG_KEY_EMAIL}")

    def set_user_notes_configuration(self, selected_path):
        pass
        
    
    def startup(self):
        self.load_setup_configuration()
        self.open_or_create_and_open_user_config_file()
        self.get_notes_dir_from_config()
        
    def set_text_editor_config(self):
        # Check if a text editor is configured, prompt to select one if not
        if 'settings' in self.user_config and 'text_editor' in self.user_config['settings']:
            TEXT_EDITOR = self.user_config['settings']['text_editor']
        else:
            TEXT_EDITOR = input("No text editor configured. Please enter the path to your preferred text editor.")
            self.user_config['settings'] = {'text_editor': TEXT_EDITOR}
            self.save_config()


def main():
    parser = argparse.ArgumentParser(description='SQNote: Secure note-taking script')
    parser.add_argument('-n', '--new', help='Add a new note', action='store_true')
    parser.add_argument('-f', '--find', nargs='+', help='Find substrings in notes (slow: decrypts everything)')  # Allow multiple search queries
    parser.add_argument('-k', '--keywords', nargs='+', help='Search notes by keywords')
    parser.add_argument('-e', '--edit', help='Edit a note', type=str)
    parser.add_argument('--set-gpg-key', help='Set the GPG Key', type=str)
    parser.add_argument('--git', nargs=argparse.REMAINDER, help='Run a git command in the sqnotes directory')
    
    subparsers = parser.add_subparsers(dest='command', help='Subcommands')
    parser_add = subparsers.add_parser('new', help='Add a new note.')
    paerser_init = subparsers.add_parser('init', help='Initialize app.')
    subparsers.add_parser('notes', help='Show a list of all notes.')
    git_parser = subparsers.add_parser('git', help='Passthrough git commands.')
    git_parser.add_argument('git_args', nargs=argparse.REMAINDER, help='Arguments for git command')
    
    args = parser.parse_args()

    sqnotes = SQNotes()
    sqnotes.startup()


    if args.command == 'init':
        sqnotes.initialize()
    else:
        initialized = sqnotes.check_initialized()
        if not initialized:
            print("SQNotes is not initialized; please initialize now. (Run with -h to see the help menu.)")
            return
        else:
            if args.command == 'new':
                sqnotes.add_note()
            elif args.command == 'notes':
                sqnotes.list_notes()
            elif args.command == 'git':
                sqnotes.run_git_command(args.git_args)
            elif args.set_gpg_key:
                sqnotes.set_gpg_key_email(args.set_gpg_key)
            elif args.new:
                sqnotes.add_note()
            elif args.git:
                sqnotes.run_git_command(args.git)
            elif args.find:
                sqnotes.search_notes(args.find)
            elif args.edit:
                sqnotes.edit_note(args.edit)
            elif args.keywords:
                sqnotes.search_keywords(args.keywords)
            else:
                parser.print_help()

if __name__ == '__main__':
    main()
