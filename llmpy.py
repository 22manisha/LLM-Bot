import pyttsx3
import speech_recognition as sr
from gpt4all import GPT4All
import tkinter as tk
from tkinter import messagebox, Label, Button
import cv2
from threading import Thread


# Initialize the speech engine (text to speech)
engine = pyttsx3.init()
engine.setProperty("rate", 150)  # Speed of speech
engine.setProperty("volume", 0.9)  # Volume (0.0 to 1.0)

# Load the GPT4All model
model = GPT4All("Llama-3.2-1B-Instruct-Q4_0.gguf")


# Function to convert text to speech
def text_to_speech(text):
    engine.say(text)
    engine.runAndWait()


# Function to recognize speech and convert it to text
def recognize_speech():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        status_label.config(text="Listening... Speak something.", fg="blue")
        try:
            audio = recognizer.listen(source)
            text = recognizer.recognize_google(audio)  # Use Google Speech Recognition
            print(f"Recognized: {text}")
            status_label.config(text="Speech recognized successfully!", fg="green")
            return text
        except sr.UnknownValueError:
            status_label.config(text="Sorry, I couldn't understand the audio.", fg="red")
            return "Sorry, I couldn't understand the audio."
        except sr.RequestError as e:
            status_label.config(text="Error with the speech recognition service.", fg="red")
            return f"Error: {str(e)}"


# Function to get a response from the GPT4All model
def get_model_response(query):
    try:
        status_label.config(text="Processing your query...", fg="blue")
        with model.chat_session():
            answer = model.generate(query, max_tokens=50)
        status_label.config(text="Response generated successfully!", fg="green")
        return answer
    except Exception as e:
        status_label.config(text="Error generating response.", fg="red")
        return f"Error: {str(e)}"


# Function to handle the "Speak" button action
def start_listening():
    user_input = recognize_speech()
    if user_input:
        response_text = get_model_response(user_input)
        print(f"Bot: {response_text}")
        text_to_speech(response_text)
        # Update the chatbot response in the UI
        chat_history.insert(tk.END, f"User: {user_input}\nBot: {response_text}\n\n")
        chat_history.see(tk.END)


# Function to open the webcam
def open_webcam():
    def show_webcam():
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            messagebox.showerror("Error", "Webcam not detected.")
            return
        while True:
            ret, frame = cap.read()
            if ret:
                cv2.imshow("Webcam (Press 'Q' to close)", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            else:
                break
        cap.release()
        cv2.destroyAllWindows()

    # Run the webcam in a separate thread
    Thread(target=show_webcam).start()


# Function to handle closing the GUI window
def on_close():
    root.quit()


# Create the GUI
def create_gui():
    global root, chat_history, status_label
    root = tk.Tk()
    root.title("Interactive Speech-to-Speech Chatbot")
    root.geometry("500x500")
    root.resizable(False, False)

    # Welcome label
    Label(root, text="Welcome to the Chatbot", font=("Arial", 18, "bold"), fg="darkblue").pack(pady=10)

    # Chat history display
    chat_history = tk.Text(root, wrap=tk.WORD, height=15, width=50, state=tk.NORMAL, bg="#f9f9f9", font=("Arial", 12))
    chat_history.pack(padx=10, pady=5)

    # Status label
    status_label = Label(root, text="Status: Ready", font=("Arial", 12), fg="green")
    status_label.pack(pady=5)

    # Speak button
    Button(
        root, text="Speak", font=("Arial", 14), bg="#4CAF50", fg="white",
        command=lambda: Thread(target=start_listening).start()
    ).pack(pady=10)

    # Webcam button
    Button(
        root, text="Open Webcam", font=("Arial", 14), bg="#2196F3", fg="white",
        command=open_webcam
    ).pack(pady=10)

    # Exit button
    Button(
        root, text="Exit", font=("Arial", 14), bg="#f44336", fg="white",
        command=on_close
    ).pack(pady=10)

    # Handle window close event
    root.protocol("WM_DELETE_WINDOW", on_close)

    root.mainloop()


# Run the GUI
if __name__ == "__main__":
    create_gui()
