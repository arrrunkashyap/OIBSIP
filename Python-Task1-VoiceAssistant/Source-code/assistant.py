import pyttsx3
import speech_recognition as sr

engine = pyttsx3.init()

def speak(text):
    print("Assistant:", text)
    engine.say(text)
    engine.runAndWait()

def listen():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    try:
        command = recognizer.recognize_google(audio)
        print("You:", command)
        return command.lower()
    except Exception:
        return ""

if __name__ == "__main__":
    speak("Hello! I am your Voice Assistant.")

    while True:
        command = listen()

        if command == "":
            speak("Sorry, I didn't understand.")
            continue

        response = execute_command(command)

        if response == "exit":
            speak("Goodbye!")
            break

        speak(response)