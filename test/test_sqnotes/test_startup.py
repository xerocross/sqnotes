
from unittest.mock import patch

import pytest
from sqnotes.sqnotes_module import SQNotes
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def describe_sqnotes_startup():
        
    @patch.object(SQNotes, '_setup_user_configuration')
    def it_calls_setup_user_config(
                                                    mock_setup_user_config,
                                                    sqnotes_obj
                                                    ):
        sqnotes_obj.startup()
        mock_setup_user_config.assert_called_once()



    