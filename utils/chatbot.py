"""
Chatbot Module
Author: morningstar
Description: Enhanced chatbot with advanced NLP support.
"""

import openai
import re

openai.api_key = "YOUR_OPENAI_API_KEY"  # Replace with your actual API key

class Chatbot:
    def __init__(self):
        self.context = []

    def process_input(self, user_input):
        """Process user input and provide intelligent responses."""
        # Handle common user queries
        if re.search(r"(scan not working|scan failed|scan issue)", user_input, re.IGNORECASE):
            return "If your scan is not working, ensure the target IP is reachable and the port range is valid."
        elif re.search(r"(how to use wireless attack|wireless attack help)", user_input, re.IGNORECASE):
            return "To use the wireless attack feature, provide a valid target IP and ensure your device supports wireless attacks."
        elif re.search(r"(server status|is the server running)", user_input, re.IGNORECASE):
            return "You can check the server status in the app's Server Monitoring tab."

        # Use OpenAI GPT for other queries
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": user_input}]
            )
            return response.choices[0].message['content']
        except Exception as e:
            return f"Sorry, I couldn't process your request. Error: {e}"
