import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading

from assistant import listen, speak
from commands import execute_command

class VoiceAssistantGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Voice Assistant")
        self.root.geometry("700x500")

        self.chat = ScrolledText(root, font=("Arial", 12))
        self.chat.pack(fill="both", expand=True, padx=10, pady=10)

        self.start_btn = tk.Button(
            root,
            text="🎤 Start Listening",
            command=self.start_assistant,
            height=2,
            width=20
        )
        self.start_btn.pack(pady=10)

    def write(self, sender, message):
        self.chat.insert(tk.END, f"{sender}: {message}\n")
        self.chat.see(tk.END)

    def start_assistant(self):
        threading.Thread(target=self.run_assistant, daemon=True).start()

    def run_assistant(self):
        self.write("Assistant", "Hello! How can I help you?")

        while True:
            command = listen()

            if command == "":
                continue

            self.write("You", command)

            response = execute_command(command)

            if response == "exit":
                speak("Goodbye!")
                self.write("Assistant", "Goodbye!")
                break

            speak(response)
            self.write("Assistant", response)

root = tk.Tk()
VoiceAssistantGUI(root)
root.mainloop()