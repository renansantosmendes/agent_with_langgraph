from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI

from agent_v2 import Agent
from retriever import WebContentVectorRetriever
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(model="gpt-4o-min")
search_engine = TavilySearchResults(max_results=4)
retriever_engine = WebContentVectorRetriever(url='https://docs.smith.langchain.com/overview')

if __name__ == '__main__':
    agent = Agent(search_engine=search_engine,
                  retriever_engine=retriever_engine.get_retriever(),
                  model=model)
    agent.invoke("qual a previsão do tempo para belo horizonte?")