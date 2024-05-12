from langchain.tools import tool
from whisperspeech.pipeline import Pipeline
import subprocess
import json 

with open('config/config.json', 'r') as file:
    config = json.load(file)

pipe = Pipeline(s2a_ref=config['model']['tts_model'])

@tool("speaker-tool", return_direct=True)
def tts(text):
    """Convert the given query to a speech format

    Args:
        text (_type_): _description_
    """

    audio_file_path = config['file_path']['saved_audio_file']
    print(text)
    pipe.generate_to_file(audio_file_path, text, lang='en', cps=10.5, speaker=config['file_path']['clone_file'])
    subprocess.run(['afplay', audio_file_path]) 
    return "Synthesized"
