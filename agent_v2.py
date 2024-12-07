from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.tools.retriever import create_retriever_tool

load_dotenv()


class Agent:
    def __init__(self, search_engine, retriever_engine, model) -> None:
        self.search = search_engine
        self.retriever = create_retriever_tool(retriever=retriever_engine,
                                               name="langsmith_search",
                                               description= "Search for information about LangSmith. For any "
                                                            "questions about LangSmith, you must use this tool!")

        self.llm = model

    def search(self, query):
        return self.search(query)

    def retriever(self, query):
        return self.retriever(query)

    def llm(self, query):
        return self.llm(query)

    def invoke(self, query):
        pass
