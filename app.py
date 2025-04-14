from flask import Flask, render_template, request # type: ignore
import requests # type: ignore
import speech_recognition as sr
import pyttsx3
import logging
import random
from datetime import datetime

app = Flask(__name__)

logging.basicConfig(filename='NOVA_log.txt', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

engine = pyttsx3.init()
recognizer = sr.Recognizer()

responses = {
    "greeting": [f"Hello, I’m Nova! How can I assist you today, sir?",
                 f"Greetings, sir! Nova at your service.",
                 f"Hey there, sir! Nova’s ready to help!"],
    "search": [f"Searching the vast knowledge net for you, sir... Here’s what I found:",
               f"Let me dive into the web for you, sir..."],
    "default": [f"I’m not sure about that, sir. Can you clarify?"]
}

def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        logging.error(f"Error in text-to-speech: {e}")

def listen():
    with sr.Microphone() as source:
        logging.info("Calibrating for background noise...")
        recognizer.adjust_for_ambient_noise(source, duration=5)
        logging.info("Listening...")
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            command = recognizer.recognize_google(audio).lower()
            logging.debug(f"Recognized command: {command}")
            return command
        except sr.UnknownValueError:
            logging.warning("Could not understand audio")
            return ""
        except sr.RequestError as e:
            logging.error(f"Request error: {e}")
            return ""

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q', '')
    if query:
        api_key = "AIzaSyAAdsRzIY3HyD5dTpcpHV_k5vnxJUJIJZw"  # Update with your API key
        cse_id = "c4b7c6db7c6154d21"  # Update with your CSE ID
        url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={query}"
        try:
            response = requests.get(url)
            data = response.json()
            if 'items' in data:
                result = data['items'][0]['snippet'] if data['items'] else "No relevant results found."
                return render_template('search.html', query=query, result=result)
            else:
                return render_template('search.html', query=query, result=f"Error: {data.get('error', {}).get('message', 'Unknown error')}")
        except requests.RequestException as e:
            return render_template('search.html', query=query, result=f"Error: {str(e)}")
    return render_template('search.html', query='', result='Please enter a search query.')

@app.route('/voice', methods=['GET'])
def voice_command():
    command = listen()
    if "search" in command:
        query = command.replace("search", "").strip()
        if query:
            api_key = "AIzaSyAAdsRzIY3HyD5dTpcpHV_k5vnxJUJIJZw"  # Update with your API key
            cse_id = "c4b7c6db7c6154d21"  # Update with your CSE ID
            url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={query}"
            try:
                response = requests.get(url)
                data = response.json()
                if 'items' in data:
                    result = data['items'][0]['snippet'] if data['items'] else "No relevant results found."
                    speak(random.choice(responses["search"]) + f" {result}")
                    return f"Spoken: {result}"
                else:
                    error = f"Error: {data.get('error', {}).get('message', 'Unknown error')}"
                    speak(error)
                    return error
            except requests.RequestException as e:
                error = f"Error: {str(e)}"
                speak(error)
                return error
    speak(random.choice(responses["default"]))
    return "Command not recognized"

if __name__ == '__main__':
    app.run(debug=True)