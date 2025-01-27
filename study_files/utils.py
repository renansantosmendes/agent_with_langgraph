from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from dotenv import load_dotenv

from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]


tool = TavilySearchResults(max_results=2)
tools = [tool]
llm = ChatOpenAI(model='gpt-4o-mini')
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State) -> dict:
    """
    A function that represents a chatbot, taking a state of type
    State and returning a dictionary with messages after invoking
    the llm model with the state's messages.
    """
    return {'messages': [llm_with_tools.invoke(state['messages'])]}


graph = StateGraph(State)
graph.add_node(node='chatbot', action=chatbot)
graph.add_node(node='tools', action=ToolNode(tools=[tool]))
graph.add_conditional_edges('chatbot', tools_condition)
graph.add_edge(start_key='tools', end_key="chatbot")
graph.set_entry_point('chatbot')
graph = graph.compile(debug=True)
