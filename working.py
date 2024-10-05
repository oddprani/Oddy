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
from googletrans import Translator  # For language translation
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

class VoiceAssistant:
    def __init__(self):
        # Initialize the recognizer and text-to-speech engine
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()
        self.translator = Translator()

        # Initialize volume control
        self.devices = AudioUtilities.GetSpeakers()
        self.interface = self.devices.Activate(IAudioEndpointVolume._iid_, 0, None)
        self.volume = self.interface.QueryInterface(IAudioEndpointVolume)

        # Specify your music folder path
        self.music_folder = r'C:\Users\vivek\Desktop\projects\voice assistant\music'  # Change this to your music folder path
        pygame.mixer.init()
        
        self.songs = []
        self.current_song_index = -1
        self.is_playing = False
        self.is_paused = False
        self.notes = []  # List to store notes
        self.API_KEY = 'cfc02400bdaecbb945953165695b4b90'  # Your API key
        self.CITY = 'Chamarajanagara'  # Your city
        
    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self):
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
            try:
                command = self.recognizer.recognize_google(audio)
                print(f"You said: {command}")
                return command.lower()
            except sr.UnknownValueError:
                print("Sorry, I did not understand that.")
                return None
            except sr.RequestError:
                print("Could not request results from Google Speech Recognition service.")
                return None

    def load_songs(self):
        if os.path.exists(self.music_folder):
            self.songs = [f for f in os.listdir(self.music_folder) if f.endswith(('.mp3', '.wav'))]
        else:
            self.speak("Music folder not found.")

    def play_music(self):
        if not self.songs:
            self.load_songs()

        if not self.songs:
            self.speak("No music files found in the folder.")
            return

        if self.current_song_index == -1:
            self.current_song_index = random.randint(0, len(self.songs) - 1)

        self.play_current_song()

    def play_current_song(self):
        if not self.songs:
            self.speak("No songs available.")
            return

        song_path = os.path.join(self.music_folder, self.songs[self.current_song_index])
        pygame.mixer.music.load(song_path)
        pygame.mixer.music.play()
        self.is_playing = True
        self.speak(f"Playing {self.songs[self.current_song_index]}")

    def pause_music(self):
        if self.is_playing and not self.is_paused:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.speak("Music paused.")
        else:
            self.speak("No music is currently playing.")

    def resume_music(self):
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.speak("Music resumed.")
        else:
            self.speak("Music is not paused.")

    def stop_music(self):
        if self.is_playing:
            pygame.mixer.music.stop()
            self.is_playing = False
            self.is_paused = False
            self.speak("Music stopped.")
        else:
            self.speak("No music is currently playing.")

    def set_volume_by_percent(self, percent):
        min_volume = self.volume.GetVolumeRange()[0]  # Usually -65.25 dB
        max_volume = self.volume.GetVolumeRange()[1]  # 0.0 dB
        volume_level = percent / 100 * (max_volume - min_volume) + min_volume
        self.volume.SetMasterVolumeLevel(volume_level, None)

    def adjust_volume(self, percent, increase=True):
        current_volume = self.volume.GetMasterVolumeLevel()
        min_volume = self.volume.GetVolumeRange()[0]
        max_volume = self.volume.GetVolumeRange()[1]
        step = (max_volume - min_volume) * (percent / 100)
        new_volume = min(current_volume + step, max_volume) if increase else max(current_volume - step, min_volume)
        self.volume.SetMasterVolumeLevel(new_volume, None)
        action = "increased" if increase else "decreased"
        self.speak(f"{action.capitalize()} volume by {percent}%")

    def get_weather(self):
        url = f"http://api.openweathermap.org/data/2.5/weather?q={self.CITY}&appid={self.API_KEY}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            main = data['main']
            weather_description = data['weather'][0]['description']
            temperature = main['temp']
            self.speak(f"The current temperature in {self.CITY} is {temperature} degrees Celsius with {weather_description}.")
        else:
            self.speak("I couldn't retrieve the weather information. Please check your city name.")

    def tell_joke(self):
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? Because he was outstanding in his field!",
            "What do you call fake spaghetti? An impasta!",
            "Why did the math book look sad? Because it had too many problems."
        ]
        self.speak(random.choice(jokes))

    def translate_text(self, text, lang):
        translation = self.translator.translate(text, dest=lang)
        return translation.text

    def manage_notes(self, action, note=None):
        if action == "add":
            self.notes.append(note)
            self.speak("Note added.")
        elif action == "view":
            if self.notes:
                self.speak("Your notes are:")
                for index, note in enumerate(self.notes):
                    self.speak(f"Note {index + 1}: {note}")
            else:
                self.speak("You have no notes.")
        elif action == "delete":
            if note in self.notes:
                self.notes.remove(note)
                self.speak("Note deleted.")
            else:
                self.speak("Note not found.")

    def respond(self, command):
        print(f"Captured command: {command}")  # Debugging print

        if 'time' in command:
            current_time = datetime.datetime.now().strftime("%H:%M")
            self.speak(f"The current time is {current_time}")
        
        elif 'wikipedia' in command:
            query = command.replace("wikipedia", "").strip()
            try:
                results = wikipedia.summary(query, sentences=1)
                self.speak(results)
            except wikipedia.DisambiguationError as e:
                self.speak(f"Your query is too ambiguous. Did you mean: {e.options[:3]}?")
            except wikipedia.PageError:
                self.speak("Sorry, I couldn't find any information on that topic.")
            except Exception:
                self.speak("Something went wrong while searching Wikipedia.")
        
        elif 'open' in command:
            self.open_application(command)
        
        elif 'weather' in command:
            self.get_weather()
        
        elif 'tell me a joke' in command:
            self.tell_joke()
        
        elif 'play music' in command:
            self.play_music()
        
        elif 'pause music' in command:
            self.pause_music()
        
        elif 'resume music' in command:
            self.resume_music()
        
        elif 'stop music' in command:
            self.stop_music()
        
        elif 'next song' in command:
            self.current_song_index = (self.current_song_index + 1) % len(self.songs)
            self.play_current_song()
        
        elif 'previous song' in command:
            self.current_song_index = (self.current_song_index - 1) % len(self.songs)
            self.play_current_song()
        
        elif 'increase volume' in command:
            match = re.search(r'increase volume by (\d+)', command)
            if match:
                percent = int(match.group(1))
                self.adjust_volume(percent, increase=True)

        elif 'decrease volume' in command:
            match = re.search(r'decrease volume by (\d+)', command)
            if match:
                percent = int(match.group(1))
                self.adjust_volume(percent, increase=False)
        
        elif 'translate' in command:
            match = re.search(r'translate "(.*)" to (\w+)', command)
            if match:
                text_to_translate = match.group(1)
                target_language = match.group(2)
                translated_text = self.translate_text(text_to_translate, target_language)
                self.speak(f"The translation is: {translated_text}")
        
        elif 'add note' in command:
            match = re.search(r'add note "(.*)"', command)
            if match:
                note = match.group(1)
                self.manage_notes("add", note)

        elif 'view notes' in command:
            self.manage_notes("view")

        elif 'delete note' in command:
            match = re.search(r'delete note "(.*)"', command)
            if match:
                note = match.group(1)
                self.manage_notes("delete", note)

        elif 'search the web' in command:
            match = re.search(r'search the web for "(.*)"', command)
            if match:
                query = match.group(1)
                webbrowser.open(f"https://www.google.com/search?q={query}")
                self.speak(f"Searching the web for {query}")
        
        elif 'hello' in command:
            self.speak("Hello! How can I assist you today?")
        
        elif 'bye' in command:
            self.speak("Goodbye! Have a great day!")
            return False  # Indicate to exit the loop
        
        else:
            self.speak("I'm sorry, I can't help with that.")
        
        return True  # Continue the loop

    def open_application(self, command):
        applications = {
            'camera': "start microsoft.windows.camera:",
            'youtube': 'https://www.youtube.com',
            'this pc': 'explorer shell:MyComputerFolder',
            'google': 'https://www.google.com',
            'instagram': 'https://www.instagram.com',
            'github': 'https://www.github.com'
        }
        for app, url in applications.items():
            if app in command:
                if app == 'camera':
                    os.system(url)
                    self.speak("Opening the camera.")
                else:
                    webbrowser.open(url)
                    self.speak(f"Opening {app.capitalize()}.")
                break

    def main(self):
        self.speak("Hello Vivek and Shabheer, I am Oddy. How may I help you?")
        self.load_songs()

        while True:
            command = self.listen()
            if command:
                if not self.respond(command):
                    break

if __name__ == "__main__":
    assistant = VoiceAssistant()
    assistant.main()
