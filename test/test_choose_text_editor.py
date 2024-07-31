
import pytest

from unittest.mock import patch
from injector import Injector
from sqnotes.choose_text_editor import ChooseTextEditor,\
    MaxInputAttemptsException
from sqnotes import interface_copy
from sqnotes.sqnotes_module import SQNotes, TEXT_EDITOR_KEY
from test.test_helper import get_all_mocked_print_output, just_return,\
    get_all_mocked_print_output_to_string
from sqnotes.configuration_module import ConfigurationModule


@pytest.fixture
def mock_get_available_editors():
    with patch.object(ChooseTextEditor, 'get_available_editors') as mock:
        mock.return_value = ['vim', 'nano']
        yield mock

@pytest.fixture
def mock_input():
    with patch('builtins.input') as mock:
        mock.side_effect = ['apple']
        yield mock

def describe_choose_text_editor():
    
    
    def describe_no_available_editors():
        
        supported_editors = ['vim', 'nano', 'vi']
        @pytest.fixture
        def choose_text_editor():
            injector = Injector()
            
            choose_text_editor:ChooseTextEditor = injector.get(ChooseTextEditor)
            choose_text_editor.set_supported_editors(supported_editors=supported_editors)
            choose_text_editor.set_available_editors(available_editors=[])
            yield choose_text_editor
        
        @pytest.mark.usefixtures("mock_input")
        def it_prints_no_editors_available_message(
                                    choose_text_editor : ChooseTextEditor,
                                    mock_printer_helper_print
                                ):
            choose_text_editor.choose_text_editor_interactive()
            message = interface_copy.NO_SUPPORTED_TEXT_EDITORS_AVAILABLE()
            output = get_all_mocked_print_output(mocked_print=mock_printer_helper_print)
            assert message in output
    
        @pytest.mark.usefixtures("mock_input")
        def it_prints_list_of_supported_editors(
                                    choose_text_editor : ChooseTextEditor,
                                    mock_printer_helper_print
                                ):
            choose_text_editor.choose_text_editor_interactive()
            message = interface_copy.SUPPORTED_TEXT_EDITORS().format(", ".join(supported_editors))
            output = get_all_mocked_print_output(mocked_print=mock_printer_helper_print)
            assert message in output
            
        @pytest.mark.usefixtures("mock_input")
        def it_prints_message_to_install_editor_and_try_again (
                                    choose_text_editor : ChooseTextEditor,
                                    mock_printer_helper_print
                                ):
            choose_text_editor.choose_text_editor_interactive()
            message = interface_copy.PLEASE_INSTALL_TEXT_EDITOR_MESSAGE()
            output = get_all_mocked_print_output(mocked_print=mock_printer_helper_print)
            assert message in output
    
    
    def describe_there_are_multiple_available_editors():
    
        @pytest.fixture
        def mock_input():
            with patch('builtins.input') as mock:
                mock.side_effect = ['vim']
                yield mock
    
        @pytest.fixture
        def choose_text_editor():
            injector = Injector()
            choose_text_editor : ChooseTextEditor = injector.get(ChooseTextEditor)
            choose_text_editor.set_supported_editors(supported_editors=['vim', 'nano', 'vi'])
            choose_text_editor.set_available_editors(available_editors=['vim', 'nano'])
            yield choose_text_editor
    
        @pytest.mark.usefixtures("mock_get_available_editors",
                                 "mock_input")
        def it_prints_request_to_choose_editor(
                                                choose_text_editor : ChooseTextEditor,
                                                mock_print
                                            ):
            
            mock_input.return_value = 'vim'
            choose_text_editor.choose_text_editor_interactive()
            message = interface_copy.PLEASE_CHOOSE_EDITOR()
            output = get_all_mocked_print_output(mocked_print=mock_print)
            assert message in output
            
        
        @pytest.mark.usefixtures("mock_get_available_editors",
                                 "mock_input")
        def it_prints_available_editors(
                                                choose_text_editor : ChooseTextEditor,
                                                mock_print
                                            ):
            choose_text_editor.choose_text_editor_interactive()
            output = get_all_mocked_print_output(mocked_print=mock_print)
            assert 'vim' in output
            assert 'nano' in output
            
        
        @pytest.mark.usefixtures("mock_get_available_editors",
                                 "mock_input")
        def it_prompts_to_choose_one (
                                                choose_text_editor : ChooseTextEditor,
                                                mock_print
                                            ):
            choose_text_editor.choose_text_editor_interactive()
            expected_message = interface_copy.SELECT_ONE_OF_FOLLOWING()
            output = get_all_mocked_print_output(mocked_print=mock_print)
            assert expected_message in output
            
        def describe_on_valid_first_input_from_user():
            
            
            @pytest.mark.usefixtures("mock_get_available_editors",
                                     "mock_input",
                                     "mock_print")
            def it_returns_user_selection (
                                                    choose_text_editor : ChooseTextEditor
                                                ):
                selection = choose_text_editor.choose_text_editor_interactive()
                assert selection == 'vim'
            
            
            
        def describe_on_empty_first_input():
            
            
            @pytest.fixture
            def mock_input():
                with patch('builtins.input') as mock:
                    mock.side_effect = ['', 'vim']
                    yield mock
                    
            @pytest.mark.usefixtures("mock_get_available_editors",
                                         "mock_input")
            def it_prompts_again (
                                        choose_text_editor : ChooseTextEditor,
                                        mock_print
                                        ):
                choose_text_editor.choose_text_editor_interactive()
                output = get_all_mocked_print_output_to_string(mocked_print= mock_print)
                expected_prompt = interface_copy.SELECT_ONE_OF_FOLLOWING()
                num_prompt_occurrences =  output.count(expected_prompt)
                assert num_prompt_occurrences == 2
            
        def describe_on_invalid_first_input_from_user():
            
            def describe_second_input_is_valid():
            
                @pytest.fixture
                def mock_input():
                    with patch('builtins.input') as mock:
                        mock.side_effect = ['apple', 'vim']
                        yield mock
                    
                
            
                @pytest.mark.usefixtures("mock_get_available_editors",
                                         "mock_input")
                def it_prompts_a_second_time (
                                                        choose_text_editor : ChooseTextEditor,
                                                        mock_print
                                                    ):
                    choose_text_editor.choose_text_editor_interactive()
                    output = get_all_mocked_print_output_to_string(mocked_print= mock_print)
                    expected_prompt = interface_copy.SELECT_ONE_OF_FOLLOWING()
                    num_prompt_occurrences =  output.count(expected_prompt)
                    assert num_prompt_occurrences == 2
                
                
                @pytest.mark.usefixtures("mock_get_available_editors",
                                         "mock_input")
                def it_returns_valid_second_input (
                                                        choose_text_editor : ChooseTextEditor
                                                    ):
                    selection = choose_text_editor.choose_text_editor_interactive()
                    assert selection == 'vim'
                
                
            def describe_invalid_second_input():
                
                def describe_third_input_is_valid():
                    
                    valid_input = 'nano'
                    
                    @pytest.fixture
                    def mock_input():
                        with patch('builtins.input') as mock:
                            mock.side_effect = ['apple', 'pear', valid_input]
                            yield mock
                    
                    @pytest.mark.usefixtures("mock_get_available_editors",
                                             "mock_input")
                    def it_prompts_a_third_time (
                                                            choose_text_editor : ChooseTextEditor,
                                                            mock_print
                                                        ):
                        choose_text_editor.choose_text_editor_interactive()
                        output = get_all_mocked_print_output_to_string(mocked_print= mock_print)
                        expected_prompt = interface_copy.SELECT_ONE_OF_FOLLOWING()
                        num_prompt_occurrences =  output.count(expected_prompt)
                        assert num_prompt_occurrences == 3
                    
                    
                    @pytest.mark.usefixtures("mock_get_available_editors",
                                             "mock_input")
                    def it_returns_valid_third_input (
                                                            choose_text_editor : ChooseTextEditor
                                                        ):
                        selection = choose_text_editor.choose_text_editor_interactive()
                        assert selection == valid_input
                    
                
                def describe_invalid_third_attempt():
                    
                    @pytest.fixture
                    def mock_input():
                        with patch('builtins.input') as mock:
                            mock.side_effect = ['apple', 'pear', 'soup']
                            yield mock
                    
                    
                    @pytest.mark.usefixtures("mock_get_available_editors",
                                             "mock_input")
                    def it_raises_max_input_attempts_exception(
                                                    choose_text_editor : ChooseTextEditor
                                                    ):
                        with pytest.raises(MaxInputAttemptsException):
                            choose_text_editor.choose_text_editor_interactive()
                        
                    
                    
def describe_set_configured_text_editor():
    
    def describe_input_editor_is_supported():
    
        @patch.object(SQNotes, '_get_supported_text_editors', just_return(['vim', 'nano']))
        @patch.object(ConfigurationModule, 'set_setting_to_user_config')
        def it_sets_text_editor_in_configuration_module(
                                                    mock_set_config_setting,
                                                    sqnotes_obj : SQNotes,
                                                    configuration_module
                                                    ):
            test_editor = 'vim'
            sqnotes_obj._set_configured_text_editor(editor = test_editor)
            mock_set_config_setting.assert_called_once_with(key = TEXT_EDITOR_KEY, value = test_editor)
            
        
            
            
            