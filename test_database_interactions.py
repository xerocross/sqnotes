import unittest
from unittest.mock import patch, mock_open, MagicMock, call, Mock
import os
import pytest
from sqnotes import SQNotes, NoteNotFoundException
import tempfile
import sqnotes

@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    
class TestSQNotesDatabaseSetup(unittest.TestCase):

    def setUp(self):
        self.sqnotes_obj = SQNotes()
    
    
    def test_for_test_database_in_memory(self):
        db_path = self.sqnotes_obj.get_db_file_path()
        self.assertEqual(db_path, ':memory:')
    
    @patch.object(SQNotes, 'set_database_is_set_up')
    @patch.object(SQNotes, 'check_is_database_set_up')
    def test_sets_up_database_without_error(self,
                                            mock_check_database_set_up,
                                            mock_set_database_is_set_up
                                            ):
        mock_check_database_set_up.return_value = False
        
        try:
            self.sqnotes_obj.open_database()
        except Exception as e:
            pytest.fail(f"Unexpected exception raised: {e}")
            
            
    
                
            
class TestSQNotesDatabaseInsertsNewDatabase(unittest.TestCase):
            
    def setUp(self):
        self.sqnotes_obj = SQNotes()
        self.patcher = patch.object(self.sqnotes_obj, 'check_is_database_set_up', return_value=False)
        self.mocked_check_is_database_set_up = self.patcher.start()
        
        self.set_db_setup_patcher = patch.object(self.sqnotes_obj, 'set_database_is_set_up', return_value=True)
        self.set_db_setup_patcher.start()
        
        # Optional debug print to verify mocking
        print(f"Mocked check_is_database_set_up: {self.mocked_check_is_database_set_up.return_value}")

        # Initialize the database or perform setup steps
        self.sqnotes_obj.open_database()
            
            
        
    def test_insert_new_note_into_database_inserts_note(self):
        test_filename = "my_filename"
        self.sqnotes_obj._insert_new_note_into_database(note_filename_base=test_filename)
        cursor = self.sqnotes_obj._get_cursor()
        cursor.execute('SELECT id FROM notes WHERE filename = ?', (test_filename,))
        result = cursor.fetchone()
        self.assertIsNotNone(result)
            
            
            
    def tearDown(self):
        # Stop patching
        self.patcher.stop()
        self.set_db_setup_patcher.stop()
        self.sqnotes_obj._get_db_connection().rollback()
    
    