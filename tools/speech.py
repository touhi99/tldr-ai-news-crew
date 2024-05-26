from langchain.tools import tool
#from whisperspeech.pipeline import Pipeline
#import subprocess
#import json 
#from openai import OpenAI
import os 
import requests

XI_API_KEY = os.environ["ELEVEN_LABS_KEY"]



@tool("speaker-tool", return_direct=True)
def tts(text, criteria=None):
    """
    Given the {text} query and IF only provided, get the voice pattern {criteria} dictionary if available keys: (gender/accent/age/use case/description of voice json) and assign the right voice id as speaker. if no pattern providedm
    use the default one. 
    After the found voice id, convert the text to speech. Return an acknowledgement of audio save.
    If no voice pattern matched or found, choose the default voice."""

    CHUNK_SIZE = 1024 
    TEXT_TO_SPEAK = text
    OUTPUT_PATH = "data/output.mp3" 

    voice_data = get_voice()
    try:
        VOICE_ID = match_voice(criteria, voice_data)
        if VOICE_ID is None:
            VOICE_ID = "Qvhoi8X7ZkQS1qSCFt8x"
            raise ValueError("No match found") 
    except Exception as e:
        print(f"Error: {str(e)} - Didn't match, default id")
        VOICE_ID = "Qvhoi8X7ZkQS1qSCFt8x"

    tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}/stream"

    headers = {
        "Accept": "application/json",
        "xi-api-key": XI_API_KEY
    }

    data = {
        "text": TEXT_TO_SPEAK,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.8,
            "style": 0.0,
            "use_speaker_boost": True
        }
    }

    response = requests.post(tts_url, headers=headers, json=data, stream=True)

    if response.ok:
        with open(OUTPUT_PATH, "wb") as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                f.write(chunk)
        print("Audio stream saved successfully.")
    else:
        print(response.text)

def get_voice():
    url = "https://api.elevenlabs.io/v1/voices"
    headers = {
    "Accept": "application/json",
    "xi-api-key": XI_API_KEY,
    "Content-Type": "application/json"
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    return data['voices']

def match_voice(criteria, voice_data):
    index = {}
    for voice in voice_data:
        for key, value in voice['labels'].items():
            if key in criteria:  # Only index based on criteria keys
                if (key, value) not in index:
                    index[(key, value)] = []
                index[(key, value)].append(voice)

    # Find best match
    best_match = None
    best_match_count = 0

    # Iterate over combinations of matching criteria
    for key, value in criteria.items():
        matched_voices = index.get((key, value), [])
        for voice in matched_voices:
            current_match_count = sum(1 for k, v in criteria.items() if voice['labels'].get(k) == v)
            if current_match_count > best_match_count:
                best_match = voice
                best_match_count = current_match_count
            if best_match_count == len(criteria):
                break

    if best_match:
        print(f"Best match: {best_match['name']} with ID {best_match['voice_id']}")
        return best_match['voice_id']
    else:
        print("No suitable match found.")
        return None
    

# client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# with open('config/config.json', 'r') as file:
#     config = json.load(file)

#OLD offline TTS
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

#old OpenAI TTS 
# @tool("speaker-tool", return_direct=True)
# def tts(text):
#     """Convert the given query to a speech format

#     Args:
#         text (str): news report text string
#     """
#     response = client.audio.speech.create(
#         model="tts-1",
#         voice="nova",
#         input=text,
#     )

#     audio_file_path = config['file_path']['saved_audio_file']
#     response.write_to_file(audio_file_path)
#     #subprocess.run(['afplay', audio_file_path]) 
#     return "Here's final news:"
