"""
Chatbot Module
Author: morningstar
Description: Enhanced chatbot with advanced NLP and voice support.
"""

import speech_recognition as sr
import pyttsx3
import openai

openai.api_key = "YOUR_OPENAI_API_KEY"  # Replace with your actual API key

class Chatbot:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.context = []

    def listen(self):
        with self.microphone as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
        try:
            text = self.recognizer.recognize_google(audio)
            print(f"User said: {text}")
            return text
        except sr.UnknownValueError:
            return "Sorry, I did not understand that."
        except sr.RequestError:
            return "Sorry, speech service is unavailable."

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def process_input(self, user_input):
        self.context.append({"role": "user", "content": user_input})
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=self.context
        )
        answer = response.choices[0].message['content']
        self.context.append({"role": "assistant", "content": answer})
        self.speak(answer)
        return answer
