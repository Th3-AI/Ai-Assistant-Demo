import webbrowser
import speech_recognition as sr
import pyttsx3
from datetime import datetime
import threading
import re
from dynaspark import DynaSpark
from markdown import Markdown

md = Markdown()
client = DynaSpark(api_key="TH3_API_KEY")

def speak(text):
    """Convert text to speech and play it."""
    engine = pyttsx3.init()
    engine.setProperty('rate', 200)
    
    sanitized_text = sanitize_text(text)
    engine.say(sanitized_text)
    engine.runAndWait()

def greeting():
    """Return a greeting based on the current time of day."""
    current_time = datetime.now().hour
    if current_time < 12:
        speak("Good morning, how can I help you?")
    elif current_time < 18:
        speak("Good afternoon, how can I help you?")
    else:
        speak("Good evening, how can I help you?")

recognizer = sr.Recognizer()

# Patterns for command recognition
search_patterns = {
    "youtube": r'\b(youtube|video)\b',
    "google": r'\b(google|search)\b',
    "wikipedia": r'\b(wikipedia|wiki)\b',
    "map": r'\b(map|location)\b',
    "image": r'\b(image|generate|of|design)\b'
}

def get_speech_input():
    """Capture speech input from the microphone and convert it to text."""
    with sr.Microphone() as source:
        print("Listening for your input...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            speak("Sorry, I did not understand that.")
            return None
        except sr.RequestError as e:
            print(f"Sorry, there was an error with the request: {e}")
            speak("Sorry, there was an error with the request.")
            return None

def sanitize_text(text):
    """Remove or replace problematic characters from the text."""
    return text.encode('ascii', 'ignore').decode('ascii')

def search_youtube(query):
    """Search YouTube for the given query and return the URL of the first result."""
    return f"https://www.youtube.com/results?search_query={sanitize_text(query)}"

def search_google(query):
    """Search Google for the given query and return the URL."""
    return f"https://google.com/search?q={sanitize_text(query)}"

def search_wikipedia(query):
    """Search Wikipedia for the given query and return the summary."""
    return f"https://wikipedia.org/wiki/{sanitize_text(query)}"

def search_maps(query):
    """Search Google Maps for the given query and open the location in a browser."""
    search_url = f"https://www.google.com/maps/search/{sanitize_text(query)}"
    webbrowser.open(search_url)

def main_loop():
    """Main loop to continuously get user input and respond."""
    greeting()  # Call the greeting function at the start

    while True:
        user_input = get_speech_input()
        
        if user_input:
            user_input = user_input.strip().lower()

            if "exit" in user_input or "quit" in user_input:
                print("Exiting...")
                speak("Exiting...")
                break

            for command, pattern in search_patterns.items():
                if re.search(pattern, user_input):
                    query = re.sub('|'.join(search_patterns.values()), '', user_input, flags=re.IGNORECASE).strip()
                    
                    if command == "youtube":
                        if query:
                            youtube_url = search_youtube(query)
                            print(f"Opening YouTube search results for: {youtube_url}")
                            webbrowser.open(youtube_url)
                        else:
                            print("No query provided for YouTube search.")
                            speak("No query provided for YouTube search.")

                    elif command == "google":
                        if query:
                            google_url = search_google(query)
                            print(f"Opening Google search results for: {google_url}")
                            webbrowser.open(google_url)
                        else:
                            print("No query provided for Google search.")
                            speak("No query provided for Google search.")

                    elif command == "wikipedia":
                        if query:
                            summary = search_wikipedia(query)
                            print(f"Opening Wikipedia: {summary}")
                            webbrowser.open(summary)
                        else:
                            print("No query provided for Wikipedia search.")
                            speak("No query provided for Wikipedia search.")
                        
                    elif command == "map":
                        if query:
                            search_maps(query)
                            print(f"Opening Google Maps for: {query}")
                        else:
                            print("No location provided for Google Maps.")
                            speak("No location provided for Google Maps.")
                        
                    elif command == "image":
                        # Assuming image generation logic here
                        try:
                            image_url = client.generate_image(prompt=user_input)
                            if image_url:
                                print(f"Image URL: {image_url}")
                                webbrowser.open(image_url)
                            else:
                                print("Failed to generate an image.")
                                speak("Failed to generate an image.")
                        except Exception as e:
                            print(f"Error generating image: {e}")
                            speak("Error generating image.")
                        
                    break
            else:
                # Generate a response using DynaSpark API or similar
                try:
                    response = client.generate_response(user_input)
                    response_text = response.get('response', '').strip()
                    response_text = sanitize_text(response_text)
                    response_text = md.convert(response_text)
                    print(response_text)
                    speak(response_text)
                except Exception as e:
                    print(f"An error occurred while generating the response: {e}")
                    speak("Sorry, I couldn't generate a response.")

        else:
            print("No speech input detected. Please try again.")
            speak("No speech input detected. Please try again.")

# Run the main loop in a separate thread to avoid blocking the main program
thread = threading.Thread(target=main_loop)
thread.start()
