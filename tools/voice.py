from langchain.tools import tool
#import json 
import os 
import requests
from openai import OpenAI
client = OpenAI()
import datetime


@tool("voice-tool", return_direct=True)
def transcribe(audio_file):
    """Given audio file path transcribe the text that returns the user query in text format. If only filename is provided,
    try data/ folder.

    Args:
        audio_file (str): audio file path
    """
    audio_file= open(audio_file, "rb")
    transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file
    )
    return transcription.text


def save_audio_file(audio_bytes):
    audio_file = "data/recorded_audio.wav"
    audio_bytes.export(audio_file, format="wav")
    return audio_file

def transcribe_audio(file_path):
    with open(file_path, "rb") as audio_file:
        transcript = transcribe(audio_file)
    return transcript["text"]