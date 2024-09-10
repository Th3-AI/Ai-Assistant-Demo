import webbrowser
import speech_recognition as sr # type: ignore
from dynaspark import DynaSpark
import pyttsx3 # type: ignore
from datetime import datetime
import threading

def speak(text):
    """Convert text to speech and play it."""
    engine = pyttsx3.init()
    engine.setProperty('rate', 200)
    
    # Sanitize the text before speaking
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

# Initialize the DynaSpark API client
client = DynaSpark(api_key="TH3_API_KEY")

# Initialize the speech recognizer
recognizer = sr.Recognizer()

def get_speech_input():
    """Capture speech input from the microphone and convert it to text."""
    with sr.Microphone() as source:
        print("Listening for your input...")
        audio = recognizer.listen(source)
        try:
            # Recognize speech using Google Web Speech API
            text = recognizer.recognize_google(audio)
            print(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print("Sorry, I did not understand that.")
            return None
        except sr.RequestError as e:
            print(f"Sorry, there was an error with the request: {e}")
            return None

def sanitize_text(text):
    """Remove or replace problematic characters from the text."""
    try:
        return text.encode('ascii', 'ignore').decode('ascii')
    except UnicodeEncodeError:
        return text

def main_loop():
    """Main loop to continuously get user input and respond."""
    greeting()  # Call the greeting function at the start

    while True:
        user_input = get_speech_input()
        
        if user_input:
            user_input = user_input.strip()
            if not user_input:
                print("Empty input received. Please try again.")
                continue

            # Check for specific commands
            if "image" in user_input.lower() or "design" in user_input.lower():
                # Generate an image
                try:
                    image_url = client.generate_image(prompt=user_input)
                    if image_url:
                        print(f"Image URL: {image_url}")
                        # Open the image URL in the default web browser
                        webbrowser.open(image_url)
                    else:
                        print("Failed to generate an image.")
                except Exception as e:
                    print(f"Error generating image: {e}")
            else:
                # Generate a response
                try:
                    response = client.generate_response(user_input)
                    response_text = response.get('response', '').strip()
                    response_text = sanitize_text(response_text)
                    print(response_text)
                    speak(response_text)  # Speak the response
                except Exception as e:
                    print(f"An error occurred while generating the response: {e}")
                    response_text = "Sorry, I couldn't generate a response."

            # Check for exit command
            if user_input.lower() in ["exit", "quit"]:
                print("Exiting...")
                break
        else:
            print("No speech input detected. Please try again.")

# Run the main loop in a separate thread to avoid blocking the main program
thread = threading.Thread(target=main_loop)
thread.start()
