# liminal

## Overview
`liminal` is a chatbot package that enables interactive conversations via WhatsApp. It utilizes the OpenAI API to generate responses from a user-specified role and stores interactions in a MySQL database. The chatbot integrates UltraMsg's messaging API to send and receive messages seamlessly.

## Installation
### **Prerequisites**
Ensure you have the following installed:
- Python 3.10+
- MySQL server
- UltraMsg API account
- OpenAI API key

### **Clone the Repository**
```sh
$ git clone https://github.com/your-repo/liminal.git
$ cd liminal
```

### **Install Dependencies**
```sh
$ pip install -r requirements.txt
```

## Configuration
### **Set Up Environment Variables**
Create a `.env` file and add the following credentials:
```
ULTRAMSG_INSTANCE_ID=your_ultramsg_instance_id
ULTRAMSG_TOKEN=your_ultramsg_token
OPENAI_API_KEY=your_openai_api_key
DB_HOST=your_db_host
DB_USER=your_db_user
DB_PASSWORD=your_db_password
```

## Usage
### **Start the Chatbot**
Run the script with the chosen role:
```sh
$ python assistant.py  # For a general AI assistant
$ python character.py  # For character-based interaction
```

### **Interacting with the Bot**
Send a WhatsApp message to your UltraMsg number. The bot responds in character based on message history.

#### **Defining a Character**
To specify a character dynamically, send a message:
```
Set Character: Sherlock Holmes
```
The bot will now respond as **Sherlock Holmes** until you define another character.

#### **Sending Messages**
Once a character is defined, simply send messages:
```
User: What is your deal?
Bot (Sherlock Holmes): My dear Watson, deduction is the key to everything.
```
If no character is defined, the default is **Mephistopheles**.

## Database
The chatbot logs interactions in a MySQL database named `liminal` with the following table:
```sql
CREATE TABLE messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_phone VARCHAR(20),
    user_input TEXT,
    bot_response TEXT,
    character_name TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Deployment
### **Run on a Server**
Use a process manager like `gunicorn` to serve the app:
```sh
$ gunicorn -b 0.0.0.0:5001 chat:create_app()
```

### **Expose via Ngrok (For Local Testing)**
```sh
$ ngrok http 5001
```
Update UltraMsg's webhook settings to point to your Ngrok URL.

## License
This project is licensed under the MIT License.
