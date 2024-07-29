import unittest
from unittest.mock import patch, mock_open, MagicMock, call
import os
import pytest
import shutil
import tempfile
from sqnotes.sqnotes_module import SQNotes, NotesDirNotConfiguredException
from sqnotes.configuration_module import ConfigurationModule
from sqnotes.database_service import DatabaseService
from injector import Injector
from test.test_helper import do_nothing


@pytest.fixture
def sqnotes_obj(test_temporary_directory):
    injector = Injector()
    sqnotes_instance : SQNotes = injector.get(SQNotes)
    sqnotes_instance.set_config_dir_override(config_dir_override = test_temporary_directory)
    yield sqnotes_instance
    
    
@pytest.fixture
def test_temporary_directory():
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)


def describe_sqnotes():
    
    
    def describe_database_setup():
    
        @patch.object(DatabaseService, 'setup_database')
        def it_calls_setup_on_database_service(
                                                mock_set_up_database,
                                                sqnotes_obj : SQNotes
                                                ):
            sqnotes_obj.setup_database()
            mock_set_up_database.assert_called_once()
    
    def describe_get_notes_dir_from_config():
        
        def it_calls_config_module_to_get_notes_dir(
                                                        sqnotes_obj : SQNotes
                                                    ):
            with patch.object(sqnotes_obj.config_module, 'get_setting_from_user_config') as mock_get_config_setting:
                sqnotes_obj.get_notes_dir_from_config()
                mock_get_config_setting.assert_called_once_with(key = 'notes_path')
            
        @patch.object(ConfigurationModule, 'get_setting_from_user_config')
        def it_returns_the_value_from_the_config_module(
                                                        mock_get_config_setting,
                                                        sqnotes_obj : SQNotes
                                                    ):
            test_notes_path = 'test/notes/path'
            mock_get_config_setting.return_value = test_notes_path
            return_value = sqnotes_obj.get_notes_dir_from_config()
            assert return_value == test_notes_path
        
        
        @patch.object(ConfigurationModule, 'get_setting_from_user_config')
        def it_raises_if_notes_path_not_configured(
                                                        mock_get_config_setting,
                                                        sqnotes_obj : SQNotes
                                                    ):
            mock_get_config_setting.return_value = None
            with pytest.raises(NotesDirNotConfiguredException):
                sqnotes_obj.get_notes_dir_from_config()
        


class TestListFiles(unittest.TestCase):

    def setUp(self):
        # Create a temporary directory
        self.test_dir = tempfile.TemporaryDirectory()
        # Add some test files
        self.test_files = ['test1.txt.gpg', 'test2.txt.gpg']
        for file in self.test_files:
            open(os.path.join(self.test_dir.name, file), 'a').close()
        injector = Injector()
        self.sqnotes = injector.get(SQNotes)

    def tearDown(self):
        self.test_dir.cleanup()

    @patch.object(SQNotes, 'get_notes_dir_from_config')
    @patch.object(SQNotes, '_get_all_note_paths')
    def test_print_all_files(self, 
                             mock_get_notes,
                             mock_get_notes_dir):
        mock_get_notes.return_value = self.test_files
        mock_get_notes_dir.return_value = "py"
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
        injector = Injector()
        self.sqnotes = injector.get(SQNotes)
    
    def test_returns_true_on_path_exists(self):
        selected_path = 'test_path'
        with patch('os.path.exists', return_value=True): 
            response = self.sqnotes._try_to_make_path(selected_path)
            self.assertTrue(response, "received false, which indicates failure")

    @patch('os.path.expanduser', lambda x: x)
    @patch('os.path.dirname')
    @patch('os.path.exists')
    def test_returns_true_if_makes_directory(self, mock_path_exists, mock_dirname):
        mock_path_exists.side_effect = [False, True]
        mock_dirname.return_value = 'parentDir'
        selected_path = 'test_path'
        with patch('os.mkdir', return_value=True): 
            response = self.sqnotes._try_to_make_path(selected_path)
            self.assertTrue(response, "received false, which indicates failure")
    
    @patch('os.path.expanduser', lambda x: x)
    @patch('os.mkdir')
    @patch('os.path.dirname')
    @patch('os.path.exists')
    def test_returns_false_on_mkdir_exception(self, mock_path_exists, mock_dirname, mock_mkdir):
        mock_path_exists.side_effect = [False, True]
        mock_dirname.return_value = 'parentDir'
        mock_mkdir.side_effect = Exception('unknown error')
        selected_path = 'test_path'
        response = self.sqnotes._try_to_make_path(selected_path)
        self.assertFalse(response, "received true, which indicates success, but should have failed")
        

if __name__ == '__main__':
    unittest.main()
