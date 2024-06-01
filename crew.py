from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from llms import load_llm
from tools.crawler import crawler_tool
from tools.vectordb import embed_news_for_dates
from tools.speech import tts
from tools.qa import get_qa, get_qa_text
from tools.voice import transcribe
@CrewBase
class TLDRNewsCrew:
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self) -> None:
        self.local_llm = load_llm('local')
        self.groq_llm = load_llm("groq")
        self.openai_llm = load_llm("openai")
    
    @agent
    def news_fetcher_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['data_crawler'],
            llm = self.openai_llm, #self.groq_llm,
            tools = [crawler_tool]
        )
    
    @agent
    def data_engineer_agent(self) -> Agent:
        return Agent(
            config = self.agents_config['data_engineer'],
            llm = self.openai_llm, #self.groq_llm,
            tools = [embed_news_for_dates]
        )
    
    @agent
    def speaker_agent(self) -> Agent:
        return Agent(
            config = self.agents_config['speaker_agent'],
            llm = self.openai_llm,
            tools = [tts]
        )
    
    @agent
    def voice_agent(self) -> Agent:
        return Agent(
            config = self.agents_config['voice_agent'],
            llm = self.openai_llm, #self.groq_llm,
            tools = [transcribe]
        )
    
    @agent
    def qa_agent(self) -> Agent:
        return Agent(
            config = self.agents_config['news_qa_support_agent'],
            llm = self.openai_llm,
            tools = [get_qa]
        )

    @agent
    def text_qa_agent(self) -> Agent:
        return Agent(
            config = self.agents_config['text_qa_agent'],
            llm = self.openai_llm,
            tools = [get_qa_text]
        )
    
    @task
    def data_crawler_task(self) -> Task:
        return Task(
            config = self.tasks_config['data_crawler_task'],
            agent = self.news_fetcher_agent()
        )

    @task
    def data_engineer_task(self) -> Task:
        return Task(
            config = self.tasks_config['data_engineer_task'],
            agent = self.data_engineer_agent()
        )
    
    @task
    def speaker_task(self) -> Task:
        return Task(
            config = self.tasks_config['speaker_task'],
            agent = self.speaker_agent()
        ) 
    
    @task
    def qa_agent_task(self) -> Task:
        return Task(
            config = self.tasks_config['news_qa_support_task'],
            agent = self.qa_agent()
        )
    
    @task
    def text_qa_agent_task(self) -> Task:
        return Task(
            config = self.tasks_config['text_qa_task'],
            agent = self.text_qa_agent()
        )
    
    @task
    def voice_agent_task(self) -> Task:
        return Task(
            config = self.tasks_config['voice_agent_task'],
            agent = self.voice_agent()
        )
    
    @crew
    def crew(self, qa_agent_bool=None, run_analysis_bool=True, speech_bool=None) -> Crew:
        "Create the TLDR News Crew"
        if run_analysis_bool and not qa_agent_bool:
            self.agents = [self.news_fetcher_agent(), self.data_engineer_agent()]
            self.tasks = [self.data_crawler_task(), self.data_engineer_task()]
        elif run_analysis_bool and qa_agent_bool and speech_bool:
            self.agents = [self.voice_agent(), self.qa_agent(), self.speaker_agent()]
            self.tasks = [self.voice_agent_task(), self.qa_agent_task(), self.speaker_task()]
        elif run_analysis_bool and qa_agent_bool and not speech_bool:
            self.agents = [self.text_qa_agent()]
            self.tasks = [self.text_qa_agent_task()]

        return Crew(
            agents= self.agents,
            tasks = self.tasks,
            process = Process.sequential,
            verbose=True,
            max_rpm=8
        )