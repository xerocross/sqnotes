

import pytest
from unittest.mock import patch
from injector import Injector, Module, provider
from sqnotes.text_editor_helper import TextEditorHelper
from sqnotes.sqnotes_config_module import SQNotesConfig

def get_subprocess_commands(mock_subprocess):
    args, _ = mock_subprocess.call_args
    subprocess_command = args[0]
    return subprocess_command

@pytest.fixture
def text_editor_helper(sqnotes_config):
    
    class TestConfigModule(Module):
        
        @provider
        def provide_sqnotes_config(self) -> SQNotesConfig:
            return sqnotes_config
        
    injector = Injector([TestConfigModule()])
    text_editor_helper = injector.get(TextEditorHelper)
    yield text_editor_helper

def describe_text_editor_helper():
    pass


    def describe_get_text_from_editor():
        
        @patch("subprocess.call")
        def it_calls_subprocess(
                                        mock_subprocess_call,
                                        text_editor_helper
                                        ):
            text_editor_helper.get_input_from_text_editor()
            mock_subprocess_call.assert_called_once()
            
            
        @pytest.fixture
        def configured_text_editor():
            text_editor = 'vim'
            yield text_editor
            
        @pytest.fixture
        def text_editor_helper_vim(text_editor_helper, configured_text_editor):
            text_editor_helper.set_text_editor(text_editor = configured_text_editor)
            yield text_editor_helper
            
        
        
        @pytest.fixture
        def temp_file_for_input(tmp_path):
            temp_file = tmp_path / "temp_input_file"
            yield str(temp_file)
            
        @pytest.fixture
        def mock_get_temp_input_file(temp_file_for_input):
            pass
        
        def describe_text_editor_is_set_vim():
        
            @patch("subprocess.call")
            def it_passes_vim_command_to_subprocess(
                                                        mock_subprocess_call,
                                                        text_editor_helper_vim,
                                                        configured_text_editor
                                                    ):
                
                text_editor_helper_vim.get_input_from_text_editor()
                mock_subprocess_call.assert_called()
                subprocess_command = get_subprocess_commands(mock_subprocess_call)
                first_command = subprocess_command[0]
                assert first_command == configured_text_editor
    
            @patch("subprocess.call")
            def it_passes_temp_file_as_seccond_argument_to_subprocess(
                                                            mock_subprocess_call,
                                                            text_editor_helper_vim,
                ):
                text_editor_helper_vim.get_input_from_text_editor()
                subprocess_command = get_subprocess_commands(mock_subprocess_call)
                first_command = subprocess_command[0]
                
    
    def describe_set_text_editor():
        
        def it_sets_text_editor_to_selected_editor(
                text_editor_helper
            ):
    
            text_editor = 'vim'
            text_editor_helper.set_text_editor(text_editor=text_editor)
            assert text_editor_helper.get_text_editor() == text_editor
    
