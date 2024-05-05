from dotenv import load_dotenv
load_dotenv()
from crew import TLDRNewsCrew

def run():
    inputs = { 
        'date' : '2024-05-03'
    }
    TLDRNewsCrew().crew().kickoff(inputs=inputs)

if __name__ == "__main__":
    run()    