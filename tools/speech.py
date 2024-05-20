from langchain.tools import tool
#from whisperspeech.pipeline import Pipeline
import subprocess
import json 
from openai import OpenAI
import os 

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

with open('config/config.json', 'r') as file:
    config = json.load(file)


'''
@tool("speaker-tool", return_direct=True)
def tts(text):
    """Convert the given query to a speech format

    Args:
        text (_type_): _description_
    """
    pipe = Pipeline(s2a_ref=config['model']['tts_model'])

    audio_file_path = config['file_path']['saved_audio_file']
    print(text)
    pipe.generate_to_file(audio_file_path, text, lang='en', cps=10.5, speaker=config['file_path']['clone_file'])
    subprocess.run(['afplay', audio_file_path]) 
    return "Synthesized"
'''

@tool("speaker-tool", return_direct=True)
def tts(text):
    """Convert the given query to a speech format

    Args:
        text (str): news report text string
    """
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text,
    )

    audio_file_path = config['file_path']['saved_audio_file']
    response.write_to_file(audio_file_path)
    #subprocess.run(['afplay', audio_file_path]) 
    return "Here's final news:"
