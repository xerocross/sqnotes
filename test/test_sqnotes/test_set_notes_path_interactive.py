

import pytest

from unittest.mock import patch

from sqnotes.path_input_helper import PathInputHelper
from sqnotes.sqnotes_module import SQNotes
from conftest import mock_printer_helper_print
from test.test_helper import get_all_mocked_print_output_to_string
from sqnotes import interface_copy


@pytest.fixture
def mock_get_path_interactive():
    with patch.object(PathInputHelper, 'get_path_interactive') as mock:
        yield mock

def describe_set_notes_path_interactive():
    
    def it_prints_message_setting_notes_path_message (
                                            mock_get_path_interactive,
                                            sqnotes_obj : SQNotes,
                                            mock_printer_helper_print
                                            ):
        sqnotes_obj.set_notes_path_interactive()
        output = get_all_mocked_print_output_to_string(mocked_print=mock_printer_helper_print)
        expected_message = interface_copy.SETTING_THE_NOTES_PATH()
        assert expected_message in output
        
    
    def it_calls_path_input_helper_to_get_path(
                                            mock_get_path_interactive,
                                            sqnotes_obj : SQNotes
                                            ):
        sqnotes_obj.set_notes_path_interactive()
        mock_get_path_interactive.assert_called_once()