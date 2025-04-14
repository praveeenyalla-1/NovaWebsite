import os
import logging
import speech_recognition as sr
import pyttsx3
from datetime import datetime, timedelta
import requests
import random
import ast
import time
import re

# Configure logging to show in both terminal and file
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('nova_log.txt'),
        logging.StreamHandler()  # Shows logs in terminal
    ]
)

# Initialize text-to-speech engine
engine = pyttsx3.init()
recognizer = sr.Recognizer()

# In-memory task list and memory for conversation context
tasks = []
memory = []  # Simulated memory (across sessions with UI integration)

# Nova personality responses (updated to address as "sir")
def get_address():
    return "sir"  # Fixed to "sir" instead of random choice

responses = {
    "greeting": [f"Hello, I’m Nova! How can I assist you today, {get_address()}?", 
                 f"Greetings, {get_address()}! Nova at your service.", 
                 f"Hey there, {get_address()}! Nova’s ready to help!"],
    "search": [f"Searching the vast knowledge net for you, {get_address()}... Here’s what I found:", 
               f"Let me dive into the web for you, {get_address()}..."],
    "improve": [f"A chance to evolve? Tell me what to add, {get_address()}!", 
                f"Upgrading Nova—give me a challenge, {get_address()}!"],
    "success": [f"Evolution complete, {get_address()}! Restart me to use it.", 
                f"Success! Nova’s smarter now, {get_address()}!"],
    "failure": [f"Oops, an error occurred, {get_address()}. Check the logs.", 
                f"I stumbled, {get_address()}. Let’s try that again."],
    "reminder_set": [f"Reminder noted, {get_address()}. I’ll alert you when it’s time!", 
                     f"Task logged in my circuits, {get_address()}!"],
    "default": [f"I’m not sure about that, {get_address()}. Can you clarify?"]
}

def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        logging.error(f"Error in text-to-speech: {e}")

def listen():
    with sr.Microphone() as source:
        logging.info("Calibrating for background noise...")  # Should show in terminal
        recognizer.adjust_for_ambient_noise(source, duration=5)
        logging.info("Listening...")  # Should show in terminal
        try:
            audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
            command = recognizer.recognize_google(audio).lower()
            logging.debug(f"Recognized command: {command}")
            memory.append(command)  # Store in memory
            return command
        except sr.UnknownValueError:
            logging.warning("Could not understand audio")
            return ""
        except sr.RequestError as e:
            logging.error(f"Request error: {e}")
            return ""

def get_time():
    return f"The current time is {datetime.now().strftime('%H:%M')}."

def get_date():
    return f"Today is {datetime.now().strftime('%Y-%m-%d')}."

def get_weather(city):
    api_key = "40dcaa6ac8960fd318097520fa705a21"
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if data["cod"] == 200:
            return f"The weather in {city} is {data['main']['temp']}°C with {data['weather'][0]['description']}."
        return f"Error: {data['message']}"
    except requests.RequestException as e:
        logging.error(f"Error fetching weather data: {e}")
        return "Unable to fetch weather data at the moment."

def show_menu():
    return ("Available commands: say 'hi' or 'hello' to start, 'time' for current time, "
            "'date' for today’s date, 'weather' or 'what about' then a city for weather, "
            "'menu' for this list, 'improve' to enhance Nova with a new feature, "
            "'code' then topic (e.g., 'code email') to generate code, "
            "'open' then a site (e.g., 'open youtube') to open websites, "
            "'search' then topic (e.g., 'search ai') for info, "
            "'remind me' then task and time (e.g., 'remind me to call at 3pm') to set a reminder, or 'exit' to quit.")

def self_improve(feature_request=""):
    current_code = open(__file__, 'r').read()
    if not feature_request:
        new_feature = random.choice([
            "def get_insight():\n    return f'Nova’s insight: The universe is vast! {datetime.now().strftime('%H:%M')}'",
            "def get_tip():\n    tips = ['Learn Python!', 'Explore space!']\n    return random.choice(tips)"
        ])
    else:
        new_feature = generate_code_from_request(feature_request, current_code)
    
    if new_feature and any(func not in current_code for func in ["get_insight", "get_tip", "send_email", "send_whatsapp_message", "control_device"]):
        new_code = current_code.replace("def show_menu():", f"{new_feature}\n\ndef show_menu():")
        try:
            ast.parse(new_code)  # Check for syntax errors
            with open(__file__, 'w') as f:
                f.write(new_code)
            feature_name = new_feature.split('\n')[0] if '\n' in new_feature else new_feature
            speak(random.choice(responses["success"]) + f" New feature: {feature_name}. Restart me, {get_address()}!")
            return True
        except SyntaxError as e:
            logging.error(f"Syntax error in new code: {e}")
            speak(random.choice(responses["failure"]))
            return False
    speak(random.choice(responses["default"]))
    return False

def generate_code_from_request(request, current_code):
    if "email" in request:
        return (
            "def send_email(to_email, subject, body):\n"
            "    import smtplib\n"
            "    from email.mime.text import MIMEText\n"
            "    msg = MIMEText(body)\n"
            "    msg['Subject'] = subject\n"
            "    msg['From'] = 'your_email@gmail.com'\n"
            "    msg['To'] = to_email\n"
            "    with smtplib.SMTP('smtp.gmail.com', 587) as server:\n"
            "        server.starttls()\n"
            "        server.login('your_email@gmail.com', 'your_password')\n"
            "        server.send_message(msg)\n"
            "    return 'Email sent (configure credentials first)'"
        )
    elif "whatsapp" in request:
        return (
            "def send_whatsapp_message(number, message):\n"
            "    print(f'Sending to {number}: {message}')\n"
            "    return 'Message sent (simulated)'"
        )
    elif "device" in request or "control" in request:
        return (
            "def control_device(device, action):\n"
            "    devices = {'light': 'simulated_light', 'fan': 'simulated_fan'}\n"
            "    if device in devices and action in ['on', 'off']:\n"
            "        print(f'{devices[device]} {action}')\n"
            "        return f'{device} {action} successfully'\n"
            "    return 'Device or action not recognized'"
        )
    else:
        speak(random.choice(responses["default"]) + f" Try 'email', 'whatsapp', or 'device control', {get_address()}.")
        return None

def generate_code(topic):
    if any(f in topic for f in ["email", "whatsapp", "device", "control"]):
        self_improve(topic)
        return True
    speak(random.choice(responses["default"]))
    return False

def open_website(site):
    site_urls = {
        "whatsapp": "https://web.whatsapp.com",
        "youtube": "https://www.youtube.com/",
        "google": "https://www.google.com",
        "facebook": "https://www.facebook.com",
        "instagram": "https://www.instagram.com",
        "chrome": "https://www.google.com"
    }
    logging.debug(f"Attempting to open site: {site} with URL: {site_urls.get(site, 'Not found')}")
    if site in site_urls:
        try:
            url = site_urls[site]
            logging.debug(f"Calling os.startfile with URL: {url}")
            result = os.startfile(url)
            logging.debug(f"os.startfile result for {site}: {result}")
            speak(f"Opening {site} for you, {get_address()}!")
        except Exception as e:
            logging.error(f"Error opening {site}: {e}")
            speak(f"Sorry, I couldn’t open {site}. Check your setup, {get_address()}.")
    else:
        speak(f"Site '{site}' not recognized. Try another, {get_address()}!")

def search_web(topic):
    # Real web search using Google Custom Search API
    api_key = "AIzaSyAAdsRzIY3HyD5dTpcpHV_k5vnxJUJIJZw"  # Your provided API key (verify full length)
    cse_id = "c4b7c6db7c6154d21"  # Your Search Engine ID from the script
    url = f"https://www.googleapis.com/customsearch/v1?key={api_key}&cx={cse_id}&q={topic}"
    try:
        response = requests.get(url)
        data = response.json()
        if 'items' in data:
            result = data['items'][0]['snippet'] if data['items'] else "No relevant results found."
            speak(random.choice(responses["search"]) + f" {result}")
        else:
            speak(f"Search failed, {get_address()}. Error: {data.get('error', {}).get('message', 'Unknown error')}")
    except requests.RequestException as e:
        logging.error(f"Error fetching search data: {e}")
        speak(f"Couldn’t search the web, {get_address()}. Check your API setup.")

def schedule_task(task, time_str):
    try:
        if "pm" in time_str.lower():
            hour = int(re.search(r'\d+', time_str.split("pm")[0]).group()) + 12 if int(re.search(r'\d+', time_str.split("pm")[0]).group()) != 12 else 12
            minute = 0
        elif "am" in time_str.lower():
            hour = int(re.search(r'\d+', time_str.split("am")[0]).group()) if int(re.search(r'\d+', time_str.split("am")[0]).group()) != 12 else 0
            minute = 0
        else:
            hour, minute = map(int, time_str.split(":"))
        
        now = datetime.now()
        task_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        if task_time < now:
            task_time += timedelta(days=1)
        
        tasks.append({"task": task, "time": task_time})
        speak(random.choice(responses["reminder_set"]))
        logging.info(f"Scheduled task: {task} at {task_time}")
    except (ValueError, AttributeError) as e:
        logging.error(f"Error parsing time: {e}")
        speak(random.choice(responses["failure"]))

def check_tasks():
    while tasks:
        current_time = datetime.now()
        for task in tasks[:]:
            if current_time >= task["time"]:
                speak(f"Alert: {task['task']} at {current_time.strftime('%H:%M')}, {get_address()}")
                tasks.remove(task)
        time.sleep(10)

def main():
    speak(random.choice(responses["greeting"]))
    import threading
    task_thread = threading.Thread(target=check_tasks, daemon=True)
    task_thread.start()
    try:
        while True:
            command = listen()
            if "hi" in command or "hello" in command:
                speak(random.choice(responses["greeting"]))
            elif "time" in command:
                speak(get_time())
            elif "date" in command:
                speak(get_date())
            elif "weather" in command or "what about" in command:
                speak(f"Please name a city, {get_address()}.")
                city = listen()
                if city:
                    speak(get_weather(city))
                else:
                    speak(f"City not recognized. Try again, {get_address()}.")
            elif "menu" in command:
                speak(show_menu())
            elif "improve" in command:
                speak(random.choice(responses["improve"]))
                feature_request = listen()
                if feature_request:
                    if self_improve(feature_request):
                        speak(random.choice(responses["success"]))
                    else:
                        speak(random.choice(responses["failure"]))
            elif "code" in command:
                speak(f"Specify a feature, {get_address()} (e.g., 'code email').")
                topic = listen()
                if topic:
                    generate_code(topic)
            elif "open" in command:
                site_words = command.split()
                site = site_words[1] if len(site_words) > 1 else ""
                if site:
                    open_website(site)
                else:
                    speak(f"Please specify a site, {get_address()} (e.g., 'open youtube').")
            elif "search" in command:
                speak(f"What topic should I search, {get_address()}? (e.g., 'search ai')")
                topic = listen().split()[1] if len(listen().split()) > 1 else ""
                if topic:
                    search_web(topic)
                else:
                    speak(f"Please provide a topic, {get_address()}!")
            elif "remind me" in command:
                speak(f"State the task and time (e.g., 'to call at 3pm'), {get_address()}.")
                reminder = listen()
                if reminder:
                    parts = reminder.split("at")
                    if len(parts) == 2:
                        task = parts[0].strip()
                        time_str = parts[1].strip()
                        schedule_task(task, time_str)
                    else:
                        speak(f"Use format 'task at time', {get_address()}.")
            elif "exit" in command:
                speak(f"Shutting down, {get_address()}. Farewell!")
                break
            elif command and memory:  # Contextual response
                if any(prev in command for prev in memory[-3:]):  # Check last 3 commands
                    speak(f"Following up on {memory[-1]}. What next, {get_address()}?")
                else:
                    speak(random.choice(responses["default"]))
    except KeyboardInterrupt:
        speak(f"Emergency shutdown initiated, {get_address()}!")

if __name__ == "__main__":
    main()