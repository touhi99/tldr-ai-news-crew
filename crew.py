from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from llms import load_llm
from tools.crawler import crawler_tool
#from tools.reporter_tool import save_to_json


@CrewBase
class TLDRNewsCrew:
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self) -> None:
        self.local_llm = load_llm('local')
        self.groq_llm = load_llm("groq")

    '''
    @agent
    def news_fetcher_agent(self) -> Agent:
        return Agent(
            config='',
            llm = self.groq_llm,
            tools = [crawler_tool]
        )
    '''

    @agent
    def news_summarizer_agent(self) -> Agent:
        return Agent(
            config = '',
            llm = self.groq_llm,
            tools = []
        )
