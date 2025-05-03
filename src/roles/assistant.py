# -*- coding: utf-8 -*-
"""
Module Name: assistant.py

Description:
This module contains the code for a chatbot that interacts with users via WhatsApp. 
The chatbot uses the OpenAI API to generate responses and stores interactions in a 
MySQL database.

Author: elreysausage
Date: 2025-02-23
"""

import os

from flask import Flask, request, jsonify
import openai

import src.core.utils as utils


app = Flask(__name__)


def get_past_interactions(user_phone: str, limit: int = 5) -> list:
    """
    Retrieve past interactions for a user in chronological order.
    """
    conn, cursor = utils.connect_db()
    cursor.execute(
        "SELECT user_input, bot_response FROM messages "
        "WHERE user_phone = %s ORDER BY id ASC LIMIT %s",
        (user_phone, limit)
    )
    history = cursor.fetchall()
    result = []
    for user_input, bot_response in history:
        result.append({"role": "user", "content": user_input})
        result.append({"role": "assistant", "content": bot_response})
    
    return result 


def generate_reply(user_input: str, user_phone: str) -> str:
    """
    Generate a reply using OpenAI's API, keeping context from the last few exchanges.
    """
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    conversation_history = get_past_interactions(user_phone)
    messages = [
        {"role": "system", "content": (
            "You are an unhelpful AI assistant. "
            "Respond succinctly and clearly."
        )}
    ]
    if conversation_history:
        messages.extend(conversation_history)
    
    messages.append({"role": "user", "content": user_input})
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages
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
    
    bot_response = generate_reply(incoming_msg, user_phone)
    utils.store_interaction(user_phone, incoming_msg, bot_response, "AI Assistant")
    utils.send_message(bot_response, user_phone)
    return jsonify({"status": "Message sent"})


if __name__ == "__main__":
    app.run(port=5001, debug=False, use_reloader=False)
