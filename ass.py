import speech_recognition as sr
import pyttsx3
import wikipedia
import datetime
import os
import re
import requests
import random
import webbrowser
import pygame  # For music playback
import math
import shutil
from googletrans import Translator  # For language translation
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import time

# Initialize the recognizer and text-to-speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()
translator = Translator()

# Initialize volume control
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, 0, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

# Specify your music folder path
MUSIC_FOLDER = r'C:\Users\vivek\Desktop\projects\voice assistant\music'  # Change this to your music folder path
pygame.mixer.init()

# OpenWeatherMap API key and city
API_KEY = 'cfc02400bdaecbb945953165695b4b90'  # Your API key
CITY = 'Chamarajanagara'  # Your city

songs = []
current_song_index = -1
is_playing = False
is_paused = False
notes = []  # List to store notes

def speak(text):
    engine.say(text)
    engine.runAndWait()

def listen():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            command = recognizer.recognize_google(audio)
            print(f"You said: {command}")
            return command
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service.")
            return None

# Function to load songs from the folder
def load_songs():
    global songs
    if os.path.exists(MUSIC_FOLDER):
        songs = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith(('.mp3', '.wav'))]
    else:
        speak("Music folder not found.")

# Function to play the current song
def play_current_song():
    global is_playing, current_song_index
    if not songs:
        speak("No songs available.")
        return
    
    song_path = os.path.join(MUSIC_FOLDER, songs[current_song_index])
    pygame.mixer.music.load(song_path)
    pygame.mixer.music.play()
    is_playing = True
    speak(f"Playing {songs[current_song_index]}")

# Function to play music
def play_music():
    global current_song_index, is_playing
    if not songs:
        load_songs()
    
    if not songs:
        speak("No music files found in the folder.")
        return
    
    if current_song_index == -1:
        current_song_index = random.randint(0, len(songs) - 1)
    
    play_current_song()

# Function to pause music
def pause_music():
    global is_playing, is_paused
    if is_playing and not is_paused:
        pygame.mixer.music.pause()
        is_paused = True
        speak("Music paused.")
    else:
        speak("No music is currently playing.")

# Function to resume music
def resume_music():
    global is_paused
    if is_paused:
        pygame.mixer.music.unpause()
        is_paused = False
        speak("Music resumed.")
    else:
        speak("Music is not paused.")

# Function to stop music
def stop_music():
    global is_playing, is_paused
    if is_playing:
        pygame.mixer.music.stop()
        is_playing = False
        is_paused = False
        speak("Music stopped.")
    else:
        speak("No music is currently playing.")

# Function to play the next song
def play_next_song():
    global current_song_index, is_playing
    if not songs:
        speak("No songs available.")
        return
    
    current_song_index = (current_song_index + 1) % len(songs)
    play_current_song()

# Function to play the previous song
def play_previous_song():
    global current_song_index, is_playing
    if not songs:
        speak("No songs available.")
        return
    
    current_song_index = (current_song_index - 1) % len(songs)
    play_current_song()

# Define the function to set volume by percentage
def set_volume_by_percent(percent):
    min_volume = volume.GetVolumeRange()[0]  # Usually -65.25 dB
    max_volume = volume.GetVolumeRange()[1]  # 0.0 dB
    volume_level = percent / 100 * (max_volume - min_volume) + min_volume
    volume.SetMasterVolumeLevel(volume_level, None)

# Function to increase volume by a percentage
def increase_volume(percent):
    current_volume = volume.GetMasterVolumeLevel()
    min_volume = volume.GetVolumeRange()[0]
    max_volume = volume.GetVolumeRange()[1]
    
    step = (max_volume - min_volume) * (percent / 100)
    new_volume = min(current_volume + step, max_volume)
    volume.SetMasterVolumeLevel(new_volume, None)
    speak(f"Increased volume by {percent}%")

# Function to decrease volume by a percentage
def decrease_volume(percent):
    current_volume = volume.GetMasterVolumeLevel()
    min_volume = volume.GetVolumeRange()[0]
    max_volume = volume.GetVolumeRange()[1]
    
    step = (max_volume - min_volume) * (percent / 100)
    new_volume = max(current_volume - step, min_volume)
    volume.SetMasterVolumeLevel(new_volume, None)
    speak(f"Decreased volume by {percent}%")

# Define the function to get the weather
def get_weather():
    url = f"http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        main = data['main']
        weather_description = data['weather'][0]['description']
        temperature = main['temp']
        speak(f"The current temperature in {CITY} is {temperature} degrees Celsius with {weather_description}.")
    else:
        speak("I couldn't retrieve the weather information. Please check your city name.")

# Define the function to tell a joke
def tell_joke():
    jokes = [
        "Why don't scientists trust atoms? Because they make up everything!",
        "Why did the scarecrow win an award? Because he was outstanding in his field!",
        "What do you call fake spaghetti? An impasta!",
        "Why did the math book look sad? Because it had too many problems."
    ]
    speak(random.choice(jokes))

# Function to translate text
def translate_text(text, lang):
    translation = translator.translate(text, dest=lang)
    return translation.text

# Function to handle notes
def manage_notes(action, note=None):
    global notes
    if action == "add":
        notes.append(note)
        speak("Note added.")
    elif action == "view":
        if notes:
            speak("Your notes are:")
            for index, note in enumerate(notes):
                speak(f"Note {index + 1}: {note}")
        else:
            speak("You have no notes.")
    elif action == "delete":
        if note in notes:
            notes.remove(note)
            speak("Note deleted.")
        else:
            speak("Note not found.")

# Function to handle user commands
def respond(command):
    command = command.lower()
    
    print(f"Captured command: {command}")  # Debugging print
    
    if 'time' in command:
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        speak(f"The current time is {current_time}")

    elif 'wikipedia' in command:
        query = command.replace("wikipedia", "").strip()
        try:
            results = wikipedia.summary(query, sentences=1)
            speak(results)
        except wikipedia.DisambiguationError as e:
            speak(f"Your query is too ambiguous. Did you mean: {e.options[:3]}?")  # Suggest first 3 options
        except wikipedia.PageError:
            speak("Sorry, I couldn't find any information on that topic.")
        except Exception as e:
            speak("Something went wrong while searching Wikipedia.")

    elif 'open camera' in command:
        os.system("start microsoft.windows.camera:")
        speak("Opening the camera.")

# New commands for opening websites
    elif 'open youtube' in command:
        webbrowser.open('https://www.youtube.com')
        speak("Opening YouTube.")
    
    elif 'open google' in command:
        webbrowser.open('https://www.google.com')
        speak("Opening Google.")
    
    elif 'open instagram' in command:
        webbrowser.open('https://www.instagram.com')
        speak("Opening Instagram.")
    
    elif 'open github' in command:
        webbrowser.open('https://www.github.com')
        speak("Opening GitHub.")

    elif 'weather' in command:
        get_weather()

    elif 'tell me a joke' in command:
        tell_joke()

    elif 'play music' in command:
        play_music()

    elif 'pause music' in command:
        pause_music()

    elif 'resume music' in command:
        resume_music()

    elif 'stop music' in command:
        stop_music()

    elif 'next song' in command:
        play_next_song()

    elif 'previous song' in command:
        play_previous_song()

    elif 'increase volume' in command:
        match = re.search(r'increase volume by (\d+)', command)
        if match:
            percent = int(match.group(1))
            increase_volume(percent)

    elif 'decrease volume' in command:
        match = re.search(r'decrease volume by (\d+)', command)
        if match:
            percent = int(match.group(1))
            decrease_volume(percent)

    elif 'translate' in command:
        match = re.search(r'translate "(.*)" to (\w+)', command)
        if match:
            text_to_translate = match.group(1)
            target_language = match.group(2)
            translated_text = translate_text(text_to_translate, target_language)
            speak(f"The translation is: {translated_text}")

    elif 'add note' in command:
        match = re.search(r'add note "(.*)"', command)
        if match:
            note = match.group(1)
            manage_notes("add", note)

    elif 'view notes' in command:
        manage_notes("view")

    elif 'delete note' in command:
        match = re.search(r'delete note "(.*)"', command)
        if match:
            note = match.group(1)
            manage_notes("delete", note)

    elif 'search the web' in command:
        match = re.search(r'search the web for "(.*)"', command)
        if match:
            query = match.group(1)
            webbrowser.open(f"https://www.google.com/search?q={query}")
            speak(f"Searching the web for {query}")

    elif 'hello' in command:
        speak("Hello! How can I assist you today?")
    
    elif 'bye' in command:
        speak("Goodbye! Have a great day!")
        return False  # Indicate to exit the loop
    
    else:
        speak("I'm sorry, I can't help with that.")
    
    return True  # Continue the loop

def main():
    speak("Hello Vivek and Shabheer, I am Oddy. How may I help you?")
    load_songs()
    
    while True:
        command = listen()
        if command:
            if not respond(command):
                break

if __name__ == "__main__":
    main()
