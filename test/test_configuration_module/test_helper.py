
import pytest
import tempfile
from injector import Injector
from sqnotes.configuration_module import ConfigurationModule
import os
import shutil

def touch(file_path):
    with open(file_path, 'a'):
        pass

@pytest.fixture
def configuration_module(test_temporary_directory):
    injector = Injector()
    config_module : ConfigurationModule = injector.get(ConfigurationModule)
    config_module._set_config_dir(test_temporary_directory)
    yield config_module
    
@pytest.fixture
def test_temporary_directory():
    temp_dir = tempfile.mkdtemp()
    try:
        yield temp_dir
    finally:
        if os.path.isdir(temp_dir):
            shutil.rmtree(temp_dir)