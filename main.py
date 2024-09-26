import subprocess
import os
import speech_recognition as sr
import pyttsx3
import webbrowser
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import tkinter as tk
from tkinter import END
import requests
import wikipedia

# Initialize the recognizer and text-to-speech engine once
recognizer = sr.Recognizer()
engine = pyttsx3.init()

# Variable to track if the Wikipedia search is ongoing
searching_wikipedia = False

# Function to make Garuda speak
def speak(text):
    engine.say(text)
    engine.runAndWait()

# Function to listen to user commands with optimizations
def listen():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening for commands...")
        try:
            audio = recognizer.listen(source, timeout=3, phrase_time_limit=5)
            command = recognizer.recognize_google(audio, language='en-in')
            print(f"You said: {command}")
            return command.lower()
        except sr.UnknownValueError:
            speak("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            speak("Sorry, my speech service is down.")
            return None
        except sr.WaitTimeoutError:
            speak("Sorry, I didn't hear anything.")
            return None

# Function to get the weather
def get_weather():
    api_key = "your_api_key_from_open_weather_map"
    city = "your_city_from_open_weather_map"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    
    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            temperature = data['main']['temp']
            weather_description = data['weather'][0]['description']
            weather_info = f"The current temperature in {city} is {temperature}°C with {weather_description}."
            speak(weather_info)
        else:
            speak("I couldn't fetch the weather information.")
    except Exception as e:
        speak(f"Sorry, an error occurred while fetching the weather: {str(e)}")

# Function to search Wikipedia and save the result in a new text file
def search_wikipedia(query):
    global searching_wikipedia
    try:
        speak(f"Searching Wikipedia for {query}")
        summary = wikipedia.summary(query, sentences=3)
        print(summary)

        # Creating a new text file for each search
        filename = f"wikipedia_response_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(filename, "w") as file:
            file.write(f"Search query: {query}\n")
            file.write(f"Wikipedia Summary:\n{summary}")

        speak("I found some information and saved it to a text file.")
    except wikipedia.exceptions.DisambiguationError as e:
        speak("The query is too broad. Please be more specific.")
    except wikipedia.exceptions.PageError:
        speak("I couldn't find any information on Wikipedia for that topic.")
    except Exception as e:
        speak(f"Sorry, an error occurred while searching Wikipedia: {str(e)}")

# Function to create and show the email popup
def show_email_popup():
    global popup, recipient_entry, subject_entry, body_text
    popup = tk.Tk()
    popup.title("Send Email")

    tk.Label(popup, text="Recipient Email:").pack()
    recipient_entry = tk.Entry(popup, width=50)
    recipient_entry.pack()

    tk.Label(popup, text="Subject:").pack()
    subject_entry = tk.Entry(popup, width=50)
    subject_entry.pack()

    tk.Label(popup, text="Body:").pack()
    body_text = tk.Text(popup, height=10, width=50)
    body_text.pack()

    send_button = tk.Button(popup, text="Send Email", command=send_email_action)
    send_button.pack()

    popup.mainloop()

# Function to send email
def send_email_action():
    recipient = recipient_entry.get()
    subject = subject_entry.get()
    body = body_text.get("1.0", END)

    sender_email = "your.email@gmail.com"  # Replace with your email
    sender_password = "your_app_password"  # Replace with your app password

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, recipient, text)
            speak("Email sent successfully.")
            popup.destroy()  # Close the pop-up window after sending the email
    except smtplib.SMTPAuthenticationError:
        speak("Authentication failed. Check your email and password.")
    except smtplib.SMTPConnectError:
        speak("Failed to connect to the server. Check your network connection.")
    except smtplib.SMTPException as e:
        speak(f"Failed to send email. Error: {str(e)}")
    except Exception as e:
        speak(f"An unexpected error occurred. Error: {str(e)}")

# Function to handle commands
def handle_command(command):
    global searching_wikipedia
    current_time = datetime.datetime.now()
    day = current_time.day
    month = current_time.strftime('%B')

    if 'open google' in command:
        speak("Ok Sir, opening Google")
        webbrowser.open("https://www.google.com")
    elif 'open youtube' in command:
        speak("Ok Sir, opening YouTube")
        webbrowser.open("https://www.youtube.com")
    elif 'open chatgpt' in command or 'open gpt' in command or 'open chat gpt' in command:
        speak("Ok Sir, opening ChatGPT")
        webbrowser.open("https://chat.openai.com/")
    elif 'open github' in command:
        speak("Ok Sir, opening GitHub")
        webbrowser.open("https://github.com/")
    elif 'play music' in command:
        speak("Ok Sir, playing music")
        music_dir = 'C:\\Music'
        songs = os.listdir(music_dir)
        if songs:
            os.startfile(os.path.join(music_dir, songs[0]))
        else:
            speak("No music files found.")
    elif any(phrase in command for phrase in ['how are you', 'are you fine', 'kya haal chal', 'kesa hai', 'kya hal chaal', 'kaisa hai', 'how r u', "kya haal chaal"]):
        speak("I am fine Sir and what about you? By the way, how can I help you?")
    elif 'introduce yourself' in command:
        speak("Hello Sir, I am Garooda, your personal assistant. How can I help you today?")
    elif 'weather' in command:
        get_weather()  # Fetching weather
    elif any(phrase in command for phrase in ['i have a question', 'search wikipedia', 'look up on wikipedia', 'find on wikipedia', 'search for information']):
        if not searching_wikipedia:
            searching_wikipedia = True
            speak("I will continue searching Wikipedia. Please tell me what you want to search.")
        else:
            query = command.replace('search wikipedia for', '').strip()
            search_wikipedia(query)  # Calling Wikipedia search function
    elif 'stop searching' in command:
        searching_wikipedia = False
        speak("I will stop searching Wikipedia now.")
    elif 'send email' in command:
        show_email_popup()  # Showing email popup
    elif any(phrase in command for phrase in ['exit', 'stop', 'bye', 'goodbye']):
        speak("Goodbye Sir")
        exit()
    elif any(phrase in command for phrase in ['thank', 'thanks', 'well done', 'good', 'keep it up', 'excellent', 'outstanding', 'shabash', 'badhiya', 'bahut badhiya']):
        speak("Welcome Sir, I am glad you like it")
    elif any(phrase in command for phrase in ['hello', 'hi', 'hay', 'hey']):
        speak("Hello Sir, How can I help you?")
    elif "time" in command:
        speak(f"The current time is {current_time.hour} hours and {current_time.minute} minutes")
    elif "date" in command:
        speak(f"Today is {day} of {month}, {current_time.year}")
    else:
        speak("Sorry Sir, I can't do that yet.")

# Function to open files, folders, or applications
def open_item(item_name):
    app_paths = {
        'notepad': r"C:\Windows\notepad.exe",
        'calculator': r"C:\Windows\System32\calc.exe",
        'word': 'C:\\Program Files\\Microsoft Office\\root\\Office16\\WINWORD.EXE',
        'excel': 'C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE',
        'powerpoint': 'C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE',
    }

    item_name = item_name.lower()
    if item_name in app_paths:
        subprocess.Popen(app_paths[item_name])
    elif os.path.exists(item_name):
        os.startfile(item_name)
    else:
        speak(f"Sorry, I cannot find the item named {item_name}.")
        print(f"Path {item_name} does not exist.")

# Garuda's introduction with time-based greeting
def introduce_garuda():
    current_hour = datetime.datetime.now().hour
    if 0 <= current_hour < 12:
        greet = "Good morning"
    elif 12 <= current_hour < 18:
        greet = "Good afternoon"
    else:
        greet = "Good evening"
    
    speak(f"{greet} Sir, I am Garooda, your AI assistant. How can I assist you today?")

if __name__ == "__main__":
    introduce_garuda()
    while True:
        command = listen()
        if command:
            handle_command(command)
