"""
Chatbot Module
Author: morningstar
Description: Enhanced chatbot with advanced NLP support.
"""

import openai

openai.api_key = "YOUR_OPENAI_API_KEY"  # Replace with your actual API key

class Chatbot:
    def __init__(self):
        self.context = []

    def process_input(self, user_input):
        self.context.append({"role": "user", "content": user_input})
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=self.context
        )
        answer = response.choices[0].message['content']
        self.context.append({"role": "assistant", "content": answer})
        return answer
