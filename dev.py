from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode

load_dotenv()

if __name__ == '__main__':
    tool = TavilySearchResults(max_results=4)
    tools = [tool]
    print(tool.invoke('o que é um node no langgraph?'))
