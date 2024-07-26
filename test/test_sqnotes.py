import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import os
import pytest
import tempfile
from sqnotes import SQNotes


@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'


class TestListFiles(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.TemporaryDirectory()
        # Add some test files
        self.test_files = ['test1.txt.gpg', 'test2.txt.gpg']
        for file in self.test_files:
            open(os.path.join(self.test_dir.name, file), 'a').close()
            
        self.sqnotes = SQNotes()

    def tearDown(self):
        self.test_dir.cleanup()

    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, '_get_all_note_paths')
    def test_print_all_files(self, 
                             mock_get_notes,
                             mock_get_notes_dir):
        mock_get_notes.return_value = self.test_files
        mock_get_notes_dir.return_value = "sqnotes"
        with patch('builtins.print') as mocked_print:
            self.sqnotes.notes_list()
            calls = [
                call('test1.txt.gpg'),
                call('test2.txt.gpg'),
            ]
            mocked_print.assert_has_calls(calls, any_order=False)


    def test_get_notes_returns_list_of_notes_in_notes_dir(self):
        test_dir_name = self.test_dir.name
        expected_value = [test_dir_name + '/' + base for base in ['test1.txt.gpg', 'test2.txt.gpg']]
        self.assertEqual(self.sqnotes._get_all_note_paths(notes_dir=test_dir_name), expected_value)



class TestTryToMakePath(unittest.TestCase):
    
    def setUp(self):
        self.sqnotes = SQNotes()
    
    def test_returns_true_on_path_exists(self):
        selected_path = 'test_path'
        with patch('os.path.exists', return_value=True): 
            response = self.sqnotes.try_to_make_path(selected_path)
            self.assertTrue(response, "received false, which indicates failure")

    @patch('os.path.dirname')
    @patch('os.path.exists')
    def test_returns_true_if_makes_directory(self, mock_path_exists, mock_dirname):
        mock_path_exists.side_effect = [False, True]
        mock_dirname.return_value = 'parentDir'
        selected_path = 'test_path'
        with patch('os.mkdir', return_value=True): 
            response = self.sqnotes.try_to_make_path(selected_path)
            self.assertTrue(response, "received false, which indicates failure")
        
    @patch('os.mkdir')
    @patch('os.path.dirname')
    @patch('os.path.exists')
    def test_returns_false_on_mkdir_exception(self, mock_path_exists, mock_dirname, mock_mkdir):
        mock_path_exists.side_effect = [False, True]
        mock_dirname.return_value = 'parentDir'
        mock_mkdir.side_effect = Exception('unknown error')
        selected_path = 'test_path'
        response = self.sqnotes.try_to_make_path(selected_path)
        self.assertFalse(response, "received true, which indicates success, but should have failed")
        

if __name__ == '__main__':
    unittest.main()
