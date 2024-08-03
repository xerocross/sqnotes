
import pytest
from sqnotes.sqnotes_module import SQNotes

def describe_sqnotes():
    
    
    def it_gets_default_notes_dir_from_sqnotes_config(
                                            sqnotes_obj : SQNotes,
                                            mock_config_data
                                                            ):
        config_default_notes_dir = '/path/to/default/dir'
        mock_config_data[sqnotes_obj.DEFAULT_NOTES_DIR_KEY] = config_default_notes_dir
        default_notes_dir = sqnotes_obj._get_default_notes_dir()
        assert default_notes_dir == config_default_notes_dir
        
    def it_gets_default_user_config_dir_from_sqnotes_config(
                                            sqnotes_obj : SQNotes,
                                            mock_config_data
                                                            ):
        config_default_config_dir = '/path/to/default/config/dir'
        mock_config_data[sqnotes_obj.USER_CONFIG_DIR_KEY] = config_default_config_dir
        default_config_dir = sqnotes_obj._get_user_config_dir()
        assert default_config_dir == config_default_config_dir
        