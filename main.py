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
if 'analysis' not in st.session_state:
    st.session_state.analysis = None
if 'qa_agent_bool' not in st.session_state:
    st.session_state.qa_agent_bool = None

def run_crew(crawling_date, query=None, audio=None, run_analysis=None, qa_agent_bool=None, speech_bool=None):
    inputs = { 
        'date' : crawling_date,
        'query': query,
        'audio': audio
    }
    return TLDRNewsCrew().crew(run_analysis_bool=run_analysis, 
                               qa_agent_bool=qa_agent_bool,
                               speech_bool=speech_bool).kickoff(inputs=inputs)

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
        if "Voice agent" in cleaned_data:
            cleaned_data = cleaned_data.replace("Voice agent", f":{self.colors[self.color_index]}[Voice agent]")
        if "speaker agent" in cleaned_data:
            cleaned_data = cleaned_data.replace("speaker agent", f":{self.colors[self.color_index]}[speaker agent]")
        if "Q&A support agent" in cleaned_data:
            cleaned_data = cleaned_data.replace("Q&A support agent", f":{self.colors[self.color_index]}[Q&A support agent]")
        if "Finished chain." in cleaned_data:
            cleaned_data = cleaned_data.replace("Finished chain.", f":{self.colors[self.color_index]}[Finished chain.]")

        self.buffer.append(cleaned_data)
        if "\n" in data:
            self.expander.markdown(''.join(self.buffer), unsafe_allow_html=True)
            self.buffer = []


# Streamlit interface
def run_crewai_app():
    st.title("TLDR AI News Crew")
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

    run_speech = st.checkbox("Use Voice Agent")

    if st.button("Run Analysis", key='run_analysis'):
        st.session_state.recording_started = False
        st.session_state.recording_finished = False
        st.session_state.messages = []
        st.session_state.analysis = True
        st.session_state.qa_agent_bool = False
        stopwatch_placeholder = st.empty()
        start_time = time.time()

        with st.expander("Fetching...", expanded=False):
            #sys.stdout = StreamToExpander(st)
            with st.spinner("Generating Results"):
                crew_result = run_crew(date_to_use, run_analysis=st.session_state.analysis, qa_agent_bool=st.session_state.qa_agent_bool, speech_bool=run_speech)
                st.session_state.crew_result = crew_result
                st.session_state.run_clicked = True
                st.session_state.qa_agent_bool = True

        end_time = time.time()
        total_time = end_time - start_time
        stopwatch_placeholder.text(f"Total Time Elapsed: {total_time:.2f} seconds")

    if 'run_clicked' in st.session_state and st.session_state.run_clicked:
        st.write("Crew Result:", st.session_state.get('crew_result', 'No result yet'))
        if run_speech:
            if st.button("Record New Message"):
                st.session_state.recording_started = False
                st.session_state.recording_finished = False
                st.experimental_rerun()  

            c = st.container()
            with c:
                if not st.session_state.recording_started and not st.session_state.recording_finished:
                    st.write("Please start recording...")
                    audio = audiorecorder("Click to record", "Click to stop recording", key="audio_recorder")
                    if audio:
                        st.session_state.audio_data = audio
                        st.session_state.recording_started = True

                elif st.session_state.recording_started and not st.session_state.recording_finished:
                    st.write("Recording complete, checking audio...")
                    if st.session_state.audio_data:
                        audio_file = save_audio_file(st.session_state.audio_data)
                        play_audio(audio_file, format='audio/wav')
                        st.write("Audio saved and processed.")
                        handle_chat_input(date_to_use, audio_file=audio_file, qa_agent_bool=st.session_state.qa_agent_bool, run_speech=run_speech)
                        st.session_state.recording_finished = True
        else:
            # Generate a unique key every run to ensure the input field is always reset
            session_key = "user_text_input_" + str(st.session_state.get("input_reset_counter", 0))
            user_text = st.text_input("Enter your message:", key=session_key)

            if st.button("Send"):
                if user_text:
                    handle_chat_input(date_to_use, query=user_text, qa_agent_bool=st.session_state.qa_agent_bool, run_speech=run_speech)
                    st.session_state.messages.append(f"You: {user_text}")
                    # Increment the counter to reset the input field
                    st.session_state.input_reset_counter = st.session_state.get("input_reset_counter", 0) + 1
                    st.experimental_rerun()  # Optional: Only if necessary to refresh other parts of the UI
                else:
                    st.error("Please enter a message to send.")

        for message in st.session_state.get('messages', []):
            if message.startswith("You:"):
                user_message = st.chat_message("user")
                user_message.write(message.replace("You:", ""))
            else:
                assistant_message = st.chat_message("assistant")
                assistant_message.write(message.replace("System:", ""))


def handle_chat_input(date_to_use, audio_file=None, query=None, qa_agent_bool=None, run_speech=None):
    if audio_file:
        st.session_state.messages.append(f"You:")
        st.session_state.messages.append("System: Processing your request...")
        with st.expander("Fetching answer...", expanded=False):
            with st.spinner("Generating Results"):
                #response_json = TLDRNewsCrew().crew(qa_agent_bool=True).kickoff(inputs={"audio": audio_file, "date": date_to_use})
                response_json = run_crew(date_to_use, audio=audio_file, run_analysis=st.session_state.analysis, qa_agent_bool=qa_agent_bool, speech_bool=run_speech)

            if isinstance(response_json, str):
                response_data = json.loads(response_json)
            else:
                response_data = response_json

            if response_data['success']:
                output_path = response_data['output_path']
                text_to_speak = response_data['text_to_speak']
                st.session_state.messages.append(f"System: {text_to_speak}") 
                play_audio(output_path) 
            else:
                error_message = response_data['text_to_speak']
                st.session_state.messages.append(f"System Error: {error_message}")
                st.error(f"Failed to process audio: {error_message}")
            st.session_state.recording_started = False
            st.session_state.recording_finished = False
            st.session_state.audio_data = None        
    elif query:
        st.session_state.messages.append("You:")
        st.session_state.messages.append("System: Processing your request...")
        with st.expander("Fetching answer...", expanded=False):
            with st.spinner("Generating Results"):
                response_text = run_crew(date_to_use, query=query, run_analysis=st.session_state.analysis, qa_agent_bool=qa_agent_bool, speech_bool=run_speech)
                st.session_state.messages.append(f"System: {response_text}")

def play_audio(audio_data, format='audio/mp3'):
    st.audio(audio_data, format)
    
if __name__ == "__main__":
    run_crewai_app()    