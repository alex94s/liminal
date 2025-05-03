# -*- coding: utf-8 -*-
"""
Module Name: test_character.py

Description:
This module contains unit tests for the character functions of the chatbot implementation, 
including the chatbot response generation and message handling.

Author: elreysausage

Date: 2025-02-25
"""

import unittest
from unittest.mock import patch, MagicMock

from flask import json

import src.roles.character as character


class TestCharacter(unittest.TestCase):
    """
    Test cases for the character functions.
    """
    @patch('src.core.utils.connect_db')
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
            ("Tell me a story", "Once upon a time...")
        ]
        history = character.get_past_interactions("Mephistopheles")
        expected = (
            "User: Hello\n"
            "Mephistopheles: Hi there!\n"
            "User: Tell me a story\n"
            "Mephistopheles: Once upon a time...\n"
        )
        self.assertEqual(history, expected)
    
    @patch('src.core.utils.openai.ChatCompletion.create')
    @patch('src.core.utils.get_past_interactions', 
           return_value="User: Hello\nMephistopheles: Hi there!\n")
    def test_generate_character_reply(
        self, 
        mock_get_past_interactions: MagicMock, 
        mock_openai: MagicMock
    ) -> None:
        """
        Test the generate_character_reply function.

        Args:
            mock_get_past_interactions: Mocked get_past_interactions function.
            mock_openai: Mocked ChatCompletion.create function.
        """
        mock_response = MagicMock()
        mock_response["choices"] = [{"message": {"content": "Greetings, mortal."}}]
        mock_openai.return_value = mock_response
        
        with patch.dict('os.environ', {"OPENAI_API_KEY": "dummy_key"}):
            reply = character.generate_character_reply("Who are you?", "Mephistopheles")
    
        self.assertEqual(reply, "Greetings, mortal.")
    
    @patch('src.core.utils.store_interaction')
    @patch('src.core.utils.send_message')
    @patch('src.role.character.generate_character_reply', return_value="Greetings, mortal.")
    def test_whatsapp_reply(
        self, 
        mock_generate_reply: MagicMock, 
        mock_send_message: MagicMock, 
        mock_store_interaction: MagicMock
    ) -> None:
        """
        Test the WhatsApp reply function.

        Args:
            mock_generate_reply: Mocked generate_character_reply function.
            mock_send_message: Mocked send_message function.
            mock_store_interaction: Mocked store_interaction function.
        """
        app = character.app.test_client()
        data = {"data": {"body": "Tell me a secret", "from": "+1234567890"}}
        response = app.post("/whatsapp", data=json.dumps(data), content_type="application/json")
        self.assertEqual(response.status_code, 200)
        mock_generate_reply.assert_called_once_with("Tell me a secret", "Mephistopheles")
        mock_store_interaction.assert_called_once_with(
            "+1234567890", "Tell me a secret", "Greetings, mortal.", "Mephistopheles"
        )
        mock_send_message.assert_called_once_with("Greetings, mortal.", "+1234567890")


if __name__ == '__main__':
    unittest.main()
