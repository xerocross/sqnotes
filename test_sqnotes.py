import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import os
import pytest
import tempfile
from sqnotes import SQNotes


@pytest.fixture(scope='session', autouse=True)
def set_test_environment():
    os.environ['TESTING'] = 'true'

class TestSQNotes(unittest.TestCase):

    
    def setUp(self):
        self.sqnotes = SQNotes()

    def test_testCase(self):
        assert True
        

    # @patch('subprocess.call')
    # def test_run_git_command_passes_through(self, mock_subprocess_call):
    #     self.sqnotes.run_git_command(['status'])
    #     default_notes_path = os.getenv('DEFAULT_NOTES_PATH')
    #     mock_subprocess_call.assert_called_once_with(['git', 'status'], cwd=os.path.expanduser(default_notes_path))

    # @patch('subprocess.call')
    # def test_add_note_creates_temp_file(self, mock_subprocess_call):
    #     with patch('tempfile.NamedTemporaryFile', mock_open()) as mock_temp_file:
    #         set_gpg_key_email("test@example.com")
    #         add_note()
    #         mock_temp_file.assert_called()
    #         mock_subprocess_call.assert_called()

    # @patch('subprocess.call')
    # def test_set_gpg_key_email(self, mock_subprocess_call):
    #     set_gpg_key_email("test@example.com")
    #     self.assertEqual(GPG_KEY_EMAIL, "test@example.com")
    #
    # def test_extract_keywords(self):
    #     content = "This is a test note with #keywords and #morekeywords."
    #     expected_keywords = ['keywords', 'morekeywords']
    #     self.assertEqual(extract_keywords(content), expected_keywords)
    #

    # Add more tests here as needed


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

    @patch.object(SQNotes, 'get_notes')
    def test_print_all_files(self, mock_get_notes):
        mock_get_notes.return_value = self.test_files
        with patch('builtins.print') as mocked_print:
            self.sqnotes.print_all_notes()
            calls = [
                call('test1.txt.gpg'),
                call('test2.txt.gpg'),
            ]
            mocked_print.assert_has_calls(calls, any_order=False)

    @patch.object(SQNotes, 'get_notes_dir_from_config')
    def test_get_notes_returns_list_of_notes_in_notes_dir(self, mock_get_notes_dir):
        test_dir_name = self.test_dir.name
        mock_get_notes_dir.return_value = test_dir_name
        expected_value = [test_dir_name + '/' + base for base in ['test1.txt.gpg', 'test2.txt.gpg']]
        self.assertEqual(self.sqnotes.get_notes(), expected_value)



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
        
        
        

class TestDatabaseInteractions(unittest.TestCase):
    pass
    # def create_database_tables_does_not_raise_error(self):
    #     pass


if __name__ == '__main__':
    unittest.main()
