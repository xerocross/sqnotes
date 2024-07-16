#!/usr/bin/env python3

import argparse
import os
import glob
import subprocess
import tempfile
from datetime import datetime
import sqlite3
import re
import configparser

# Configurable directory for storing notes and database location
NOTE_DIR = os.path.expanduser("~/sqnotes")
CONFIG_DIR = os.path.expanduser("~/.sqnotes")
DB_FILE = os.path.join(CONFIG_DIR, "sqnotes_index.db")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.ini")


# Ensure the configuration directory exists
if not os.path.exists(CONFIG_DIR):
    print(f"creating new config directory {CONFIG_DIR}")
    os.makedirs(CONFIG_DIR)

# Load configuration
config = configparser.ConfigParser()
if os.path.exists(CONFIG_FILE):
    config.read(CONFIG_FILE)



# Initialize SQLite connection
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create tables if not exists
cursor.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS keywords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS note_keywords (
        note_id INTEGER,
        keyword_id INTEGER,
        FOREIGN KEY (note_id) REFERENCES notes(id),
        FOREIGN KEY (keyword_id) REFERENCES keywords(id),
        PRIMARY KEY (note_id, keyword_id)
    )
''')

conn.commit()

def save_config():
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

def get_gpg_key_email():
    if 'settings' in config and 'gpg_key_email' in config['settings']:
        return config['settings']['gpg_key_email']
    else:
        return None

GPG_KEY_EMAIL = get_gpg_key_email()

if not os.path.exists(NOTE_DIR):
    os.makedirs(NOTE_DIR)

def check_gpg_key_email():
    if GPG_KEY_EMAIL is None:
        print("Error: GPG key not set.")
        print("Please set the GPG key using the following command:")
        print("  sqnotes --set-gpg-key your_email@example.com")
        exit(1)
        
def run_git_command(args):
    subprocess.call(['git'] + args, cwd=NOTE_DIR)

def set_gpg_key_email(new_gpg_key_email):
    global GPG_KEY_EMAIL
    GPG_KEY_EMAIL = new_gpg_key_email
    if 'settings' not in config:
        config['settings'] = {}
    config['settings']['gpg_key_email'] = new_gpg_key_email
    save_config()
    print(f"GPG Key Email set to: {GPG_KEY_EMAIL}")

def add_note():
    check_gpg_key_email()
    # Create a temporary file for the new note
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_filename = temp_file.name

    # Open the text editor to edit the note
    subprocess.call([TEXT_EDITOR, temp_filename])

    # Read the content from the temporary file
    with open(temp_filename, 'r') as file:
        note_content = file.read().strip()

    # Add signature text
    signature = f" [{GPG_KEY_EMAIL}] [{datetime.now().strftime('%Y-%m-%d %H:%M')}]"
    note_content += signature

    # Delete the temporary file
    os.remove(temp_filename)

    # Save the encrypted note content to a new note file
    note_id = len(glob.glob(f"{NOTE_DIR}/*.gpg")) + 1
    note_filename_slug = f"note_{note_id}.txt.gpg"
    note_filename = os.path.join(NOTE_DIR, note_filename_slug)
    with tempfile.NamedTemporaryFile(delete=False) as temp_enc_file:
        temp_enc_filename = temp_enc_file.name
        temp_enc_file.write(note_content.encode('utf-8'))

    # Encrypt the note using the gpg_key_email's public key
    subprocess.call(['gpg', '--yes', '--batch', '--output', note_filename, '--encrypt', '--recipient', GPG_KEY_EMAIL, temp_enc_filename])
    os.remove(temp_enc_filename)
    print(f"Note added: {note_filename}")

    # Extract hashtags from note content and insert into keywords table
    keywords = extract_keywords(note_content)
    keyword_ids = []
    for keyword in keywords:
        cursor.execute('''
            INSERT OR IGNORE INTO keywords (keyword)
            VALUES (?)
        ''', (keyword,))
        conn.commit()
        cursor.execute('SELECT id FROM keywords WHERE keyword = ?', (keyword,))
        keyword_id = cursor.fetchone()[0]
        keyword_ids.append(keyword_id)

    # Insert note and keyword associations into note_keywords table
    for keyword_id in keyword_ids:
        cursor.execute('''
            INSERT INTO note_keywords (note_id, keyword_id)
            VALUES (?, ?)
        ''', (note_id, keyword_id))
        conn.commit()

    # Insert note into notes table
    cursor.execute('''
        INSERT INTO notes (id, filename)
        VALUES (?, ?)
    ''', (note_id, note_filename_slug))
    conn.commit()


def extract_keywords(content):
    # Extract hashtags using regular expression
    return re.findall(r'\B#\w+\b', content)

# Function to search notes
def search_notes(search_queries):
    check_gpg_key_email()

    # Convert all search queries to lowercase
    search_queries_lower = [query.lower() for query in search_queries]

    # Search for the queries in all notes
    for filename in glob.glob(f"{NOTE_DIR}/*.gpg"):
        with tempfile.NamedTemporaryFile(delete=False) as temp_dec_file:
            temp_dec_filename = temp_dec_file.name

        # Decrypt the note
        subprocess.call(['gpg', '--yes', '--batch', '--quiet', '--output', temp_dec_filename, '--decrypt', filename])

        with open(temp_dec_filename, 'r') as file:
            content = file.read()
            content_lower = content.lower()  # Convert note content to lowercase

            # Check if all search queries are in the note content
            if all(query in content_lower for query in search_queries_lower):
                print(f"\n{filename}:\n{content}")

        os.remove(temp_dec_filename)

def decrypt_and_print(filename):
    # Decrypt and print note content
    with tempfile.NamedTemporaryFile(delete=False) as temp_dec_file:
        temp_dec_filename = temp_dec_file.name
        subprocess.call(['gpg', '--yes', '--batch', '--quiet', '--output', temp_dec_filename, '--decrypt', filename])
        with open(temp_dec_filename, 'r') as file:
            content = file.read()
            print(f"\n{filename}:\n{content}")


def edit_note(filename):
    check_gpg_key_email()
    note_path = os.path.join(NOTE_DIR, filename)
    if not os.path.exists(note_path):
        print(f"Note not found: {filename}")
        return

    # Decrypt the note to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_dec_file:
        temp_dec_filename = temp_dec_file.name

    subprocess.call(['gpg', '--yes', '--batch', '--output', temp_dec_filename, '--decrypt', note_path])

    # Open the note with the configured text editor
    subprocess.call([TEXT_EDITOR, temp_dec_filename])

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

    # Update keywords in the database
    keywords = extract_keywords(edited_content)
    keyword_ids = []
    for keyword in keywords:
        cursor.execute('''
            INSERT OR IGNORE INTO keywords (keyword)
            VALUES (?)
        ''', (keyword,))
        conn.commit()
        cursor.execute('SELECT id FROM keywords WHERE keyword = ?', (keyword,))
        keyword_id = cursor.fetchone()[0]
        keyword_ids.append(keyword_id)

    cursor.execute('DELETE FROM note_keywords WHERE note_id = ?', (filename,))
    for keyword_id in keyword_ids:
        cursor.execute('''
            INSERT INTO note_keywords (note_id, keyword_id)
            VALUES (?, ?)
        ''', (filename, keyword_id))
        conn.commit()

    print(f"Note edited: {filename}")

def main():
    global TEXT_EDITOR
    # Check if a text editor is configured, prompt to select one if not
    if 'settings' in config and 'text_editor' in config['settings']:
        TEXT_EDITOR = config['settings']['text_editor']
    else:
        TEXT_EDITOR = input("No text editor configured. Please enter the path to your preferred text editor: ")
        config['settings'] = {'text_editor': TEXT_EDITOR}
        save_config()

    parser = argparse.ArgumentParser(description='SQNote: Secure note-taking script')
    parser.add_argument('-n', '--new', help='Add a new note', action='store_true')
    parser.add_argument('-f', '--find', help='Find a note by filename')  # Single filename search
    parser.add_argument('-k', '--keywords', nargs='+', help='Search notes by keywords')
    parser.add_argument('-e', '--edit', help='Edit a note', type=str)
    parser.add_argument('--set-gpg-key', help='Set the GPG Key', type=str)
    parser.add_argument('--git', nargs=argparse.REMAINDER, help='Run a git command in the sqnotes directory')
    
    args = parser.parse_args()

    if args.set_gpg_key:
        set_gpg_key_email(args.set_gpg_key)
    elif args.new:
        add_note()
    elif args.git:
        run_git_command(args.git)
    elif args.find:
        search_notes(args.find)
    elif args.edit:
        edit_note(args.edit)
    elif args.keywords:
        keyword_query = ','.join(args.keywords)
        cursor.execute('''
            SELECT n.filename
            FROM notes n
            JOIN note_keywords nk ON n.id = nk.note_id
            JOIN keywords k ON nk.keyword_id = k.id
            WHERE k.keyword IN ({})
            GROUP BY n.filename
            HAVING COUNT(*) = {}
        '''.format(', '.join('?' for _ in args.keywords), len(args.keywords)), args.keywords)
        results = cursor.fetchall()
        if results:
            for result in results:
                note_filename = os.path.join(NOTE_DIR, result[0])
                decrypt_and_print(note_filename)
        else:
            print(f"No notes found with keywords: {args.keywords}")
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
