
import pytest
from sqnotes.sqnotes_module import SQNotes

def describe_sqnotes():
    
    
    def it_gets_default_notes_dir_from_sqnotes_config(
                                            sqnotes_obj : SQNotes,
                                            mock_config_data
                                                            ):
        config_default_notes_dir = '/path/to/default/dir'
        mock_config_data['DEFAULT_NOTES_DIR'] = config_default_notes_dir
        default_notes_dir = sqnotes_obj._get_default_notes_dir()
        assert default_notes_dir == config_default_notes_dir