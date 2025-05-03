# -*- coding: utf-8 -*-
"""
Module Name: test_assistant.py

Description:
This module contains unit tests for the assistant functions of the chatbot implementation, 
including the chatbot response generation and message handling.

Author: elreysausage

Date: 2025-02-25
"""

import unittest
from unittest.mock import patch, MagicMock

from flask import json

import src.roles.assistant as assistant


class TestAssistant(unittest.TestCase):
    """
    Test cases for the assistant functions.
    """
    @patch('src.role.assistant.utils.connect_db')
    def test_get_past_interactions(self, mock_connect_db: MagicMock) -> None:
        """
        Test the get_past_interactions function.

        Args:
            mock_connect_db: Mocked connect_db function.
        """
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect_db.return_value = (mock_conn, mock_cursor)
        mock_cursor.fetchall.return_value = [
            ("Hello", "Hi there!"),
            ("How are you?", "I'm doing well!")
        ]
        history = assistant.get_past_interactions("+1234567890")
        expected = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"},
            {"role": "assistant", "content": "I'm doing well!"}
        ]
        self.assertEqual(history, expected)
    
    @patch('src.role.assistant.openai.ChatCompletion.create')
    @patch('src.role.assistant.get_past_interactions', return_value=[])
    def test_generate_reply(
        self, 
        mock_get_past_interactions: MagicMock, 
        mock_openai: MagicMock
    ) -> None:
        """
        Test the generate_reply function.

        Args:
            mock_get_past_interactions: Mocked get_past_interactions function.
            mock_openai: Mocked OpenAI API client.
        """
        mock_openai.return_value = {
            "choices": [{"message": {"content": "Hello!"}}]
        }
        with patch.dict('os.environ', {"OPENAI_API_KEY": "dummy_key"}):
            reply = assistant.generate_reply("Hi!", "+1234567890")
        self.assertEqual(reply, "Hello!")
    
    @patch('src.role.assistant.utils.store_interaction')
    @patch('src.role.assistant.utils.send_message')
    @patch('src.role.assistant.generate_reply', return_value="Hello!")
    def test_whatsapp_reply(
        self, 
        mock_generate_reply: MagicMock, 
        mock_send_message: MagicMock, 
        mock_store_interaction: MagicMock
    ) -> None:
        """
        Test the WhatsApp reply function.

        Args:
            mock_generate_reply: Mocked generate_reply function.
            mock_send_message: Mocked send_message function.
            mock_store_interaction: Mocked store_interaction function.
        """
        app = assistant.app.test_client()
        data = {"data": {"body": "Hi!", "from": "+1234567890"}}
        response = app.post("/whatsapp", data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        mock_generate_reply.assert_called_once_with("Hi!", "+1234567890")
        mock_store_interaction.assert_called_once_with("+1234567890", "Hi!", "Hello!")
        mock_send_message.assert_called_once_with("Hello!", "+1234567890")


if __name__ == '__main__':
    unittest.main()
