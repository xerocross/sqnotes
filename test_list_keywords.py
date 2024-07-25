import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import os
import pytest
import tempfile
import sqlite3
from sqnotes import SQNotes
from dotenv import load_dotenv


@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'



def reload_dotenv():
    # Optionally clear existing environment variables
    for key in list(os.environ.keys()):
        if key.startswith('DATABASE_URL'):  # Adjust this as necessary for your specific environment variables
            del os.environ[key]

    # Reload the .env file
    load_dotenv(override=True)  # `override=True` ensures existing variables are overridden
    
            

class TestSQNotesListKeywordsCommand(unittest.TestCase):

    
    def setUp(self):
        self.sqnotes = SQNotes()
        
    @patch.object(SQNotes, 'open_database', lambda x: None)
    @patch.object(SQNotes, '_get_all_keywords_from_database')
    def test_keywords_command_prints_all_keywords(self,
                                                  mock_get_all_keywords):
        mock_get_all_keywords.return_value = ['apple', 'pear', 'banana']
        with patch('builtins.print') as mocked_print:
            self.sqnotes.print_all_keywords()
            calls = mocked_print.call_args_list
            printed_values = [call[0][0] for call in calls]
            self.assertEqual(printed_values, ['apple', 'pear', 'banana'])
            
class TestSQNotesGetAllKeywords(unittest.TestCase):
    
    @patch.object(SQNotes, 'check_is_database_set_up', lambda x : False)
    @patch.object(SQNotes, 'get_db_file_path', lambda x,y : ':memory:')
    @patch.object(SQNotes, 'get_notes_dir_from_config', lambda x : "")
    @patch.object(SQNotes,'set_database_is_set_up', lambda x : None)
    def setUp(self):
        reload_dotenv()
        # Set up a connection and a cursor
        
        self.sqnotes = SQNotes()
        self.sqnotes.open_database()
        self.connection = self.sqnotes._get_database_connection()
        self.cursor = self.sqnotes._get_database_cursor()
        
        
    def tearDown(self):
        # Roll back the transaction
        
        # Close the connection
        self.connection.close()
    
    def test_when_three_keywords_get_all_keywords_gets_all_keywords_from_database(self):
        self.connection.execute('BEGIN TRANSACTION;')
        new_keywords = ['apple', 'pear', 'banana']
        for k in new_keywords:
            self.cursor.execute('''
                    INSERT INTO keywords (keyword)
                    VALUES (?)
                ''', (k,))
        
        
        all_keywords = self.sqnotes._get_all_keywords_from_database()
        self.assertEqual(all_keywords, ['apple', 'pear', 'banana'])
    
        self.connection.execute('ROLLBACK;')
    
    def test_when_one_keyword_get_all_keywords_gets_all_keywords_from_database(self):
        self.connection.execute('BEGIN TRANSACTION;')
        new_keywords = ['orange',]
        for k in new_keywords:
            self.cursor.execute('''
                    INSERT INTO keywords (keyword)
                    VALUES (?)
                ''', (k,))
        
        
        all_keywords = self.sqnotes._get_all_keywords_from_database()
        self.assertEqual(all_keywords, ['orange'])
    
        self.connection.execute('ROLLBACK;')
    
    def test_when_no_keywords_get_all_keywords_gets_no_keywords_from_database(self):
        self.connection.execute('BEGIN TRANSACTION;')

        all_keywords = self.sqnotes._get_all_keywords_from_database()
        self.assertEqual(all_keywords, [])
    
        self.connection.execute('ROLLBACK;')
    
    
    
    
    
    
    
    
    
    