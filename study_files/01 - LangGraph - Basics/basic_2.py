from typing import Annotated

from langgraph.prebuilt import ToolNode, tools_condition
from typing_extensions import TypedDict

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import START, END

from langgraph.graph import StateGraph, add_messages
from langchain_community.tools.tavily_search import TavilySearchResults
import json
from langchain_core.messages import ToolMessage

from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()

load_dotenv()


def main():
    class State(TypedDict):
        messages: Annotated[list, add_messages]

    graph_builder = StateGraph(State)

    llm = ChatOpenAI(model="gpt-4o-mini")
    tool = TavilySearchResults(max_results=3)
    tools = [tool]
    llm_with_tools = llm.bind_tools(tools)

    def chatbot(state: State) -> dict:
        new_message = llm_with_tools.invoke(state['messages'])
        return {'messages': state['messages'] + [new_message]}

    def route_tools(state: State):
        if isinstance(state, list):
            ai_message = state[-1]
        elif messages := state.get('messages', []):
            ai_message = messages[-1]
        else:
            raise ValueError('no messsages found')
        if hasattr(ai_message, 'tool_calls') and len(ai_message.tool_calls) > 0:
            return 'tools'
        return END

    graph_builder.add_edge(start_key=START, end_key="chatbot")
    graph_builder.add_node(node='chatbot', action=chatbot)
    graph_builder.add_edge(start_key="chatbot", end_key=END)

    tool_node = ToolNode(tools=[tool])
    graph_builder.add_node("tools", tool_node)
    graph_builder.add_conditional_edges('chatbot',
                                        tools_condition)
    graph_builder.add_edge(start_key='tools', end_key="chatbot")

    graph = graph_builder.compile(checkpointer=memory)

    def stream_graph_updates(user_input: str):
        config = {"configurable": {"thread_id": "1"}}
        for event in graph.stream({"messages": [("user", user_input)]}, config):
            for value in event.values():
                print("Assistant:", value["messages"][-1].content)

    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)


if __name__ == '__main__':
    print('Hello World!')
    main()
