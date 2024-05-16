from dotenv import load_dotenv
load_dotenv()
from crew import TLDRNewsCrew
import re 
import streamlit as st 
st.set_page_config(layout="wide")

import time
import sys 


task_values = []

def run_crew(crawling_date, run_speech):
    inputs = { 
        'date' : crawling_date, #'2024-05-03',
    }
    print(run_speech)
    speech_agent = run_speech
    return TLDRNewsCrew().crew(speech_agent).kickoff(inputs=inputs)

#display the console processing on streamlit UI
class StreamToExpander:
    def __init__(self, expander):
        self.expander = expander
        self.buffer = []
        self.colors = ['red', 'green', 'blue', 'orange'] 
        self.color_index = 0  

    def write(self, data):
        cleaned_data = re.sub(r'\x1B\[[0-9;]*[mK]', '', data)

        # Check if the data contains 'task' information
        task_match_object = re.search(r'\"task\"\s*:\s*\"(.*?)\"', cleaned_data, re.IGNORECASE)
        task_match_input = re.search(r'task\s*:\s*([^\n]*)', cleaned_data, re.IGNORECASE)
        task_value = None
        if task_match_object:
            task_value = task_match_object.group(1)
        elif task_match_input:
            task_value = task_match_input.group(1).strip()

        if task_value:
            st.toast(":robot_face: " + task_value)

        # Check if the text contains the specified phrase and apply color
        if "Entering new CrewAgentExecutor chain" in cleaned_data:
            # Apply different color and switch color index
            self.color_index = (self.color_index + 1) % len(self.colors)  # Increment color index and wrap around if necessary

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
    
    crawling_date = st.text_input("Enter a date")
    run_speech = st.checkbox("Listen news")

    if st.button("Run Analysis"):
        # Placeholder for stopwatch
        stopwatch_placeholder = st.empty()
        
        # Start the stopwatch
        start_time = time.time()
        with st.expander("Processing!", expanded=True):
            sys.stdout = StreamToExpander(st)
            with st.spinner("Generating Results"):
                crew_result = run_crew(crawling_date, run_speech)

        # Stop the stopwatch
        end_time = time.time()
        total_time = end_time - start_time
        stopwatch_placeholder.text(f"Total Time Elapsed: {total_time:.2f} seconds")

        st.header("Results:")
        st.markdown(crew_result)

if __name__ == "__main__":
    run_crewai_app()    