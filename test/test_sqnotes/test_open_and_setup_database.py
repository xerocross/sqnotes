

import pytest
from unittest.mock import patch
from sqnotes.sqnotes_module import SQNotes, CouldNotOpenDatabaseException
from sqnotes.database_service import DatabaseService
from test.test_helper import just_return, do_nothing
from conftest import sqnotes_obj

def describe_open_database():
    
    def describe_database_is_set_up():
    
        @pytest.mark.usefixtures('mock_get_database_file_path',
                                 'mock_get_notes_dir_from_config')
        @patch.object(SQNotes, '_get_is_database_set_up', just_return(True))
        @patch.object(SQNotes, 'setup_database', do_nothing)
        @patch.object(DatabaseService, 'connect')
        
        def it_connects_database_service(
                                                mock_dbservice_connect,
                                                sqnotes_obj : SQNotes
                                         ):
            sqnotes_obj.open_database()
            mock_dbservice_connect.assert_called_once()
            
            
        @pytest.mark.usefixtures('mock_get_database_file_path',
                                 'mock_get_notes_dir_from_config')
        @patch.object(SQNotes, '_get_is_database_set_up', just_return(True))
        @patch.object(SQNotes, 'setup_database')
        @patch.object(DatabaseService, 'connect')
        def it_does_not_setup_database(
                                                mock_dbservice_connect,
                                                mock_setup_database,
                                                sqnotes_obj : SQNotes
                                         ):
            sqnotes_obj.open_database()
            mock_setup_database.assert_not_called()
            
        def describe_error_on_connecting_to_database():
        
        
            @pytest.mark.usefixtures('mock_get_database_file_path',
                                     'mock_get_notes_dir_from_config')
            @patch.object(SQNotes, '_get_is_database_set_up', just_return(True))
            @patch.object(SQNotes, 'setup_database', do_nothing)
            @patch.object(DatabaseService, 'connect')
            def it_raises_could_not_open_database_exception(
                                                            mock_dbservice_connect,
                                                            sqnotes_obj : SQNotes
                                                            ):
                mock_dbservice_connect.side_effect = Exception()
                with pytest.raises(CouldNotOpenDatabaseException):
                    sqnotes_obj.open_database()
            
    def describe_database_is_not_set_up():
            
            
        @pytest.mark.usefixtures('mock_get_database_file_path',
                                 'mock_get_notes_dir_from_config')
        @patch.object(SQNotes, '_get_is_database_set_up', just_return(False))
        @patch.object(SQNotes, 'setup_database', do_nothing)
        @patch.object(DatabaseService, 'connect')
        def it_connects_database_service(
                                                mock_dbservice_connect,
                                                sqnotes_obj : SQNotes
                                         ):
            sqnotes_obj.open_database()
            mock_dbservice_connect.assert_called_once()
            
            
        @pytest.mark.usefixtures('mock_get_database_file_path',
                                 'mock_get_notes_dir_from_config')
        @patch.object(SQNotes, '_get_is_database_set_up', just_return(False))
        @patch.object(DatabaseService, 'connect', do_nothing)
        @patch.object(SQNotes, 'setup_database')
        def it_calls_to_set_up_database(
                                                mock_setup_database,
                                                sqnotes_obj : SQNotes
                                         ):
            sqnotes_obj.open_database()
            mock_setup_database.assert_called_once()
            
            
        def describe_error_on_connecting_to_database():
        
        
            @pytest.mark.usefixtures('mock_get_database_file_path',
                                     'mock_get_notes_dir_from_config')
            @patch.object(SQNotes, '_get_is_database_set_up', just_return(False))
            @patch.object(SQNotes, 'setup_database', do_nothing)
            @patch.object(DatabaseService, 'connect')
            def it_raises_could_not_open_database_exception(
                                                            mock_dbservice_connect,
                                                            sqnotes_obj : SQNotes
                                                            ):
                mock_dbservice_connect.side_effect = Exception()
                with pytest.raises(CouldNotOpenDatabaseException):
                    sqnotes_obj.open_database()
            
            
def describe_setup_database():
    
    @pytest.mark.usefixtures('mock_print')
    @patch.object(SQNotes, '_set_database_is_set_up', do_nothing)
    @patch.object(DatabaseService, 'setup_database')
    def it_calls_database_service_to_set_up_database(
                                                        mock_setup_database,
                                                        sqnotes_obj: SQNotes
                                                     ):
        sqnotes_obj.setup_database()
        mock_setup_database.assert_called_once()
    
    
    @pytest.mark.usefixtures('mock_print')
    @patch.object(DatabaseService, 'setup_database', do_nothing)
    @patch.object(SQNotes, '_set_database_is_set_up')
    def it_calls_set_database_is_set_up(
                                                        mock_set_database_is_set_up,
                                                        sqnotes_obj: SQNotes
                                                     ):
        sqnotes_obj.setup_database()
        mock_set_database_is_set_up.assert_called_once()
    
    
            
