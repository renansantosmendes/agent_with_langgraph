from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = ChatOpenAI(model='gpt-4o-mini')


def chatbot(state: State) -> dict:
    """
    A function that represents a chatbot, taking a state of type
    State and returning a dictionary with messages after invoking
    the llm model with the state's messages.
    """
    return {'messages': [llm.invoke(state['messages'])]}


graph = StateGraph(State)
graph.add_node(node='chatbot', action=chatbot)
graph.add_edge(start_key=START, end_key="chatbot")
graph.add_edge(start_key="chatbot", end_key=END)
graph = graph.compile(debug=True)
