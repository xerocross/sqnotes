
import pytest
import os
from sqnotes.sqnotes_config_module import SQNotesConfig
import logging

logger = logging.getLogger(__name__)

current_dir = os.path.dirname(os.path.abspath(__file__))
test_root = os.path.abspath(os.path.join(current_dir, "../"))
test_resources_root = os.path.join(test_root, 'resources')
config_file = os.path.join(test_resources_root, 'test_config.yaml')

def describe_config():

    def it_gets_value_from_config_file(
                                    mock_sqnotes_config_from_resource_file : SQNotesConfig
                                    ):
        test_key = 'USER_CONFIG_DIR'
        expected_value = '~/.sqnotes'
        value = mock_sqnotes_config_from_resource_file.get(key = test_key)
        assert value == expected_value

    def describe_value_is_no():
        def it_returns_false(mock_sqnotes_config_from_resource_file):
            expected_value = False
            value = mock_sqnotes_config_from_resource_file.get(key = 'key_with_no_value')
            assert value == expected_value
