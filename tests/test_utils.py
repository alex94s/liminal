# -*- coding: utf-8 -*-
"""
Module Name: test_utils.py

Description:
This module contains unit tests for the utility functions shared across multiple chatbot
implementations, including database connectivity, message handling, and API communication.

Author: elreysausage

Date: 2025-02-25
"""

import unittest
from unittest.mock import patch, MagicMock

import src.core.utils as utils


class TestUtils(unittest.TestCase):
    """
    Test cases for the utility functions.
    """
    @patch('src.core.utils.mysql.connector.connect')
    def test_connect_db(self, mock_connect: MagicMock) -> None:
        """
        Test the database connection function.

        Args:
            mock_connect: Mocked mysql.connector.connect function.
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        conn, cursor = utils.connect_db()
        mock_connect.assert_called_once()
        mock_conn.cursor.assert_called_once()
        mock_cursor.execute.assert_called()
        mock_conn.commit.assert_called_once()
        self.assertEqual(conn, mock_conn)
        self.assertEqual(cursor, mock_cursor)

    @patch('src.core.utils.requests.post')
    @patch('src.core.utils.time.sleep', return_value=None)
    def test_send_message(self, mock_sleep: MagicMock, mock_post: MagicMock) -> None:
        """
        Test the send_message function.

        Args:
            mock_sleep: Mocked time.sleep function.
            mock_post: Mocked requests.post function.
        """
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        with patch.dict(
            'os.environ', 
            {"ULTRAMSG_TOKEN": "dummy_token", "ULTRAMSG_INSTANCE_ID": "dummy_id"}
        ): utils.send_message("Hello! How are you?", "+1234567890")

        mock_post.assert_called()

    def test_split_message(self) -> None:
        """
        Test the split_message function.

        Args:
            text: The text to split.
        """
        text = (
            "This is a long message that needs to be split. "
            "It contains multiple sentences. "
            "Let's see if it works correctly."
        )
        expected_output = [
            "This is a long message that needs to be split.",
            "It contains multiple sentences.",
            "Let's see if it works correctly."
        ]
        result = utils.split_message(text, max_length=50)
        self.assertEqual(result, expected_output)

    @patch('src.core.utils.connect_db')
    def test_store_interaction(self, mock_connect_db: MagicMock) -> None:
        """
        Test the store_interaction function.

        Args:
            mock_connect_db: Mocked connect_db function.
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = (mock_conn, mock_cursor)
        utils.store_interaction("+1234567890", "Hi", "Hello!", "Bot")
        mock_cursor.execute.assert_called_once()
        mock_conn.commit.assert_called_once()


if __name__ == '__main__':
    unittest.main()
