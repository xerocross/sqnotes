import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import os
import pytest
from sqnotes import SQNotes, GPGSubprocessException
from test_helper import get_all_mocked_print_output


@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    
    
def get_all_notes(*args, **kwargs):
    return ['note1.txt']
        
class TestSQNotesSearchNotes(unittest.TestCase):

    def setUp(self):
        self.sqnotes = SQNotes()
        
    @patch.object(SQNotes, 'get_notes_dir_from_config', lambda self: '')
    @patch.object(SQNotes, '_get_all_note_paths', lambda self, notes_dir: ['note1.txt', 'note2.txt', 'note3.txt'])
    @patch.object(SQNotes,'_get_decrypted_content')
    @patch('builtins.print')
    def test_prints_notes_that_match_one_query(self, 
                                           mock_print, 
                                           mock_get_decrypted_content):
        search_queries = ['apple']
        mock_get_decrypted_content.side_effect = ['a note with apple in it',
                                                  'a second note with apple in it',
                                                  'a note without the search term']
        self.sqnotes.search_notes(search_queries=search_queries)
        mock_print.assert_called()
        output = get_all_mocked_print_output(mocked_print=mock_print)
        self.assertIn('a note with apple', output)
        self.assertIn('a second note with apple', output)
        self.assertNotIn('a note without the search term', output)
        
        
    @patch.object(SQNotes, 'get_notes_dir_from_config', lambda self: '')
    @patch.object(SQNotes, '_get_all_note_paths', lambda self, notes_dir: ['note1.txt', 'note2.txt', 'note3.txt'])
    @patch.object(SQNotes,'_get_decrypted_content')
    @patch('builtins.print')
    def test_prints_notes_that_match_two_queries(self, 
                                           mock_print, 
                                           mock_get_decrypted_content):
        search_queries = ['apple', 'pear']
        mock_get_decrypted_content.side_effect = ['a note with apple in it',
                                                  'a second note with apple and pear in it',
                                                  'a note without the search term']
        self.sqnotes.search_notes(search_queries=search_queries)
        mock_print.assert_called()
        output = get_all_mocked_print_output(mocked_print=mock_print)
        self.assertNotIn('a note with apple', output)
        self.assertIn('a second note with apple', output)
        self.assertNotIn('a note without the search term', output)
        
        
    @patch.object(SQNotes, 'get_notes_dir_from_config', lambda self: '')
    @patch.object(SQNotes, '_get_all_note_paths', lambda self, notes_dir: ['note1.txt', 'note2.txt', 'note3.txt'])
    @patch.object(SQNotes,'_get_decrypted_content')
    @patch('builtins.print', lambda x: None)
    def test_exits_if_decrypt_function_raises_GPG_subprocess_exception(self,
                                                                       mock_get_decrypted_content):
        search_queries = ['apple', 'pear']
        mock_get_decrypted_content.side_effect = GPGSubprocessException()
        with self.assertRaises(SystemExit):
            self.sqnotes.search_notes(search_queries=search_queries)
        

    @patch.object(SQNotes, 'get_notes_dir_from_config', lambda self: '')
    @patch.object(SQNotes, '_get_all_note_paths', lambda self, notes_dir: ['note1.txt', 'note2.txt', 'note3.txt'])
    @patch.object(SQNotes,'_get_decrypted_content')
    @patch('builtins.print')
    def test_prints_error_message_if_decrypt_function_raises_GPG_subprocess_exception(self,
                                                                                      mock_print,
                                                                                      mock_get_decrypted_content):
        search_queries = ['apple', 'pear']
        mock_get_decrypted_content.side_effect = GPGSubprocessException()
        with self.assertRaises(SystemExit):
            self.sqnotes.search_notes(search_queries=search_queries)
        output = get_all_mocked_print_output(mocked_print=mock_print)
        self.assertIn('error while attempting to call GPG', output)
        self.assertIn('Exiting', output)
        
        
    @patch.object(SQNotes, '_decrypt_note_into_temp_file')
    def test_get_decrypted_raises_if_decrypt_into_file_raises_gpg_subprocess_exception(self,
                                                                                       mock_decrypt_note_into_temp):
        test_note_path = '/path/to/note1.txt'
        mock_decrypt_note_into_temp.side_effect = GPGSubprocessException()
        with self.assertRaises(GPGSubprocessException):
            self.sqnotes._get_decrypted_content(note_path=test_note_path)
       
       
    @patch.object(SQNotes, '_delete_temp_file')
    @patch.object(SQNotes, '_decrypt_note_into_temp_file')
    def test_get_decrypted_deletes_temp_file_after_reading_content(self,
                                                                            mock_decrypt_note_into_temp,
                                                                            mock_delete_temp_file):
        test_note_path = '/path/to/note1.txt'
        test_temp_file = "temp_file.txt"
        mock_decrypt_note_into_temp.return_value = test_temp_file
        
        mock_open_function = mock_open(read_data='Mock note content')
        with patch('builtins.open', mock_open_function):
            self.sqnotes._get_decrypted_content(note_path=test_note_path)
            mock_delete_temp_file.assert_called_once_with(temp_file=test_temp_file)
        
        
        
    @patch.object(SQNotes, '_delete_temp_file')
    @patch('builtins.open')
    @patch.object(SQNotes, '_decrypt_note_into_temp_file')
    def test_get_decrypted_deletes_temp_file_even_if_open_raises_exception(self,
                                                                            mock_decrypt_note_into_temp,
                                                                            local_mock_open,
                                                                            mock_delete_temp_file):
        test_note_path = '/path/to/note1.txt'
        test_temp_file = "temp_file.txt"
        mock_decrypt_note_into_temp.return_value = test_temp_file
        local_mock_open.side_effect = Exception()
        
        with self.assertRaises(Exception):
            self.sqnotes._get_decrypted_content(note_path=test_note_path)
            mock_delete_temp_file.assert_called_once_with(temp_file=test_temp_file)
        
        
        
        
    
        
        
        
        
