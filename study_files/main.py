from agent import Agent
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_community.tools.tavily_search import TavilySearchResults


load_dotenv()


if __name__ == '__main__':
    tool = TavilySearchResults(max_results=4)
    model = ChatOpenAI(model="gpt-4o")  # reduce inference cost
    abot = Agent(model=model, tools=[tool])
    messages = [HumanMessage(content="qual a previsão do tempo para belo horizonte?")]
    result = abot.graph.invoke({"messages": messages})
    print(result['messages'][-1].content)
