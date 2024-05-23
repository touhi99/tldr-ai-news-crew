from dotenv import load_dotenv
load_dotenv()
from crew import TLDRNewsCrew
import re 
import streamlit as st 
st.set_page_config(layout="wide")
import json
import time
import sys 

with open('config/config.json', 'r') as file:
    config = json.load(file)

if 'run_clicked' not in st.session_state:
    st.session_state.run_clicked = False
if 'messages' not in st.session_state:
    st.session_state.messages = []

def run_crew(crawling_date, run_speech):
    inputs = { 
        'date' : crawling_date, #'2024-05-03',
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
    with st.expander("About the Team:"):
        st.subheader("Diagram")
        left_co, cent_co,last_co = st.columns(3)
    
    # Date selection setup
    date_option = st.radio("Choose the type of date input:", ["Single Date", "Date Range"])
    if date_option == "Single Date":
        date_to_use = st.date_input("Select a Date for Analysis", format='YYYY-MM-DD')
    elif date_option == "Date Range":
        date_range = st.date_input("Select Date Range for Analysis", [], format='YYYY-MM-DD')
        if len(date_range) == 2:
            start_date, end_date = date_range
            date_to_use = (start_date, end_date)
        else:
            st.error("Please select a complete date range.")
            date_to_use = None

    #crawling_date = st.text_input("Enter a date")
    run_speech = st.checkbox("Listen news")

    if st.button("Run Analysis", key='run_analysis'):
        st.session_state.run_clicked = True
        stopwatch_placeholder = st.empty()
        start_time = time.time()

        with st.expander("Fetching...", expanded=True):
            sys.stdout = StreamToExpander(st)
            with st.spinner("Generating Results"):
                crew_result = run_crew(date_to_use, run_speech)

        # Stop the stopwatch
        end_time = time.time()
        total_time = end_time - start_time
        stopwatch_placeholder.text(f"Total Time Elapsed: {total_time:.2f} seconds")

        st.header("Results:")
        if run_speech:
            audio_file = config['file_path']['saved_audio_file']
            st.markdown(crew_result)
            st.audio(audio_file, format='audio/mp3', start_time=0)
        else:
            st.markdown(crew_result)

    if st.session_state.run_clicked:
        chat_input = st.text_input("Chat with system", key="chat_input", value="")
        send_button = st.button("Send", key="send_chat")
        if send_button:
            handle_chat_input(date_to_use)
        for message in st.session_state.messages:
            st.text(message)

def handle_chat_input(date_to_use):
    user_input = st.session_state.chat_input.strip()
    #print(user_input)
    if user_input:
        st.session_state.messages.append(f"You: {user_input}")
        st.session_state.messages.append("System: Analysis received, processing...")
        st.session_state.messages.append(TLDRNewsCrew().crew(qa_agent_bool=True).kickoff(inputs={"query": user_input, "date": date_to_use}))
        #st.session_state.chat_input = ""

if __name__ == "__main__":
    run_crewai_app()    