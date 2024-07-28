import unittest
from unittest.mock import patch, mock_open, MagicMock, call, Mock
import os
import pytest
from sqnotes import SQNotes, GPGSubprocessException
from encrypted_note_helper import EncryptedNoteHelper
from test.test_helper import get_all_mocked_print_output
from injector import Injector


@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'
    
    
def get_all_notes(*args, **kwargs):
    return ['note1.txt']
        
class TestSQNotesSearchNotes(unittest.TestCase):

    def setUp(self):
        injector = Injector()
        self.sqnotes = injector.get(SQNotes)

    @patch.object(SQNotes, 'get_notes_dir_from_config', lambda self: '')
    @patch.object(SQNotes, '_get_all_note_paths', lambda self, notes_dir: ['note1.txt', 'note2.txt', 'note3.txt'])
    @patch.object(EncryptedNoteHelper,'get_decrypted_content_in_memory')
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
    @patch.object(EncryptedNoteHelper,'get_decrypted_content_in_memory')
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
    @patch.object(EncryptedNoteHelper,'get_decrypted_content_in_memory')
    @patch('builtins.print', lambda x: None)
    def test_exits_if_decrypt_function_raises_GPG_subprocess_exception(self,
                                                                       mock_get_decrypted_content):
        search_queries = ['apple', 'pear']
        mock_get_decrypted_content.side_effect = GPGSubprocessException()
        with self.assertRaises(SystemExit):
            self.sqnotes.search_notes(search_queries=search_queries)
        

    @patch.object(SQNotes, 'get_notes_dir_from_config', lambda self: '')
    @patch.object(SQNotes, '_get_all_note_paths', lambda self, notes_dir: ['note1.txt', 'note2.txt', 'note3.txt'])
    @patch.object(EncryptedNoteHelper,'get_decrypted_content_in_memory')
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
        
        
        
        
        
