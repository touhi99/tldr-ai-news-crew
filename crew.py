from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from llms import load_llm
from tools.crawler import crawler_tool
from tools.vectordb import get_news, embed_news
from tools.speech import tts
@CrewBase
class TLDRNewsCrew:
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self) -> None:
        self.local_llm = load_llm('local')
        self.groq_llm = load_llm("groq")
        self.openai_llm = load_llm("openai")

    '''
    @agent
    def news_fetcher_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['data_crawler'],
            llm = self.groq_llm,
            tools = [crawler_tool]
        )
    '''
    @agent
    def data_engineer_agent(self) -> Agent:
        return Agent(
            config = self.agents_config['data_engineer'],
            llm = self.groq_llm,
            tools = [embed_news]
        )
    
    @agent
    def data_analyst_agent(self) -> Agent:
        return Agent(
            config = self.agents_config['data_analyst'],
            llm = self.groq_llm,
            tools = [get_news]
        )
    
    @agent
    def speaker_agent(self) -> Agent:
        return Agent(
            config = self.agents_config['speaker_agent'],
            llm = self.groq_llm,
            tools = [tts]
        )

    # @task
    # def data_crawler_task(self) -> Task:
    #     return Task(
    #         config = self.tasks_config['data_crawler_task'],
    #         agent = self.news_fetcher_agent()
    #     )

    @task
    def data_engineer_task(self) -> Task:
        return Task(
            config = self.tasks_config['data_engineer_task'],
            agent = self.data_engineer_agent()
        )
    
    @task
    def data_analyst_task(self) -> Task:
        return Task(
            config = self.tasks_config['data_analyst_task'],
            agent = self.data_analyst_agent()
        )

    @task
    def speaker_task(self) -> Task:
        return Task(
            config = self.tasks_config['speaker_task'],
            agent = self.speaker_agent()
        ) 
    @crew
    def crew(self) -> Crew:
        "Create the TLDR News Crew"
        return Crew(
            agents= self.agents,
            tasks = self.tasks,
            process = Process.sequential,
            verbose=True,
            max_rpm=8
        )