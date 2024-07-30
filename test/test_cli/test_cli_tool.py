
import pytest
import unittest
from unittest.mock import patch
import io
import sqnotes.sqnotes_module as sqnotes_module
from sqnotes.sqnotes_module import SQNotes
from sqnotes.manual import Manual

class TestCLI(unittest.TestCase):
    startup_patcher = None
    @classmethod
    def setUpClass(cls):
        cls.startup_patcher = patch.object(SQNotes, "startup", lambda x: None)
        cls.startup_patcher.start()
        
    @classmethod
    def tearDownClass(cls):
        cls.startup_patcher.stop()

    @patch('sys.stdout', new_callable=io.StringIO)
    def run_cli(self, args, mock_stdout):
        with patch('sys.argv', args):
            sqnotes_module.main()
        return mock_stdout.getvalue()

    @patch.object(SQNotes, 'initialize')
    def test_init_called_first_executes_initialize(self, mock_initialize):
        self.run_cli(['sqnotes', 'init'])
        mock_initialize.assert_called_once()

    @patch.object(SQNotes, '_get_is_initialized', lambda x : False)
    def test_new_command_called_not_initialized_prints_not_initialized_message(self):
        output = self.run_cli(['sqnotes', 'new'])
        self.assertIn("not initialized", output, "output message did not contain 'not initialized'")


    def test_invalid_action_raises_exit(self):
        with self.assertRaises(SystemExit):
            self.run_cli(['sqnotes', 'unknown'])


@patch('sys.stdout', new_callable=io.StringIO)
def run_cli(args, mock_stdout):
    with patch('sys.argv', args):
        sqnotes_module.main()
    return mock_stdout.getvalue()
    
    
def describe_sqnotes_cli():
    
    def describe_app_is_initialized():
    

        @pytest.mark.usefixtures("mock_get_is_initialized")
        @patch.object(SQNotes, 'new_note')
        def it_maps_new_command_to_new_note_method(mock_new_note):
            """
                The new command refers to the new_note method.
            """
            run_cli(['sqnotes', 'new'])
            mock_new_note.assert_called_once()
            
        @pytest.mark.usefixtures("mock_get_is_initialized")
        @patch.object(SQNotes, 'notes_list')
        def it_maps_notes_command_to_print_notes_method(mock_print_all_notes):
            """
                The notes-list command refers to the print notes method.
            """
            run_cli(['sqnotes', 'notes-list'])
            mock_print_all_notes.assert_called_once()
            
        @pytest.mark.usefixtures("mock_get_is_initialized")
        @patch.object(SQNotes, 'run_git_command')
        def it_maps_git_command_to_git_method(mock_run_git_command):
            run_cli(['sqnotes', 'git'])
            mock_run_git_command.assert_called_once()
            
        @pytest.mark.usefixtures("mock_get_is_initialized")
        @patch.object(SQNotes, 'print_all_keywords')
        def it_maps_print_keywords_command_to_keywords_method(mock_print_all_keywords):
            run_cli(['sqnotes', 'print-keywords'])
            mock_print_all_keywords.assert_called_once()
        
        @pytest.mark.usefixtures("mock_get_is_initialized")
        @patch.object(SQNotes, 'rescan_for_database')
        def it_maps_rescan_command_to_rescan_method(mock_rescan_for_database):
            run_cli(['sqnotes', 'rescan'])
            mock_rescan_for_database.assert_called_once()
            
    
            
        @pytest.mark.usefixtures("mock_get_is_initialized")
        @patch.object(SQNotes, 'edit_note')
        def test_edit_n_command_refers_to_edit_note_method(mock_edit_note):
            run_cli(['sqnotes', 'edit', '-n', 'note_1.txt'])
            mock_edit_note.assert_called_once_with('note_1.txt')
            
        
        @pytest.mark.usefixtures("mock_get_is_initialized")
        @patch.object(SQNotes, 'edit_note')
        def test_edit_note_command_refers_to_edit_note_method(mock_edit_note):
            run_cli(['sqnotes', 'edit', '--note', 'note_1.txt'])
            mock_edit_note.assert_called_once_with('note_1.txt')
    
        @pytest.mark.usefixtures("mock_get_is_initialized")
        @patch.object(SQNotes, 'search_notes')
        def test_search_t_command_refers_to_edit_note_method(mock_search_notes):
            run_cli(['sqnotes', 'search', '-t', 'apple', 'pear'])
            mock_search_notes.assert_called_once_with(['apple', 'pear'])
    
        @pytest.mark.usefixtures("mock_get_is_initialized")
        @patch.object(SQNotes, 'search_notes')
        def test_search_text_command_refers_to_edit_note_method(mock_search_notes):
            run_cli(['sqnotes', 'search', '--text', 'apple', 'pear'])
            mock_search_notes.assert_called_once_with(['apple', 'pear'])
            
            
        @pytest.mark.usefixtures("mock_get_is_initialized")
        @patch.object(SQNotes, 'set_gpg_key_email')
        def test_set_gpg_key_i_command_refers_to_set_gpg_key_method(mock_set_gpg_key_email):
            run_cli(['sqnotes', 'set-gpg-key', '-i', 'test@domain'])
            mock_set_gpg_key_email.assert_called_once_with('test@domain')
            
        @pytest.mark.usefixtures("mock_get_is_initialized")
        @patch.object(SQNotes, 'set_gpg_key_email')
        def test_set_gpg_key_ID_command_refers_to_set_gpg_key_method(mock_set_gpg_key_email):
            run_cli(['sqnotes', 'set-gpg-key', '--id', 'test@domain'])
            mock_set_gpg_key_email.assert_called_once_with('test@domain')
    
    
        @pytest.mark.usefixtures("mock_get_is_initialized")
        @patch.object(SQNotes, 'search_keywords')
        def test_main_command_with_k_option_calls_keyword_search(mock_search_keywords):
            run_cli(['sqnotes', '-k', 'apple', 'pear'])
            mock_search_keywords.assert_called_once_with(keywords=['apple', 'pear'])
            
        @pytest.mark.usefixtures("mock_get_is_initialized")
        @patch.object(Manual, 'print_main_page')
        def test_shows_manual_main_page_if_man_command_even_not_initialized(mock_print_main_man_page):
            run_cli(['sqnotes', 'man'])
            mock_print_main_man_page.assert_called_once()
    
        @pytest.mark.usefixtures("mock_get_is_initialized")
        @patch.object(Manual, 'print_encryption_page')
        def test_shows_manual_encryption_page_if_man_encryption_command(mock_print_man_encryption_page):
            run_cli(['sqnotes', 'man', 'encryption'])
            mock_print_man_encryption_page.assert_called_once()
            
        @pytest.mark.usefixtures("mock_get_is_initialized")
        @patch.object(SQNotes, 'directly_insert_note')
        def test_new_argument_with_text_refers_to_direct_insert(
                                                                mock_directly_insert):
            run_cli(['sqnotes', '-n', 'this is a test note'])
            mock_directly_insert.assert_called_once_with(text='this is a test note')
    
        @pytest.mark.usefixtures("mock_get_is_initialized")
        @patch.object(SQNotes, 'search_notes')
        def test_s_argument_refers_to_search_notes(
                                                                mock_search_notes):
            run_cli(['sqnotes', '-s', 'apple', 'pear'])
            mock_search_notes.assert_called_once_with(search_queries=['apple', 'pear'])



class TestCLIInitializedCommandsReferredCorrectly(unittest.TestCase):
    """once initialized, command line arguments are referred correctly"""
    
    startup_patcher = None
    
    @classmethod
    def setUpClass(cls):
        cls.startup_patcher = patch.object(SQNotes, "startup", lambda x: None)
        cls.startup_patcher.start()
        
    @classmethod
    def tearDownClass(cls):
        cls.startup_patcher.stop()

    @patch('sys.stdout', new_callable=io.StringIO)
    def run_cli(self, args, mock_stdout):
        with patch('sys.argv', args):
            sqnotes_module.main()
        return mock_stdout.getvalue()
    
    
    
    
    
        
    
    

if __name__ == '__main__':
    unittest.main()