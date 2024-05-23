from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from llms import load_llm
from tools.crawler import crawler_tool
from tools.vectordb import get_news, embed_news
from tools.speech import tts
from tools.qa import get_qa
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
            llm = self.groq_llm,
            tools = [crawler_tool]
        )
    
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
            llm = self.openai_llm,
            tools = [get_news]
        )
    
    @agent
    def speaker_agent(self) -> Agent:
        return Agent(
            config = self.agents_config['speaker_agent'],
            llm = self.groq_llm,
            tools = [tts]
        )
    
    @agent
    def qa_agent(self) -> Agent:
        return Agent(
            config = self.agents_config['news_qa_support_agent'],
            llm = self.openai_llm,
            tools = [get_qa]
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
    
    @task
    def qa_agent_task(self) -> Task:
        return Task(
            config = self.tasks_config['news_qa_support_task'],
            agent = self.qa_agent()
        )

    
    @crew
    def crew(self, speech_agent_bool=False, qa_agent_bool=False) -> Crew:
        "Create the TLDR News Crew"
        if speech_agent_bool and not qa_agent_bool:
            print("HERE")
            self.agents = [self.news_fetcher_agent(), self.data_engineer_agent(), self.data_analyst_agent(), self.speaker_agent()]
            self.tasks = [self.data_crawler_task(), self.data_engineer_task(), self.data_analyst_task(), self.speaker_task()]
        elif not speech_agent_bool and not qa_agent_bool:
            print("THERE")
            self.agents = [self.news_fetcher_agent(), self.data_engineer_agent(), self.data_analyst_agent()]
            self.tasks = [self.data_crawler_task(), self.data_engineer_task(), self.data_analyst_task()]
        elif not speech_agent_bool and qa_agent_bool:
            print("INSIDE QA")
            self.agents = [self.qa_agent()]
            self.tasks = [self.qa_agent_task()]

        return Crew(
            agents= self.agents,
            tasks = self.tasks,
            process = Process.sequential,
            verbose=True,
            max_rpm=8
        )