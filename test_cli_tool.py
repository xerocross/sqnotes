import unittest
from unittest.mock import patch
import io
import sys
import sqnotes
from sqnotes import SQNotes


class TestCLI(unittest.TestCase):

    @patch('sys.stdout', new_callable=io.StringIO)
    def run_cli(self, args, mock_stdout):
        with patch('sys.argv', args):
            sqnotes.main()
        return mock_stdout.getvalue()

    @patch.object(SQNotes, 'initialize')
    def test_init_called_first_executes_initialize(self, mock_initialize):
        self.run_cli(['sqnotes', 'init'])
        mock_initialize.assert_called_once()

    @patch.object(SQNotes, 'check_initialized', lambda x : False)
    def test_new_command_called_not_initialized_prints_not_initialized_message(self):
        output = self.run_cli(['sqnotes', 'new'])
        self.assertIn("not initialized", output, "output message did not contain 'not initialized'")


    def test_invalid_action_raises_exit(self):
        with self.assertRaises(SystemExit):
            self.run_cli(['sqnotes', 'unknown'])


class TestCLIInitializedCommandsReferredCorrectly(unittest.TestCase):

    @patch('sys.stdout', new_callable=io.StringIO)
    def run_cli(self, args, mock_stdout):
        with patch('sys.argv', args):
            sqnotes.main()
        return mock_stdout.getvalue()
    
    @patch.object(SQNotes, 'check_initialized', lambda x : True)
    @patch.object(SQNotes, 'add_note')
    def test_new_command_refers_to_add_note_method(self, mock_add_note):
        self.run_cli(['sqnotes', 'new'])
        mock_add_note.assert_called_once()
    
    @patch.object(SQNotes, 'check_initialized', lambda x : True)
    @patch.object(SQNotes, 'print_all_notes')
    def test_notes_command_refers_to_print_notes_method(self, mock_print_all_notes):
        self.run_cli(['sqnotes', 'notes-list'])
        mock_print_all_notes.assert_called_once()
        
    @patch.object(SQNotes, 'check_initialized', lambda x : True)
    @patch.object(SQNotes, 'run_git_command')
    def test_git_command_refers_to_git_method(self, mock_run_git_command):
        self.run_cli(['sqnotes', 'git'])
        mock_run_git_command.assert_called_once()
        
    @patch.object(SQNotes, 'check_initialized', lambda x : True)
    @patch.object(SQNotes, 'print_all_keywords')
    def test_keywords_command_refers_to_keywords_method(self, mock_print_all_keywords):
        self.run_cli(['sqnotes', 'print-keywords'])
        mock_print_all_keywords.assert_called_once()
    
    @patch.object(SQNotes, 'check_initialized', lambda x : True)
    @patch.object(SQNotes, 'rescan_for_database')
    def test_rescan_command_refers_to_rescan_method(self, mock_rescan_for_database):
        self.run_cli(['sqnotes', 'rescan'])
        mock_rescan_for_database.assert_called_once()
        

        
    @patch.object(SQNotes, 'check_initialized', lambda x : True)
    @patch.object(SQNotes, 'edit_note')
    def test_edit_n_command_refers_to_edit_note_method(self, mock_edit_note):
        self.run_cli(['sqnotes', 'edit', '-n', 'note_1.txt'])
        mock_edit_note.assert_called_once_with('note_1.txt')
        
    @patch.object(SQNotes, 'check_initialized', lambda x : True)
    @patch.object(SQNotes, 'edit_note')
    def test_edit_note_command_refers_to_edit_note_method(self, mock_edit_note):
        self.run_cli(['sqnotes', 'edit', '--note', 'note_1.txt'])
        mock_edit_note.assert_called_once_with('note_1.txt')

    @patch.object(SQNotes, 'check_initialized', lambda x : True)
    @patch.object(SQNotes, 'search_notes')
    def test_search_t_command_refers_to_edit_note_method(self, mock_search_notes):
        self.run_cli(['sqnotes', 'search', '-t', 'apple', 'pear'])
        mock_search_notes.assert_called_once_with(['apple', 'pear'])

    @patch.object(SQNotes, 'check_initialized', lambda x : True)
    @patch.object(SQNotes, 'search_notes')
    def test_search_text_command_refers_to_edit_note_method(self, mock_search_notes):
        self.run_cli(['sqnotes', 'search', '--text', 'apple', 'pear'])
        mock_search_notes.assert_called_once_with(['apple', 'pear'])


if __name__ == '__main__':
    unittest.main()