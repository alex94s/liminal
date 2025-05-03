# -*- coding: utf-8 -*-
"""
Module Name: utils.py

Description:
This module contains utility functions shared across multiple chatbot 
implementations, including database connectivity, message handling, and 
API communication.

Author: elreysausage
Date: 2025-02-24
"""

import os
import random
import re
import time
from datetime import datetime

import requests
import mysql.connector


def connect_db() -> tuple:
    """
    Connect to the MySQL database.
    """
    conn = mysql.connector.connect(
        host=os.environ.get('DB_HOST'),
        user=os.environ.get('DB_USER'),
        password=os.environ.get('DB_PASSWORD'),
        database='liminal'
    )
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_phone VARCHAR(20),
        user_input TEXT,
        bot_response TEXT,
        character_name TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    return conn, cursor


def send_message(message: str, user_phone: str) -> None:
    """
    Send a message to the user via UltraMsg.

    Args:
        message: The message to send.
        user_phone: The user's phone number
    """
    ULTRAMSG_TOKEN = os.environ.get("ULTRAMSG_TOKEN")
    ULTRAMSG_INSTANCE_ID = os.environ.get("ULTRAMSG_INSTANCE_ID")
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
    message_chunks = split_message(message)

    for chunk in message_chunks:
        delay = random.uniform(1.5, 4.0)
        time.sleep(delay)
        payload = {
            "token": ULTRAMSG_TOKEN,
            "to": user_phone,
            "body": chunk
        }
        requests.post(url, json=payload)


def split_message(text: str, max_length: int = 100) -> list:
    """
    Split a long message into chunks of a specified maximum length.

    Args:
        text: The text to split.
        max_length: The maximum length of each chunk.
    
    Returns:
        A list of message chunks.
    """
    if len(text) <= max_length:
        return [text]
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_length:
            current_chunk += " " + sentence if current_chunk else sentence
        else:
            chunks.append(current_chunk)
            current_chunk = sentence
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


def store_interaction(user_phone: str, user_input: str, bot_response: str, character: str):
    """
    Store the user input and bot response in the database.
    """
    conn, cursor = connect_db()
    cursor.execute(
        "INSERT INTO messages (user_phone, user_input, bot_response, character_name, timestamp) "
        "VALUES (%s, %s, %s, %s, %s)",
        (user_phone, user_input, bot_response, character, datetime.now())
    )
    conn.commit()
