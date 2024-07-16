#!/usr/bin/env python3

import argparse
import os
import glob
import subprocess
import tempfile
import configparser

# Configurable directory for storing notes
NOTE_DIR = os.path.expanduser("~/sqnotes")
CONFIG_FILE = os.path.expanduser("~/.sqnotes_config")

# Load configuration
config = configparser.ConfigParser()
if os.path.exists(CONFIG_FILE):
    config.read(CONFIG_FILE)

# Function to save configuration
def save_config():
    with open(CONFIG_FILE, 'w') as configfile:
        config.write(configfile)

# Set default recipient if not present in config
def get_recipient():
    if 'settings' in config and 'recipient' in config['settings']:
        return config['settings']['recipient']
    else:
        return None

RECIPIENT = get_recipient()

if not os.path.exists(NOTE_DIR):
    os.makedirs(NOTE_DIR)

def check_recipient():
    if RECIPIENT is None:
        print("Error: GPG recipient not set.")
        print("Please set the GPG recipient using the following command:")
        print("  ./script.py --set-recipient your_email@example.com")
        exit(1)

def set_recipient(new_recipient):
    global RECIPIENT
    RECIPIENT = new_recipient
    if 'settings' not in config:
        config['settings'] = {}
    config['settings']['recipient'] = new_recipient
    save_config()
    print(f"Recipient set to: {RECIPIENT}")

def add_note():
    check_recipient()
    # Create a temporary file for the new note
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_filename = temp_file.name

    # Open Vim to edit the note
    subprocess.call(['vim', temp_filename])

    # Read the content from the temporary file
    with open(temp_filename, 'r') as file:
        note_content = file.read()

    # Delete the temporary file
    os.remove(temp_filename)

    # Save the encrypted note content to a new note file
    note_id = len(glob.glob(f"{NOTE_DIR}/*.gpg")) + 1
    note_filename = os.path.join(NOTE_DIR, f"note_{note_id}.txt.gpg")
    with tempfile.NamedTemporaryFile(delete=False) as temp_enc_file:
        temp_enc_filename = temp_enc_file.name
        temp_enc_file.write(note_content.encode('utf-8'))

    # Encrypt the note using the recipient's public key
    subprocess.call(['gpg', '--output', note_filename, '--encrypt', '--recipient', RECIPIENT, temp_enc_filename])
    os.remove(temp_enc_filename)
    print(f"Note added: {note_filename}")

def search_notes(search_queries):
    check_recipient()
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

def edit_note(filename):
    check_recipient()
    note_path = os.path.join(NOTE_DIR, filename)
    if not os.path.exists(note_path):
        print(f"Note not found: {filename}")
        return

    # Decrypt the note to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_dec_file:
        temp_dec_filename = temp_dec_file.name

    subprocess.call(['gpg', '--output', temp_dec_filename, '--decrypt', note_path])

    # Open the note with vim editor
    subprocess.call(['vim', temp_dec_filename])

    # Encrypt the edited note back to the original file
    subprocess.call(['gpg', '--output', note_path, '--encrypt', '--recipient', RECIPIENT, temp_dec_filename])
    os.remove(temp_dec_filename)

def run_git_command(args):
    subprocess.call(['git'] + args, cwd=NOTE_DIR)

def main():
    parser = argparse.ArgumentParser(description='SQNote: Secure note-taking script')
    parser.add_argument('-n', '--new', help='Add a new note', action='store_true')
    parser.add_argument('-f', '--find', nargs='+', help='Find a note')  # Allow multiple search queries
    parser.add_argument('-e', '--edit', help='Edit a note', type=str)
    parser.add_argument('--git', nargs=argparse.REMAINDER, help='Run a git command in the sqnotes directory')
    parser.add_argument('--set-recipient', help='Set the GPG recipient', type=str)

    args = parser.parse_args()

    if args.set_recipient:
        set_recipient(args.set_recipient)
    elif args.new:
        add_note()
    elif args.find:
        search_notes(args.find)
    elif args.edit:
        edit_note(args.edit)
    elif args.git:
        run_git_command(args.git)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

