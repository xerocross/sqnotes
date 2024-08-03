
import pytest
import os
from unittest.mock import patch
from injector import Injector, Module, provider
from sqnotes.sqnotes_config_module import SQNotesConfig
import logging

logger = logging.getLogger("test_config")


current_dir = os.path.dirname(os.path.abspath(__file__))
test_root = os.path.abspath(os.path.join(current_dir, "../"))
test_resources_root = os.path.join(test_root, 'resources')
config_file = os.path.join(test_resources_root, 'test_config.yaml')


    


    
    
def describe_config():
    
    def it_gets_value_from_config_file(
                            mock_sqnotes_config_from_resource_file
                            ):
        test_key = 'initialized'
        expected_value = 'no'
        value = mock_sqnotes_config_from_resource_file.get(key = test_key)
        logger.debug("config data")
        logger.debug(mock_sqnotes_config_from_resource_file.data)
        assert value == expected_value
        
    def describe_value_is_no():
        def it_returns_false(mock_sqnotes_config_from_resource_file):
            expected_value = False
            value = mock_sqnotes_config_from_resource_file.get(key = 'key_with_no_value')
            assert value == expected_value
        
    