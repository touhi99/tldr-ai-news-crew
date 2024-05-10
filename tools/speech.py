from langchain.tools import tool
from whisperspeech.pipeline import Pipeline
import subprocess
pipe = Pipeline(s2a_ref='collabora/whisperspeech:s2a-q4-tiny-en+pl.model')

@tool("speaker-tool", return_direct=True)
def tts(text):
    """Convert the given query to a speech format

    Args:
        text (_type_): _description_
    """

    audio_file_path = "data/audio.mp3"
    print(text)
    pipe.generate_to_file(audio_file_path, text, lang='en', cps=10.5, speaker='data/testvoc.mp3')
    subprocess.run(['afplay', audio_file_path]) 
    return "Synthesized"
