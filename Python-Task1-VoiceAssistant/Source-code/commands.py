import webbrowser
import wikipedia
from datetime import datetime

def execute_command(command):
    command = command.lower()

    if "google" in command:
        webbrowser.open("https://www.google.com")
        return "Opening Google."

    elif "youtube" in command:
        webbrowser.open("https://www.youtube.com")
        return "Opening YouTube."

    elif "github" in command:
        webbrowser.open("https://github.com")
        return "Opening GitHub."

    elif "time" in command:
        return "Current time is " + datetime.now().strftime("%I:%M %p")

    elif "date" in command:
        return "Today's date is " + datetime.now().strftime("%d %B %Y")

    elif "wikipedia" in command:
        topic = command.replace("wikipedia", "").strip()

        if topic == "":
            return "Please tell me what you want to search."

        try:
            result = wikipedia.summary(topic, sentences=2)
            return result
        except:
            return "Sorry, I couldn't find that topic."

    elif "exit" in command:
        return "exit"

    else:
        return "Sorry, I don't know that command yet."