import pyttsx3
import tempfile
import os

def tts(text: str):
    engine = pyttsx3.init()
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    engine.save_to_file(text, temp.name)
    engine.runAndWait()
    return temp.name