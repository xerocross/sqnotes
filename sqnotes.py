
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

project_root = os.path.dirname(os.path.abspath(__file__))
env_file_path = os.path.join(project_root, '.production.env')

if os.getenv('TESTING') == 'true':
    env_file_path = os.path.join(project_root, '.test.env')
    load_dotenv(env_file_path)
else:
    env_file_path = os.path.join(project_root, '.env.production')
    load_dotenv(env_file_path)


# # Configurable directory for storing notes and database location
# DEFAULT_NOTE_DIR = os.path.expanduser(os.getenv('DEFAULT_NOTES_PATH'))
# CONFIG_DIR = os.path.expanduser(os.getenv('DEFAULT_CONFIG_DIR_PATH'))
#
#
# DB_FILE = os.path.join(DEFAULT_NOTE_DIR, "sqnotes_index.db")
#
#
# CONFIG_FILE = os.path.join(CONFIG_DIR, "config.ini")
# DB_FILE = os.path.expanduser(os.getenv('DEFAULT_NOTES_PATH'))
#





#
# # Ensure the configuration directory exists
# if not os.path.exists(CONFIG_DIR):
#     print(f"creating new config directory {CONFIG_DIR}")
#     os.makedirs(CONFIG_DIR)
#
# # Load configuration
# config = configparser.ConfigParser()
# if os.path.exists(CONFIG_FILE):
#     config.read(CONFIG_FILE)
#




# # Initialize SQLite connection
# conn = sqlite3.connect(DB_FILE)
# cursor = conn.cursor()


    
#
#
#
#
# GPG_KEY_EMAIL = get_gpg_key_email()
#
# if not os.path.exists(DEFAULT_NOTE_DIR):
#     os.makedirs(DEFAULT_NOTE_DIR)


        







def extract_keywords(content):
    # Extract hashtags using regular expression
    return [match[1:] for match in re.findall(r'\B#\w+\b', content)]






class NotesDirNotConfiguredException(Exception):
    """Exception raised if the user notes directory is not configured."""
    pass




class SQNotes:
    
    def save_config(self):
        with open(self.CONFIG_FILE, 'w') as configfile:
            self.user_config.write(configfile)
    
    def load_setup_configuration(self):
        # Configurable directory for storing notes and database location
        self.DEFAULT_NOTE_DIR = os.path.expanduser(os.getenv('DEFAULT_NOTES_PATH'))
        self.CONFIG_DIR = os.path.expanduser(os.getenv('DEFAULT_CONFIG_DIR_PATH'))
        self.CONFIG_FILE = os.path.join(self.CONFIG_DIR, "config.ini")
        
    
    def create_initial_user_config(self, user_config):
        user_config['global']['initialized'] = 'no'
        user_config['global']['VERSION'] = VERSION
        
        with open(self.CONFIG_FILE, 'w') as configfile:
            user_config.write(configfile)
        self.user_config = user_config
    
    
    def run_git_command(self, args):
        subprocess.call(['git'] + args, cwd=self.NOTES_DIR)
    
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
    
    def check_initialized(self):
        if 'global' in self.user_config and 'initialized' in self.user_config['global']:
            return (self.user_config['global']['initialized'] == 'yes')
        else:
            return False
    
    
    def get_notes_dir_from_config(self):
        if 'settings' in self.user_config and 'notes_path' in self.user_config['settings']:
            self.NOTES_DIR = self.user_config['settings']['notes_path']
        else:
            raise NotesDirNotConfiguredException()
    
    def prompt_to_initialize(self):
        print("sqnotes not initialized; please run initialization")
    
    def search_keywords(self, keywords):
    
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
                    print(f"an error occurred.")
                    return False
            else:
                print(f"parent directory {directory} does not exist")
                return False
                
    
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
        
    
    def initialize(self):
        selected_path = self.prompt_for_user_notes_path()
        
        
        if 'global' not in self.user_config:
            self.user_config['global'] = {}
        self.user_config['global']['initialized'] = 'yes'
        
        if 'settings' not in self.user_config:
            self.user_config['settings'] = {}
        self.user_config['settings']['notes_path'] = selected_path
        
        self.save_config()
        
    def open_database(self):
        # Initialize SQLite connection
        self.conn = sqlite3.connect(self.DB_FILE)
        self.cursor = self.conn.cursor()
        

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
        

    def setup_database(self):
        # Create tables if not exists
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

    def add_note(self):
        self.check_gpg_key_email()
        # Create a temporary file for the new note
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_filename = temp_file.name
    
        # Open the text editor to edit the note
        subprocess.call([self.TEXT_EDITOR, temp_filename])
    
        # Read the content from the temporary file
        with open(temp_filename, 'r') as file:
            note_content = file.read().strip()
    
        # Add signature text
        signature = f" [{GPG_KEY_EMAIL}] [{datetime.now().strftime('%Y-%m-%d %H:%M')}]"
        note_content += signature
    
        # Delete the temporary file
        os.remove(temp_filename)
    
        datetime_string = datetime.now().strftime('%Y%m%d%H%M%S')
        note_filename_slug = f"{datetime_string}.txt.gpg"
        note_filename = os.path.join(self.NOTES_DIR, note_filename_slug)
        with tempfile.NamedTemporaryFile(delete=False) as temp_enc_file:
            temp_enc_filename = temp_enc_file.name
            temp_enc_file.write(note_content.encode('utf-8'))
    
        # Encrypt the note using the gpg_key_email's public key
        subprocess.call(['gpg', '--yes', '--batch', '--output', note_filename, '--encrypt', '--recipient', GPG_KEY_EMAIL, temp_enc_filename])
        os.remove(temp_enc_filename)
        print(f"Note added: {note_filename}")
    
        # Insert note into notes table
        self.cursor.execute('''
                INSERT INTO notes (filename)
                VALUES (?)
            ''', (note_filename_slug,))
        note_id = self.cursor.lastrowid
    
        # Extract hashtags from note content and insert into keywords table
        keywords = extract_keywords(note_content)
        keyword_ids = []
        for keyword in keywords:
            self.cursor.execute('''
                INSERT OR IGNORE INTO keywords (keyword)
                VALUES (?)
            ''', (keyword,))
            self.conn.commit()
            self.cursor.execute('SELECT id FROM keywords WHERE keyword = ?', (keyword,))
            keyword_id = self.cursor.fetchone()[0]
            keyword_ids.append(keyword_id)
    
        # Insert note and keyword associations into note_keywords table
        for keyword_id in keyword_ids:
            self.cursor.execute('''
                INSERT INTO note_keywords (note_id, keyword_id)
                VALUES (?, ?)
            ''', (note_id, keyword_id))
            self.conn.commit()


    def edit_note(self, filename):
        self.check_gpg_key_email()
        raise Exception("haven't programmed self.NOTES_DIR")
        note_path = os.path.join(self.NOTES_DIR, filename)
        if not os.path.exists(note_path):
            print(f"Note not found: {filename}")
            return
    
        # Decrypt the note to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_dec_file:
            temp_dec_filename = temp_dec_file.name
    
        subprocess.call(['gpg', '--yes', '--batch', '--output', temp_dec_filename, '--decrypt', note_path])
    
        # Open the note with the configured text editor
        subprocess.call([self.TEXT_EDITOR, temp_dec_filename])
    
        # Read the edited content from the temporary file
        with open(temp_dec_filename, 'r') as file:
            edited_content = file.read().strip()
    
        # Add signature text
        signature = f"[{GPG_KEY_EMAIL}] [{datetime.now().strftime('%Y-%m-%d %H:%M')}]"
        edited_content += '\n' + signature
    
        # Encrypt the edited note back to the original file
        with tempfile.NamedTemporaryFile(delete=False) as temp_enc_file:
            temp_enc_filename = temp_enc_file.name
            temp_enc_file.write(edited_content.encode('utf-8'))
    
        subprocess.call(['gpg', '--yes', '--batch', '--output', note_path, '--encrypt', '--recipient', GPG_KEY_EMAIL, temp_enc_filename])
        os.remove(temp_dec_filename)
        os.remove(temp_enc_filename)
    
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
        keywords = extract_keywords(edited_content)
        keyword_ids = []
        for keyword in keywords:
            self.cursor.execute('''
                INSERT OR IGNORE INTO keywords (keyword)
                VALUES (?)
            ''', (keyword,))
            self.conn.commit()
            self.cursor.execute('SELECT id FROM keywords WHERE keyword = ?', (keyword,))
            keyword_id = self.cursor.fetchone()[0]
            keyword_ids.append(keyword_id)
    
        self.cursor.execute('DELETE FROM note_keywords WHERE note_id = ?', (filename,))
        for keyword_id in keyword_ids:
            self.cursor.execute('''
                INSERT INTO note_keywords (note_id, keyword_id)
                VALUES (?, ?)
            ''', (note_id, keyword_id))
            self.conn.commit()
    
    
        print(f"Note edited: {filename}")
        
        
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
        global GPG_KEY_EMAIL
        GPG_KEY_EMAIL = new_gpg_key_email
        if 'settings' not in self.user_config:
            self.user_config['settings'] = {}
        self.user_config['settings']['gpg_key_email'] = new_gpg_key_email
        self.save_config()
        print(f"GPG Key Email set to: {GPG_KEY_EMAIL}")

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
