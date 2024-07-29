

import sqlite3
from injector import inject

class NoteNotFoundInDatabaseException(Exception):
    """Raise when could not find a note reference in the database."""
    
class DatabaseService:
    @inject
    def __init__(self):
        self.connected = False
        
    def connect(self, db_file_path):
        self.db_file_path = db_file_path
        self.conn = sqlite3.connect(self.db_file_path)
        self.cursor = self.conn.cursor()
        
    def _get_connection(self):
        return self.conn
    
    def _get_cursor(self):
        return self.cursor
        
    def _get_all_keywords_from_database(self):
        self.cursor.execute('SELECT keyword FROM keywords')
        rows = self.cursor.fetchall()
        keywords = [row[0] for row in rows]
        return keywords
    
    def setup_database(self):
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
        self.commit_transaction()
        
        
    def insert_new_note_into_database(self, note_filename_base):
        self.cursor.execute('''
                INSERT INTO notes (filename)
                VALUES (?)
            ''', (note_filename_base,))
        note_id = self.cursor.lastrowid
        # self.logger.debug(f"insert new note filename : {note_filename_base}, id : {note_id}")
        return note_id
    
    def insert_note_keyword_into_database(self, note_id, keyword_id):
        query = '''
                    INSERT INTO note_keywords (note_id, keyword_id)
                    VALUES (?, ?)
                '''
        
        self.cursor.execute(query, (note_id, keyword_id))
        
    def insert_keyword_into_database(self, keyword):
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
        
    def get_note_id_from_database_or_none(self, filename):
        self.cursor.execute('SELECT id FROM notes WHERE filename = ?', (filename,))
        result = self.cursor.fetchone()
        if result:
            note_id = result[0]
            return note_id
        else:
            return None
        
        
    def get_note_id_from_database_or_raise(self, filename):
        self.cursor.execute('SELECT id FROM notes WHERE filename = ?', (filename,))
        result = self.cursor.fetchone()
        if result:
            note_id = result[0]
            return note_id
        else:
            raise NoteNotFoundInDatabaseException()
        
    def delete_keywords_from_database_for_note(self, note_id):
        self.cursor.execute('DELETE FROM note_keywords WHERE note_id = ?', (note_id,))
        
    def commit_transaction(self):
        self.conn.commit()
        
        
        
        
        
        
        
        
        