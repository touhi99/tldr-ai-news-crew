from dotenv import load_dotenv
load_dotenv()
from crew import TLDRNewsCrew
import re 
import streamlit as st 
st.set_page_config(layout="wide")
import json
import time
import sys 
from util import *
from audiorecorder import audiorecorder
from tools.voice import save_audio_file

with open('config/config.json', 'r') as file:
    config = json.load(file)

if 'recording_started' not in st.session_state:
    st.session_state.recording_started = False
if 'recording_finished' not in st.session_state:
    st.session_state.recording_finished = False
if 'audio_data' not in st.session_state:
    st.session_state.audio_data = None
if 'run_clicked' not in st.session_state:
    st.session_state.run_clicked = False
if 'crew_result' not in st.session_state:
    st.session_state.crew_result = None
if 'messages' not in st.session_state:
    st.session_state.messages = []

def run_crew(crawling_date, run_speech):
    inputs = { 
        'date' : crawling_date, #'YYYY-MM-DD',
    }
    print(run_speech)
    speech_agent = run_speech
    return TLDRNewsCrew().crew(speech_agent).kickoff(inputs=inputs)

class StreamToExpander:
    def __init__(self, expander):
        self.expander = expander
        self.buffer = []
        self.colors = ['red', 'green', 'blue', 'orange'] 
        self.color_index = 0  

    def write(self, data):
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)

        task_match_object = re.search(r'\"task\"\s*:\s*\"(.*?)\"', cleaned_data, re.IGNORECASE)
        task_match_input = re.search(r'task\s*:\s*([^\n]*)', cleaned_data, re.IGNORECASE)
        task_value = None
        if task_match_object:
            task_value = task_match_object.group(1)
        elif task_match_input:
            task_value = task_match_input.group(1).strip()

        if task_value:
            st.toast(":robot_face: " + task_value)

        if "Entering new CrewAgentExecutor chain" in cleaned_data:
            self.color_index = (self.color_index + 1) % len(self.colors)  

            cleaned_data = cleaned_data.replace("Entering new CrewAgentExecutor chain", f":{self.colors[self.color_index]}[Entering new CrewAgentExecutor chain]")

        if "Data crawler" in cleaned_data:
            cleaned_data = cleaned_data.replace("Data crawler", f":{self.colors[self.color_index]}[Data crawler]")
        if "data engineer" in cleaned_data:
            cleaned_data = cleaned_data.replace("data engineer", f":{self.colors[self.color_index]}[data engineer]")
        if "data_analyst" in cleaned_data:
            cleaned_data = cleaned_data.replace("data_analyst", f":{self.colors[self.color_index]}[data_analyst]")
        if "speaker agent" in cleaned_data:
            cleaned_data = cleaned_data.replace("speaker agent", f":{self.colors[self.color_index]}[speaker agent]")
        if "Finished chain." in cleaned_data:
            cleaned_data = cleaned_data.replace("Finished chain.", f":{self.colors[self.color_index]}[Finished chain.]")

        self.buffer.append(cleaned_data)
        if "\n" in data:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer = []


# Streamlit interface
def run_crewai_app():
    st.title("TLDR news crew")
    # with st.expander("About the Team:"):
    #     st.subheader("Diagram")
    #     left_co, cent_co,last_co = st.columns(3)
    
    # Date selection setup
    date_option = st.radio("Choose the type of date input:", ["Single Date", "Date Range"])
    if date_option == "Single Date":
        selected_date = st.date_input("Select a Date for Analysis", format='YYYY-MM-DD')
        if is_weekday(selected_date):
            date_to_use = [str(selected_date)]
        else:
            st.error("Please select a weekday.")
            date_to_use = None
    elif date_option == "Date Range":
        date_range = st.date_input("Select Date Range for Analysis", [], format='YYYY-MM-DD')
        if len(date_range) == 2:
            start_date, end_date = date_range
            if is_weekday(start_date) and is_weekday(end_date):
                date_to_use = [d.strftime('%Y-%m-%d') for d in pd.date_range(start_date, end_date) if is_weekday(d)]
            else:
                st.error("Both start and end dates must be weekdays.")
                date_to_use = None
        else:
            st.error("Please select a complete date range.")
            date_to_use = None

    run_speech = st.checkbox("Listen news")

    if st.button("Run Analysis", key='run_analysis'):
        st.session_state.run_clicked = True
        stopwatch_placeholder = st.empty()
        start_time = time.time()

        with st.expander("Fetching...", expanded=True):
            sys.stdout = StreamToExpander(st)
            with st.spinner("Generating Results"):
                crew_result = run_crew(date_to_use, run_speech)
                st.session_state.crew_result = crew_result

        end_time = time.time()
        total_time = end_time - start_time
        stopwatch_placeholder.text(f"Total Time Elapsed: {total_time:.2f} seconds")

    if st.session_state.run_clicked:
        if 'crew_result' in st.session_state:
            st.write("Crew Result:", st.session_state.crew_result)
            c = st.container()
            with c:
                if not st.session_state.recording_started:
                    st.write("Please start recording...")
                    audio = audiorecorder("Click to record", "Click to stop recording", key="audio_recorder")
                    if audio:
                        st.session_state.recording_started = True
                        st.session_state.audio_data = audio
                elif not st.session_state.recording_finished:
                    st.write("Recording complete, checking audio...")
                    if st.session_state.audio_data and len(st.session_state.audio_data) > 0:
                        st.session_state.recording_finished = True
                        audio_file = "data/recorded_audio.wav"
                        st.session_state.audio_data.export(audio_file, format="wav")
                        st.audio(audio_file, format='audio/wav')
                        st.write("Audio saved and processed.")
                        handle_chat_input(audio_file, "2024-05-24")

                if st.session_state.audio_data:
                    st.write(f"Stored Audio Length: {len(st.session_state.audio_data)} milliseconds")
                else:
                    st.write("No audio data stored in session.")

        for message in st.session_state.messages:
            st.text(message)

def handle_chat_input(audio_file, date_to_use):
    if audio_file:
        st.session_state.messages.append(f"You:")
        response_text = "System: Processing your request..."
        st.session_state.messages.append(response_text)
        response_audio = TLDRNewsCrew().crew(qa_agent_bool=True).kickoff(inputs={"audio": audio_file, "date": date_to_use})
        play_audio(response_audio)


def play_audio(audio_data):
    """ Play audio response """
    st.audio(audio_data, format='audio/mp3')
    
if __name__ == "__main__":
    run_crewai_app()    