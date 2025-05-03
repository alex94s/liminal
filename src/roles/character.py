# -*- coding: utf-8 -*-
"""
Module Name: character.py

Description:
This module contains the code for the chatbot that interacts with the user via WhatsApp.
The chatbot uses the OpenAI API to generate responses from a user-specified character.
User input and bot responses are stored in a MySQL database.

Author: elreysausage
Date: 2025-02-23
"""

import os
import re

from flask import Flask, request, jsonify
import openai

import src.core.utils as utils


app = Flask(__name__)


def get_past_interactions(character: str) -> str:
    """
    Retrieve the past interactions with the specified character.
    """
    conn, cursor = utils.connect_db()
    cursor.execute(
        "SELECT user_input, bot_response "
        "FROM messages "
        "WHERE character_name = %s "
        "ORDER BY id DESC LIMIT 5",
        (character,)
    )
    history = cursor.fetchall()
    conversation = ""
    for user_input, bot_response in history:
        conversation += f"User: {user_input}\n{character}: {bot_response}\n"
    return conversation


def generate_character_reply(user_input: str, character: str) -> str:
    """
    Generate a reply from the specified character based on the user input.
    
    Args:
        user_input: The user's message.
        character: The character to generate a reply from.

    Returns:
        The character's response to the user's message.
    """
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    conversation_history = get_past_interactions(character)
    prompt = f"{character}: {conversation_history}\nUser: {user_input}\n{character}:" 
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": (
                f"You are {character}. Stay fully in character, responding with their tone, "
                f"mannerisms, and personality. Ensure the conversation flows naturally within "
                f"the character’s nature—if they are reserved, they stay reserved, if they are "
                f"engaging, they remain engaging. Adjust your response length to be roughly "
                f"similar to the user's message length — if they are brief, be succinct; "
                f"if they are more detailed, respond with greater depth, but do not exceed "
                f"what feels natural for a conversation."
            )},
            {"role": "user", "content": prompt}
        ]
    )
    return response["choices"][0]["message"]["content"]


@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply() -> str:
    """
    Handle incoming messages from UltraMsg and generate a response.
    """
    data = request.get_json()
    incoming_msg = data.get("data", {}).get("body", "").strip()
    user_phone = data.get("data", {}).get("from", "").strip()

    if not incoming_msg:
        return jsonify({"error": "Received blank message"}), 400
    
    conn, cursor = utils.connect_db()
    char_match = re.match(r"Set Character:\s*(.+)", incoming_msg, re.IGNORECASE)

    if char_match:
        character = char_match.group(1).strip()
        cursor.execute(
            "INSERT INTO messages (user_input, bot_response, character_name) VALUES (%s, %s, %s)",
            (incoming_msg, f"Character set to {character}.", character)
        )
        conn.commit()
        utils.send_message(f"Character set to {character}. Continue chatting!", user_phone)
        return jsonify({"status": "Character updated"})
    
    cursor.execute(
        "SELECT character_name FROM messages "
        "WHERE character_name IS NOT NULL AND character_name != '' "
        "ORDER BY id DESC LIMIT 1"
    )
    last_character = cursor.fetchone()
    character = last_character[0] if last_character else "Mephistopheles"
    bot_response = generate_character_reply(incoming_msg, character)
    utils.store_interaction(user_phone, incoming_msg, bot_response, character)
    utils.send_message(bot_response, user_phone)
    return jsonify({"status": "Message sent"})


if __name__ == "__main__":
    app.run(port=5001, debug=False, use_reloader=False)
